from py2neo import Node, Relationship, Graph, NodeSelector, watch
from py2neo.database.status import DatabaseError

from cristin import rest, ws
from threading import Thread
from prwlock import RWLock

import json
import time
import pprint

r_lock = RWLock()
p_lock = RWLock()
i_lock = RWLock()
u_lock = RWLock()

pprint = pprint.PrettyPrinter(indent=4).pprint


class CristinDB():
    def __init__(self, queue, verbose=True, threads=5):
        self.queue = queue
        if verbose:
            self.verbose = lambda x: print(f"[VERBOSE] {x}")
            watch(self.__class__.__name__)
        else:
            self.verbose = lambda x: None

        with open('config.json') as c:
            conf = json.load(c)
            watch("neo4j.http")
            self.__db = Graph(**conf['database'])

        def select(label, prop):
            select = NodeSelector(self.__db).select(label)
            return set(map(lambda x: x[prop], select))

        self.drop_db()
        self.results = select("Result", "id")
        self.persons = select("Person", "cristin_person_id")
        self.instits = select("Institution", "cristin_institution_id")
        self.units = select("Unit", "cristin_unit_id")

        self.threads = {}

        for pid in range(threads):
            name = f"neo4j:{pid}"
            t = Thread(target=self.run, name=name, args=(name,), daemon=True)
            self.threads[name] = t.start()

        self.run(self.__class__.__name__)

    def result_create(self, result):
        # Check if Result exist
        r_lock.acquire_read()
        if result.id in self.results:
            r_lock.release()
            return
        r_lock.release()

        # Add result to the set
        r_lock.acquire_write()
        if result.id in self.results:
            r_lock.release()
            return
        self.results.add(result.id)
        r_lock.release()

        # Compile result node
        result_node = compile_node("Result", result)
        tx = self.__db.begin()
        tx.create(result_node)
        tx.commit()
        self.verbose(result)

        # Add authors and returns them
        for author in result.get_collaborators():
            person_node = self.person_create(author.cristin_person_id)
            tx = self.__db.begin()
            tx.create(Relationship(person_node, "author", result_node))
            tx.commit()


    def person_get(self, cristin_id):
        select = NodeSelector(self.__db).select
        return select("Person", cristin_person_id=cristin_id).first()

    def person_create(self, cristin_id):
        # Check if person exist
        p_lock.acquire_read()
        if cristin_id in self.persons:
            p_lock.release()
            return self.person_get(cristin_id)
        p_lock.release()

        # Fetch person
        person = rest.Person(cristin_id)
        person_node = compile_node("Person", person)

        # Add person
        p_lock.acquire_write()
        if cristin_id in self.persons:
            p_lock.release()
            return self.person_get(cristin_id)

        self.verbose(person)
        tx = self.__db.begin()
        tx.create(person_node)
        tx.commit()
        self.persons.add(cristin_id)

        # Affiliation
        for affiliation in person.affiliations:
            institution_id = affiliation["cristin_institution_id"]
            unit_id = affiliation['cristin_unit_id']

            if "position" in affiliation and affiliation["position"] is not None:
                relation = affiliation["position"]
            else:
                relation = "unknown"

            institution_node = self.institution_create(institution_id)
            unit_node = self.unit_get(unit_id)

            # Save link
            tx = self.__db.begin()
            try:
                tx.create(Relationship(person_node, relation, unit_node))
            except AttributeError:
                print(f"[WARNING] {unit_id}: not found")

            tx.create(Relationship(person_node, relation, institution_node))
            tx.commit()
        p_lock.release()

        return person_node

    def institution_get(self, cristin_id):
        select = NodeSelector(self.__db).select
        return select("Institution", cristin_institution_id=cristin_id).first()

    def institution_create(self, cristin_id):
        # Check if institution exist
        i_lock.acquire_read()
        if cristin_id in self.persons:
            i_lock.release()
            return self.institution_get(cristin_id)
        i_lock.release()

        # Fetch unit and institution
        inst = rest.Institution(cristin_id)
        unit = rest.Unit(inst.cristin_unit_id)
        inst_node = compile_node("Institution", inst)

        # Add institution
        i_lock.acquire_write()
        if cristin_id in self.instits:
            i_lock.release()
            return self.institution_get(cristin_id)

        # Save institution
        self.verbose(inst)
        tx = self.__db.begin()
        tx.create(inst_node)
        tx.commit()
        self.instits.add(cristin_id)

        # institution node
        for subunit in unit.subunits:
            unit_id = subunit["cristin_unit_id"]
            self.unit_create(inst_node, unit_id)

        i_lock.release()
        return inst_node

    def unit_get(self, cristin_id):
        u_lock.acquire_read()
        select = NodeSelector(self.__db).select
        unit = select("Unit", cristin_unit_id=cristin_id).first()
        u_lock.release()
        return select("Unit", cristin_unit_id=cristin_id).first()

    def unit_create(self, parent_node, cristin_id):
        u_lock.acquire_read()
        if cristin_id in self.units:
            u_lock.release()
            return self.unit_get(cristin_id)
        u_lock.release()

        # Fetch unit
        unit = rest.Unit(cristin_id)
        unit_node = compile_node("Unit", unit)

        self.verbose(unit)

        # Save node
        tx = self.__db.begin()
        try:
            tx.create(Relationship(unit_node, "belong", parent_node))
        except DatabaseError:
            print("[ERROR] DATABASE ERROR")
            print(f"[ERROR] {unit}")
            print(f"[ERROR] {unit_node}")
            print(f"[ERROR] {parent_node}")
            raise DatabaseError

        tx.commit()
        self.units.add(cristin_id)

        for subunit in unit.subunits:
            subunit_id = subunit['cristin_unit_id']
            self.unit_create(unit_node, subunit_id)

    def drop_db(self):
        self.__db.delete_all()

    def run(self, name):
        while True:
            print(f"[INFO] Wants to get from queue: {self.queue.qsize()}")
            try:
                pkg = self.queue.get(timeout=10)
            except TimeoutError:
                print(f"[WARNING] Unable to get data from the queue of current size: {self.queue.qsize()}")
            if isinstance(pkg, list):
                for result in pkg:
                    if isinstance(result, ws.Result):
                        self.result_create(result)
                    else:
                        print("[WARNING] {name} exiting")
                        return
            else:
                print("[WARNING] {name} exiting")
                return


def compile_node(label, props):
    p = filter(lambda x: not isinstance(x[1], list), props)
    p = filter(lambda x: not isinstance(x[1], dict), list(p))
    return Node(label, **{x[0]: x[1] for x in list(p)})
