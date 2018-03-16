import requests
from . import ws

class Resource():
    def __init__(self, URL, data):
        if isinstance(data, int) or isinstance(data, str):
            res = requests.get(f"{self.URL}/{data}")
            if res.status_code == 200:
                self.__attributes = res.json()
            else:
                raise LookupError(f"Requesting {self.URL}/{data} returned {res.status_code}: {res.reason}")

        elif isinstance(data, dict):
            self.__attributes = data
        else:
            raise TypeError

    def get_property(self, prop_name):
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
    def attributes(self):
        return self.__attributes

    def __getitem__(self, prop_name):
        return self.get_property(prop_name)

    def __iter__(self):
        self.__start = 0
        return self

    def __next__(self):
        self.__start += 1
        if self.__start > len(self):
            raise StopIteration

        return list(self.attributes.items())[self.__start - 1]

    def __len__(self):
        return len(self.__attributes)



class Unit(Resource):
    """

    doc comes lates
    """
    URL = 'https://api.cristin.no/v2/units'

    def __init__(self, data):
        Resource.__init__(self, self.URL, data)

    def __str__(self):
        name = list(self.unit_name.values())[0]
        return f"ID {self.cristin_unit_id}: {name}"

    @property
    def cristin_unit_id(self):
        """
        Returns:
            type: string
        """
        return self.get_property('cristin_unit_id')

    @property
    def unit_name(self):
        """
        Returns:
            type: dict
        """
        return self.get_property('unit_name')

    @property
    def institution(self):
        """
        Returns:
            type: dict
        """
        return self.get_property('institution')

    @property
    def parent_unit(self):
        """
        Returns:
            type: dict
        """
        return self.get_property('parent_unit')

    @property
    def subunits(self):
        """
        Returns:
            type: list
        """
        return self.get_property('subunits')


class Institution(Resource):
    """

    doc comes lates
    """
    URL = 'https://api.cristin.no/v2/institutions'

    def __init__(self, data):
        Resource.__init__(self, self.URL, data)

    def __str__(self):
        name = list(self.institution_name.values())[0]
        return f"ID {self.cristin_institution_id}: {name}"

    @property
    def cristin_institution_id(self):
        """
        Returns:
            type: string
        """
        return self.get_property('cristin_institution_id')

    @property
    def acronym(self):
        """
        Returns:
            type: string
        """
        return self.get_property('acronym')

    @property
    def institution_name(self):
        """
        Returns
            type: string
        """
        return self.get_property('institution_name')

    @property
    def country(self):
        """
        Returns:
            type: string
        """
        return self.get_property('country')

    @property
    def cristin_user_institution(self):
        """
        Returns:
            type: boolean
        """
        return self.get_property('cristin_user_institution')

    @property
    def corresponding_unit(self):
        """
        Returns:
            type: dict
        """
        return self.get_property('corresponding_unit')


class Person(Resource):
    """ Class desgined after cristins person JSON schema.

    doc comes later
    """
    URL = "https://api.cristin.no/v2/persons"

    def __init__(self, data):
        Resource.__init__(self, self.URL, data)

    def __str__(self):
        return f"ID {self.cristin_person_id}: {self.surname},{self.firstname}"

    def get_results(self, session=None):
        return ws.get_results_by_person_id(self.cristin_person_id, session)

    @property
    def cristin_person_id(self):
        """
        Note:
            Required field in the person JSON schema

        Returns:
            type: string
        """
        return self.get_property('cristin_person_id')

    @property
    def firstname(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.get_property('firstname')

    @property
    def surname(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.get_property('surname')

    @property
    def private_email(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.get_property('private_email')

    @property
    def tel(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.get_property('tel')

    @property
    def identified_cristin_person(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: boolean
        """
        return self.get_property('identified_cristin_person')

    @property
    def date_of_birth(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.get_property('date_of_birth')

    @property
    def picture_url(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.get_property('picture_url')

    @property
    def cristin_profile_url(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.get_property('cristin_profile_url')

    @property
    def affiliations(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: list
        """
        return self.get_property('affiliations')
