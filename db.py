from py2neo import Node, Relationship, Graph, NodeSelector
from cristin import rest
import json

import pprint
pp = pprint.PrettyPrinter(indent=4)

class DB:
    def __init__(self, queue):
        self.__queue = queue
        with open('config.json') as c:
            conf = json.load(c)
            self.__db = Graph(**conf['database'])

    def add_result(self, result):
        pass

    def add_person(self, person):
        # Check if person exist
        if person_exist(person['cristin_person_id']):
            return

        # Create person node
        person_node = person_create(person)
        print(person_node)

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

    def _add_institution(self, institution):
        # Creating a institution node
        institution_node = create_institution_node(institution)

        # Fetching a unit object with institution_id, because we need the institution subunits
        unit = rest.Unit(institution['corresponding_unit'])
        for subunit in unit.subunits:
            subunit_id = subunit['cristin_unit_id']
            if not unit_exist(subunit_id):
                self._add_subunit(institution_node, rest.Unit(subunit_id))

    def _add_subunit(self, parent, subunit):
        # Creating a institution node
        unit_node = unit_create(subunit)

        # Create relationship from subunit -> parent
        tx = self.__db.begin()
        tx.create(Relationship(unit_node, 'BELONGS_TO', parent))
        tx.commit()

        # Traversing through n subunits
        for subunit in unit.subunits:
            subunit_id = subunit['cristin_unit_id']
            if not unit_exist(subunit_id):
                self._add_subunit(unit_node, rest.Unit(subunit_id))

    def drop_db(self):
        self.__db.delete_all()

    def run(self):
        while True:
            pkg = self.__queue.get()
            if isinstance(pkg, rest.Person):
                self.add_person(pkg)
            else:
                self.add_result(pkg)

def person_create(person):
    p = filter(lambda x : not isinstance(x[1], list), person)
    return Node('Person', **{x[0] : x[1] for x in list(p)})

def person_exist(person_id):
    return False

def institution_create(institution):
    if isinstance(institution, rest.Institution):
        i = map(lambda x: (x[0], list(x[1].values())[0]) if isinstance(x[1], dict) else x, institution)
        return Node('Institution', **{x[0] : x[1] for x in list(i)})
    else:
        raise TypeError("Argument is not of type Institution")

def institution_exist(institution_id):
    return False

def unit_create(unit):
    if isinstance(unit, rest.Unit):
        u = {'cristin_unit_id': unit.cristin_unit_id,
        'unit_name': unit.unit_name,
        'institution': unit.institution}
        return Node('Unit', **u)
    else:
        raise TypeError("Argument is not of type Unit")

def unit_exist(unit_id):
    return False
