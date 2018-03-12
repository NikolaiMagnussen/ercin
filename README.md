# ERCIN: Exploring Research Connectivity In Norway

## Ideas:
- Crawl CRISTIN for authors and scientific publications
- Insert authors and publications into a Neo4j database
- Use Neo4j database to visualize and gain knowledge regarding research connectivity in Norway
- Write paper based on the extracted knowledge

## Methods:
- Crawl CRISTIN using Python3, [Requests](http://requests.readthedocs.io/en/master/) and [Neo4j](https://neo4j.com/developer/python/).
- Create Python modules for the CRISTIN API's. One for [Web Services](http://www.cristin.no/ressurser/dokumentasjon/web-service/) and another for [REST API](https://api.cristin.no/v2/doc/index.html).
- Use Web Services module for extracting scientific publications authored by a person.
- Use REST API module for extracting information about a person and which institution they belong to.

## Problems Encountered:
- Each Web Service API call seem to be rate-limited to 1MB/s.

## Authors:
- Andreas Isnes Nilsen
- Nikolai Åsen Magnussen
