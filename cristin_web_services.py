import requests


class Cristin_WS():
    URL = "https://cristin.no/ws/"

    def __init__(self):
        pass

    def get_scientific_results(self, person_id):
        assert(isinstance(person_id, int))
        res = requests.get(f"{self.URL}hentVarbeiderPerson"
                           f"?lopenr={person_id}&format=json")
        if res.status_code != 200:
            return []
        results = [x['fellesdata'] for x in res.json()['forskningsresultat']]
        return results

    def get_scientific_collaborators(self, results):
        assert(isinstance(results, list))
        if len(results) == 0:
            return []

        # Extract titles
        results_titles = [res['tittel'] for res in results]

        # Extract lists of authors
        results_persons = [res['person'] for res in results]
        # Single author means only a dict, convert to single-element list
        results_persons = map(lambda p: [p] if isinstance(p, dict) else p,
                              results_persons)

        # Extract the data we want from each author
        results_persons = [[{'id': p['id'],
                             'fornavn': p['fornavn'],
                             'etternavn': p['etternavn']} for p in persons]
                           for persons in results_persons]

        # Combine titles with their corresponding authors
        return list(zip(results_titles, results_persons))
