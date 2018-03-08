import requests
import rest


def get_results_by_person_id(person_id):
    """
    Query Cristin Web Service API for scientific results by a person.

    Parameters:
        person_id: Int - Integer specifying the ID of the person to query.

    Returns:
        List[Result] associated with the person queried for, and
                     if no person was found, an empty list is returned.
    """
    res = requests.get(f"https://cristin.no/ws/hentVarbeiderPerson"
                       f"?lopenr={person_id}&format=json")
    if res.status_code != 200:
        return []

    return [Result(x['fellesdata']) for x in res.json()['forskningsresultat']]


class Result():
    """ Class designed after the result type in Cristin Web Service API.
    Doc: http://www.cristin.no/teknisk/xsd/resultater/1.0/resultater.xsd

    Proper documentation comes later.
    """
    def __init__(self, kwargs_dict):
        self.__attributes = kwargs_dict

    def __str__(self):
        return f"{self.ar}: {self.tittel}"

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

        return [rest.Person(person['id']) for person in authors]

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


if __name__ == "__main__":
    start = 1
    end = 50
    for i in range(start, end):
        results = get_results_by_person_id(i)
        for i in results:
            print(f"\n{i.tittel} is made by:")
            if isinstance(i.person, dict):
                person = rest.Person(i.person['id'])
                print(f"\t{person.surname} has id {person.cristin_person_id}")
            else:
                for p in i.person:
                    person = rest.Person(p['id'])
                    print(f"\t{person.surname} has id"
                          f"{person.cristin_person_id}")
