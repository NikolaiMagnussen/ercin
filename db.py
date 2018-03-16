from py2neo import Node, Relationship, Graph, NodeSelector
from cristin import rest
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

    def person_create(self, person, recursive=True):

        # Check if person exist
        if self.person_exist(cristin_person_id=dag_id):
            self.__verbose(f"{person} exist -> return")

        # Create person node
        person_node = person_compile_node(person)

        # Iterate through affiliations
        for a in person.affiliations:
            institution_id = a['institution']['cristin_institution_id']
            unit_id        = a['unit']['cristin_unit_id']
            position       = list(a['position'].values())[0]

            if len(position):
                position = 'unkown'

            if not institution_exist(institution_id):
                self._add_institution(rest.Institution(institution_id))

            # Fetch institution record and unit record
            institution_node = institution_fetch(institution_id)
            unit_node        = unit_fetch(unit_id)

            # Creates relationship
            person_node = Relationship(person_node, position, institution_node)
            person_node = Relationship(person_node, position, unit_node)

        tx = self.__db.begin()
        tx.create(person_node)
        tx.commit()

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


    def institution_create(self, institution, recursive=False):
        # Creating a institution node
        institution_node = institution_compile_node(institution)

        # Fetching a unit object with institution_id, because we need the institution subunits
        unit = rest.Unit(institution['corresponding_unit']['cristin_unit_id'])

        for subunit in unit.subunits:
            subunit_id = subunit['cristin_unit_id']

            if self.__verbose:
                print(f"{i}/{len(unit.subunits)} -> {subunit['unit_name']}")

            if not self.unit_exist(subunit_id):
                self._add_subunit(institution_node, rest.Unit(subunit_id))

        if self.__verbose:
            print(f"The institution {institution.institution_name} has been added")

    def institution_read(self, **kwarg):
        return False

    def institution_update(self):
        pass

    def institution_delete(self, **kwarg):
        pass

    def institution_exist(self, **kwarg):
        return True if len(self.institution_read(**kwarg)) else False



    def unit_create(self, unit, recursive=False):
        # Creating a institution node
        unit_node = unit_create(unit)

        # Create relationship from subunit -> parent
        tx = self.__db.begin()
        tx.create(Relationship(unit_node, 'BELONGS_TO', parent))
        tx.commit()

        # Traversing through n subunits
        for subunit in unit.subunits:
            subunit_id = subunit['cristin_unit_id']
            if not unit_exist(subunit_id):
                self._add_subunit(unit_node, rest.Unit(subunit_id))

    def unit_read(self, **kwarg):
        pass

    def unit_update(self):
        pass

    def unit_delete(self, **kwarg):
        pass

    def unit_exist(self, **kwarg):
        pass



    def drop_db(self):
        self.__db.delete_all()

    def run(self):
        while True:
            pkg = self.__queue.get()
            if isinstance(pkg, rest.Person):
                self.person_create(pkg)


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
        u = {'cristin_unit_id': unit.cristin_unit_id,
        'unit_name': list(unit.unit_name.values())[0],
        'institution': list(unit.institution.values())[0]}
        return Node('Unit', **u)

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
