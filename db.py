from py2neo import Node, Relationship, Graph, NodeSelector
from cristin import rest, ws
import json

import pprint
pprint = pprint.PrettyPrinter(indent=4).pprint


class CRUD_neo4j:
    def __init__(self, queue, verbose=True):
        self.__queue = queue
        self.__verbose = lambda x : print(x) if verbose else lambda x: None

        with open('config.json') as c:
            conf = json.load(c)
            self.__db = Graph(**conf['database'])

    def result_create(self, result):
        if self.result_exist(id=result.id):
            self.__verbose(f"[EXIST][RESULT]:{result}")
            return


        authors = result.get_collaborators()
        authors_nodes = []
        for a in authors:
            if not self.person_exist(cristin_person_id=a.cristin_person_id):
                self.person_create(rest.Person(a.cristin_person_id))
            authors_nodes.append(self.person_read(cristin_person_id=a.cristin_person_id))

        result_node = compile_node('Result', result)
        tx = self.__db.begin()
        tx.create(result_node)
        tx.commit()

        for a in authors_nodes:
            tx = self.__db.begin()
            tx.create(Relationship(a, 'author', result_node))
            tx.commit()

    def result_read(self, **kwarg):
        selector = NodeSelector(self.__db)
        selected = selector.select("Result", **kwarg).first()
        return selected

    def result_update(self):
        pass

    def result_delete(self, **kwarg):
        pass

    def result_exist(self, **kwarg):
        return True if self.result_read(**kwarg) else False


    def person_create(self, person):
        # Check if person exist
        if self.person_exist(cristin_person_id=person.cristin_person_id):
            self.__verbose(f"[EXIST][PERSON]:{person}")
            return

        # Create person node
        person_node = compile_node("Person", person)

        # Iterate through affiliations
        for affiliation in person.affiliations:
            inst_id = affiliation['cristin_institution_id']
            unit_id = affiliation['cristin_unit_id']

            if not self.institution_exist(cristin_institution_id=inst_id):
                self.institution_create(rest.Institution(inst_id))

            def transaction(node):
                tx = self.__db.begin()
                relation = 'unkown'
                try:
                    relation = affiliation['position']
                except KeyError:
                    pass

                tx.create(Relationship(person_node, relation, node))
                tx.commit()

            # Fetch institution record and unit record
            try:
                transaction(self.institution_read(cristin_institution_id=inst_id)[0])
            except IndexError:
                raise IndexError(f"cristin_institution_id: {inst_id} don't exist")
            try:
                transaction(self.unit_read(cristin_unit_id=unit_id)[0])
            except IndexError:
                try:
                    transaction(self.institution_read(cristin_unit_id=unit_id)[0])
                except IndexError:
                    pass

        tx = self.__db.begin()
        tx.create(person_node)
        tx.commit()
            # Create relationships
        self.__verbose(f"[CREATE][PERSON]:{person}")

    def person_read(self, **kwarg):
        selector = NodeSelector(self.__db)
        selected = selector.select("Person", **kwarg)
        return selected.first()

    def person_update(self):
        pass

    def person_delete(self, **kwarg):
        pass

    def person_exist(self, **kwarg):
        return True if self.person_read(**kwarg) else False


    def institution_create(self, institution):
        # Check if institution exist
        if self.institution_exist(cristin_institution_id=institution.cristin_institution_id):
            self.__verbose(f"[EXIST][INSTITUTION]:{institution}")
            return

        # Creating a institution node
        institution_node = compile_node("Institution", institution)

        # Fetching a unit object with institution_id, because we need the institution subunits
        tx = self.__db.begin()
        tx.create(institution_node)
        tx.commit()
        self.__verbose(f"[CREATE][INSTITUTION]:{institution}")

        unit = rest.Unit(institution['cristin_unit_id'])

        for subunit in unit.subunits:
            s = rest.Unit(subunit['cristin_unit_id'])
            if not self.unit_exist(cristin_unit_id=s.cristin_unit_id):
                self.__verbose(f"[CREATE][UNIT]:{s}")
                self.unit_create(institution_node, rest.Unit(s.cristin_unit_id))

    def institution_read(self, **kwarg):
        selector = NodeSelector(self.__db)
        selected = selector.select("Institution", **kwarg)
        return list(selected)

    def institution_update(self):
        pass

    def institution_delete(self, **kwarg):
        pass

    def institution_exist(self, **kwarg):
        return True if len(self.institution_read(**kwarg)) else False


    def unit_create(self, parent, unit):
        # Check if institution exist
        if self.unit_exist(cristin_unit_id=unit.cristin_unit_id):
            self.__verbose(f"[EXIST][UNIT]:{unit}")
            return

        # Creating a institution node
        unit_node = compile_node("Unit", unit)

        # Create relationship from subunit -> parent
        tx = self.__db.begin()
        tx.create(Relationship(unit_node, 'BELONGS_TO', parent))
        tx.commit()

        # Traversing through n subunits
        for subunit in unit.subunits:
            s = rest.Unit(subunit['cristin_unit_id'])
            if not self.unit_exist(cristin_unit_id=s.cristin_unit_id):
                self.__verbose(f"[CREATE][UNIT]:{s}")
                self.unit_create(unit_node, rest.Unit(s.cristin_unit_id))

    def unit_read(self, **kwarg):
        selector = NodeSelector(self.__db)
        selected = selector.select("Unit", **kwarg)
        return list(selected)

    def unit_update(self):
        pass

    def unit_delete(self, **kwarg):
        pass

    def unit_exist(self, **kwarg):
        return True if len(self.unit_read(**kwarg)) else False


    def drop_db(self):
        self.__db.delete_all()

    def run(self):
        self.drop_db()
        while True:
            pkg = self.__queue.get()
            if isinstance(pkg, list):
                self.result_create(pkg[0])

def compile_node(label, properties):
    prop = filter(lambda x: not isinstance(x[1], list) and not isinstance(x[1], dict), properties)
    return Node(label, **{x[0]:x[1] for x in list(prop)})
