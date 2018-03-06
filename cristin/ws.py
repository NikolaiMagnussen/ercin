import requests

def get_results_by_person_id(lopenr):
    res = requests.get(f"https://cristin.no/ws/hentVarbeiderPerson"
                       f"?lopenr={person_id}&format=json")
    if res.status_code != 200:
        return []

    return [x['fellesdata'] for x in res.json()['forskningsresultat']]


class Result():
    def __init__(self, **kwargs):
        self.__attributes = kwargs

    def get_collaborators(self):
        authors = self.person


    @property
    def id(self):
        return self.__attributes['id']

    @property
    def eier(self):
        return self.__attributes['eier']

    @property
    def registrert(self):
        return self.__attributes['registrert']

    @property
    def endret(self):
        return self.__attributes['endret']

    @property
    def kategori(self):
        return self.__attributes['kategori']

    @property
    def person(self):
        return self.__attributes['person']

    @property
    def sprak(self):
        return self.__attributes['sprak']

    @property
    def tittel(self):
        return self.__attributes['tittel']

    @property
    def ar(self):
        return self.__attributes['ar']

    @property
    def erPublisert(self):
        return self.__attributes['erPublisert']
