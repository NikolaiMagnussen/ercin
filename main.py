#!/usr/bin/env python
import requests
import json
import pprint

def main():
    cristin_v1 = "https://cristin.no"
    lopenr = "1"
    
    r = requests.get(f"{cristin_v1}/ws/hentVarbeiderPerson?lopenr={lopenr}&format=json")
    data = json.loads(r.text)
    shits = data['forskningsresultat'][0]['fellesdata']
    print(f"Forskningsresultat is of type {type(shits)} has keys {shits.keys()}")

if __name__ == "__main__":
    main()
