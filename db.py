from py2neo import Node, Relationship, Graph, NodeSelector
from cristin import rest, ws
import json

import pprint
pp = pprint.PrettyPrinter(indent=4)

dag_id="58877"

class CRUD_neo4j:
    def __init__(self, queue, verbose=True):
        self.__queue = queue
        self.__verbose = lambda x : print(x) if verbose else lambda x: None

        with open('config.json') as c:
            conf = json.load(c)
            self.__db = Graph(**conf['database'])

    def result_create(self, result, recursive=True):
        authors = result.get_collaborators()
        pp.pprint(result.tittel)
        for a in authors:
            # Because of light persons
            self.person_create(rest.Person(a.cristin_person_id))

        #pp.pprint(result.eier)
        #pp.pprint(result.id)
        #pp.pprint(result.kategori)
        #pp.pprint(result.person)

    def result_read(self, **kwarg):
        # Do something!
        r = result_compile_node()

    def result_update(self):
        pass

    def result_delete(self, **kwarg):
        pass

    def result_exist(self, **kwarg):
        return True if len(self.result_read(**kwarg)) else False


    def person_create(self, person, recursive=True):
        # Check if person exist
        if self.person_exist(cristin_person_id=person.cristin_person_id):
            self.__verbose(f"[EXIST]: {person}")
            return

        # Create person node
        person_node = person_compile_node(person)

        # Iterate through affiliations
        for a in reversed(person.affiliations):
            institution_id = a['institution']['cristin_institution_id']
            unit_id = a['unit']['cristin_unit_id']

            relation_prop  = {'active': get_prop(a, 'active'), 'email': get_prop(a, 'email')}
            relation = get_prop(a, 'position')

            relation = 'unkown' if relation == '' else list(relation.values())[0]

            if recursive and not self.institution_exist(cristin_institution_id=institution_id):
                self.institution_create(rest.Institution(institution_id))

            def transaction(node):
                try:
                    print(node)
                    node = node[0]
                    tx = self.__db.begin()
                    tx.create(Relationship(person_node, relation, node, **relation_prop))
                    tx.commit()
                except IndexError:
                    raise IndexError(f"couldn't find associated institution for {person} : {unit_id} : {institution_id}")

            # Fetch institution record and unit record
            transaction(self.institution_read(cristin_institution_id=institution_id))
            transaction(self.unit_read(cristin_unit_id=unit_id))


            # Create relationships
        self.__verbose(f"[CREATED] {person}")

    def person_read(self, **kwarg):
        p = person_compile_node(rest.Person(kwarg))
        selector = NodeSelector(self.__db)
        selected = selector.select("Person", **dict(p))
        return list(selected)

    def person_update(self):
        pass

    def person_delete(self, **kwarg):
        pass

    def person_exist(self, **kwarg):
        return True if len(self.person_read(**kwarg)) else False


    def institution_create(self, institution, recursive=True):
        # Check if institution exist
        if self.institution_exist(**institution.attributes):
            self.__verbose(f"[EXIST ] {institution}")
            return

        # Creating a institution node
        institution_node = institution_compile_node(institution)
        pp.pprint(institution_node)

        if not recursive:
            tx = self.__db.begin()
            tx.create(institution_node)
            tx.commit()
            return

        # Fetching a unit object with institution_id, because we need the institution subunits
        unit = rest.Unit(institution['corresponding_unit']['cristin_unit_id'])
        self.__verbose(f"[CREATE] {unit}")

        for subunit in unit.subunits:
            s = rest.Unit(subunit['cristin_unit_id'])
            if not self.unit_exist(cristin_unit_id=s.cristin_unit_id):
                self.__verbose(f"[CREATE] {s}")
                self.unit_create(institution_node, rest.Unit(s.cristin_unit_id))

    def institution_read(self, **kwarg):
        i = institution_compile_node(rest.Institution(kwarg))
        selector = NodeSelector(self.__db)
        selected = selector.select("Institution", **dict(i))
        return list(selected)

    def institution_update(self):
        pass

    def institution_delete(self, **kwarg):
        pass

    def institution_exist(self, **kwarg):
        return True if len(self.institution_read(**kwarg)) else False


    def unit_create(self, parent, unit, recursive=True):
        # Check if institution exist
        if self.unit_exist(**unit.attributes):
            self.__verbose(f"[EXIST ] {unit}")
            return

        # Creating a institution node
        unit_node = unit_compile_node(unit)

        # Create relationship from subunit -> parent
        tx = self.__db.begin()
        tx.create(Relationship(unit_node, 'BELONGS_TO', parent))
        tx.commit()

        if not recursive:
            return

        # Traversing through n subunits
        for subunit in unit.subunits:
            s = rest.Unit(subunit)
            if not self.unit_exist(cristin_unit_id=s.cristin_unit_id):
                self.__verbose(f"[CREATE] {s}")
                self.unit_create(unit_node, rest.Unit(s.cristin_unit_id))

    def unit_read(self, **kwarg):
        u = unit_compile_node(rest.Unit(kwarg))
        selector = NodeSelector(self.__db)
        selected = selector.select("Unit", **dict(u))
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
            if isinstance(pkg, rest.Person):
                self.person_create(pkg)
            elif isinstance(pkg, ws.Result):
                self.result_create(pkg)


def person_compile_node(person):
    if isinstance(person, rest.Person):
        p = filter(lambda x : not isinstance(x[1], list), person)
        return Node('Person', **{x[0] : x[1] for x in list(p)})

    elif isinstance(person, Node):
        return person

    else:
        raise TypeError("Argument is not of type cristin.rest.Person")

def unit_compile_node(unit):
    if isinstance(unit, rest.Unit):
        u = map(lambda x: (x[0], list(x[1].values())[0]) if isinstance(x[1], dict) else x, unit)
        u = filter(lambda x : not isinstance(x[1], list), list(u))
        return Node('Unit', **{x[0] : x[1] for x in list(u)})

    elif isinstance(unit, Node):
        return unit

    else:
        raise TypeError("Argument is not of type cristin.rest.Unit")

def institution_compile_node(institution):
    if isinstance(institution, rest.Institution):
        i = map(lambda x: (x[0], list(x[1].values())[0]) if isinstance(x[1], dict) else x, institution)
        return Node('Institution', **{x[0] : x[1] for x in list(i)})

    elif isinstance(institution, Node):
        return institution

    else:
        raise TypeError("Argument is not of type cristin.rest.Institution")

def result_compile_node(result):
    pass

def get_prop(key, val):
    try:
        return key[val]
    except KeyError:
        return ''
