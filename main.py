from py2neo import Node, Relationship, Graph
from cristin import rest
import requests

import pprint
pp = pprint.PrettyPrinter(indent=4)


dag_id = 58877



class Test:
    URI = "localhost"
    def __init__(self):
        self.__db = Graph(self.URI, password='kakedeig')

    def add_person(self, person):
        for a in person.affiliations:
            print(a['institution'])


    def add_institution(self, institution):
        pass

    def add_unit(self, unit):
        pass

t = Test()
t.add_person(rest.Person(dag_id))
