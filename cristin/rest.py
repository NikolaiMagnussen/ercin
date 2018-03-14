import requests
from . import ws


class Resource():
    def __init__(self, URL, data):
        if isinstance(data, dict):
            self.__attributes = data

        res = requests.get(f"{URL}/{data}")
        if res.status_code == 200:
            self.__attributes = res.json()
        else:
            raise LookupError

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


class Unit(Resource):
    """

    doc comes lates
    """
    URL='https://api.cristin.no/v2/units'

    def __init__(self, data):
        Resource.__init__(self, self.URL, data)

class Institution(Resource):
    """

    doc comes lates
    """
    URL='https://api.cristin.no/v2/institutions'

    def __init__(self, data):
        Resource.__init__(self, self.URL, data)

    def __str__(self):
        return f"ID {self.cristin_institution_id}: {self.institution_name}"

    @property
    def cristin_institution_id(self):
        return self.get_property('cristin_institution_id')

    @property
    def acronym(self):
        return self.get_property('acronym')

    @property
    def institution_name(self):
        return self.get_property('institution_name')

    @property
    def country(self):
        return self.get_property('country')

    @property
    def cristin_user_institution(self):
        return self.get_property('cristin_user_institution')

    @property
    def corresponding_unit(self):
        return self.get_property('corresponding_unit')


class Person():
    """ Class desgined after cristins person JSON schema.

    doc comes later
    """
    URL = "https://api.cristin.no/v2/persons"

    def __init__(self, data):
        if isinstance(data, int) or isinstance(data, str):
            res = requests.get(f"{self.URL}/{data}")
            if res.status_code == 200:
                self.__attributes = res.json()
            else:
                raise LookupError
        elif isinstance(data, dict):
            self.__attributes = data
        else:
            raise TypeError

    def __str__(self):
        return f"ID {self.cristin_person_id}: {self.surname},{self.firstname}"

    def get_results(self, session=None):
        return ws.get_results_by_person_id(self.cristin_person_id, session)

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
    def attributes(self):
        return self.__attributes

    @property
    def cristin_person_id(self):
        """
        Note:
            Required field in the person JSON schema

        Returns:
            type: string
        """
        return self.__get_property('cristin_person_id')

    @property
    def firstname(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.__get_property('firstname')

    @property
    def surname(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.__get_property('surname')

    @property
    def private_email(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.__get_property('private_email')

    @property
    def tel(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.__get_property('tel')

    @property
    def identified_cristin_person(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: boolean
        """
        return self.__get_property('identified_cristin_person')

    @property
    def date_of_birth(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.__get_property('date_of_birth')

    @property
    def picture_url(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.__get_property('picture_url')

    @property
    def cristin_profile_url(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        return self.__get_property('cristin_profile_url')

    @property
    def affiliations(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: list
        """
        return self.__get_property('affiliations')
