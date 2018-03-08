#!/usr/bin/env python
import requests
import json
import cws
from cristin import ws
from cristin import rest

def query_collaborators():
    dag = rest.Person(58877)
    dag_results = dag.get_results()
    dag_collaborators = []
    for res in dag_results:
        for collab in res.get_collaborators():
            print(collab)


if __name__ == "__main__":
    query_collaborators()
