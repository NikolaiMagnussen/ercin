#!/usr/bin/env python
import requests
import json
import pprint
import cws
import cristin

pp = pprint.PrettyPrinter()


def main():
    cristin_v1 = "https://cristin.no"
    lopenr = "1"

    r = requests.get(
            f"{cristin_v1}/ws/hentVarbeiderPerson?lopenr={lopenr}&format=json")
    data = json.loads(r.text)
    shits = data['forskningsresultat'][0]['fellesdata']
    print(f"Shit is of type {type(shits)} has keys {shits.keys()}")
    pp.pprint(shits)


def query_collaborators():
    dag = 58877
    ws = cws.Cristin_WS()
    results = ws.get_scientific_results(dag)
    collaborators = ws.get_scientific_collaborators(results)
    print(f"Got back {len(collaborators)} results for Dag!")
    for i in range(1000):
        results = ws.get_scientific_results(i)
        collaborators = ws.get_scientific_collaborators(results)
        print(f"Got back {len(collaborators)} results for id: {i}")


if __name__ == "__main__":
    #query_collaborators()
    cristin.rest.kake()
    cristin.ws.kake()
