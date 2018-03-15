import requests
from . import rest


def get_results_by_person_id(person_id, session=None):
    """
    Query Cristin Web Service API for scientific results by a person.

    Parameters:
        person_id: Int - Integer specifying the ID of the person to query.

    Returns:
        List[Result] associated with the person queried for, and
                     if no person was found, an empty list is returned.
    """
    if session is not None:
        def extract_results(sess, resp):
            if resp.status_code == 200:
                json_data = resp.json()['forskningsresultat']
                resp.data = [Result(x['fellesdata']) for x in json_data]
            else:
                resp.data = []

        return session.get(f"https://api.cristin.no/ws/hentVarbeiderPerson"
                           f"?lopenr={person_id}&format=json",
                           background_callback=extract_results)
    else:
        resp = requests.get(f"https://api.cristin.no/ws/hentVarbeiderPerson"
                            f"?lopenr={person_id}&format=json")

        if resp.status_code != 200:
            return []

        json_data = resp.json()['forskningsresultat']
        return [Result(x['fellesdata']) for x in json_data]


class Result():
    """ Class designed after the result type in Cristin Web Service API.
    Doc: http://www.cristin.no/teknisk/xsd/resultater/1.0/resultater.xsd

    Proper documentation comes later.
    """
    def __init__(self, kwargs_dict):
        self.__attributes = kwargs_dict

    def __str__(self):
        return f"{self.ar}: {self.tittel}"

    def __get_property(self, prop_name):
        """
        Extract the value of a property from the Result data.

        Parameters:
            prop_name: str - denoting the name of the field to extract from.

        Returns:
            String with the value of the property, if it exist.
            If it does not exist, an empty string will be returned.
        """
        try:
            return self.__attributes[prop_name]
        except KeyError:
            return ''

    def get_collaborators(self):
        """
        Get a list of collaborators that worked on the Result.

        Parameters:
            None

        Returns:
            List[Person] where some parts of the Person will be provided,
                         but not all. At least id, firstname and suname
                         will be present.
        """
        authors = self.person
        if isinstance(authors, dict):
            authors = [authors]

        def person_lite(p):
            return {"cristin_person_id": p["id"],
                    "firstname": p["fornavn"],
                    "surname": p["etternavn"]}
        return [rest.Person(person_lite(person)) for person in authors]

    @property
    def id(self):
        """
        Note:
            (Hopefully) required field in the Result

            Returns:
                String
        """
        return self.__get_property('id')

    @property
    def eier(self):
        """
        Note:
            (Hopefully) required field in the Result

            Returns:
                String
        """
        return self.__get_property('eier')

    @property
    def registrert(self):
        """
        Note:
            (Hopefully) required field in the Result

            Returns:
                String
        """
        return self.__get_property('registrert')

    @property
    def endret(self):
        """
        Note:
            (Hopefully) required field in the Result

            Returns:
                String
        """
        return self.__get_property('endret')

    @property
    def kategori(self):
        """
        Note:
            (Hopefully) required field in the Result

            Returns:
                String
        """
        return self.__get_property('kategori')

    @property
    def person(self):
        """
        Note:
            (Hopefully) required field in the Result

            Returns:
                String
        """
        return self.__get_property('person')

    @property
    def sprak(self):
        """
        Note:
            (Hopefully) required field in the Result

            Returns:
                String
        """
        return self.__get_property('sprak')

    @property
    def tittel(self):
        """
        Note:
            (Hopefully) required field in the Result

            Returns:
                String
        """
        return self.__get_property('tittel')

    @property
    def ar(self):
        """
        Note:
            (Hopefully) required field in the Result

            Returns:
                String
        """
        return self.__get_property('ar')

    @property
    def erPublisert(self):
        """
        Note:
            (Hopefully) required field in the Result

            Returns:
                String
        """
        return self.__get_property('erPublisert')
