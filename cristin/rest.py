import requests
from jsonschema import validate
from . import ws
import pprint
pprint = pprint.PrettyPrinter(indent=4).pprint


DEFAULT_LANG='en'
schemas = {}



def del_lang_tag(blob, prop, lang):
    try:
        blob[prop] = blob[prop][lang]
    except KeyError:
        try:
            blob[prop] = list(blob[prop].values())[0]
        except KeyError:
            pass

class APIResource():
    def __init__(self, data, lang):
        name = self.__class__.__name__
        if not name in schemas:
            res = requests.get(f"{self.schema}?lang={lang}")
            if res.status_code != 200:
                raise LookupError("[{res.status_code}:{res.reason}] couldn't fetch {name} json schema")

            schemas[name] = res.json()

        if isinstance(data, int) or isinstance(data, str):
            res = requests.get(f"{self.URL}/{data}?lang={lang}")
            if res.status_code == 200:
                self.__attributes = res.json()
            else:
                raise LookupError(f"[{res.status_code}:{res.reason}] {self.URL}/{data}")

        elif isinstance(data, dict):
            self.__attributes = data
        else:
            raise TypeError

        #validate(self.attributes, schemas[name])

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


class Unit(APIResource):
    """

    doc comes lates
    """
    URL = 'https://api.cristin.no/v2/units'
    schema = 'http://api.cristin.no/v2/doc/json-schemas/units_GET_response.json'

    def __init__(self, data, lang=DEFAULT_LANG):
        APIResource.__init__(self, data, lang)

        if isinstance(self.institution, str):
            pprint(self.attributes)
        self.attributes['cristin_institution_id'] = list(self.institution.values())[0]

        del_lang_tag(self.attributes, 'unit_name', lang)

        try:
            del_lang_tag(self.attributes.parent_unit, 'unit_name', lang)
        except AttributeError:
            pass

        try:
            for unit in self.subunits:
                del_lang_tag(unit, 'unit_name', lang)
        except KeyError:
            pass

    def __str__(self):
        return f"{self.cristin_unit_id:15} : {self.unit_name}"

    @property
    def cristin_institution_id(self):
        """
        Returns:
            type: string
        """
        return self.get_property('cristin_institution_id')

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

class Institution(APIResource):
    """

    doc comes lates
    """
    URL = 'https://api.cristin.no/v2/institutions'
    schema = 'http://api.cristin.no/v2/doc/json-schemas/institutions_GET_response.json'

    def __init__(self, data, lang=DEFAULT_LANG):
        APIResource.__init__(self, data, lang)
        del_lang_tag(self.attributes, 'institution_name', lang)

        try:
            self.attributes['cristin_unit_id'] = self.attributes['corresponding_unit']['cristin_unit_id']
        except KeyError:
            self.attributes['cristin_unit_id'] = self.attributes['corresponding_unit'].values()[0]

    def __str__(self):
        return f"{self.cristin_unit_id:15}:{self.institution_name}"

    @property
    def cristin_unit_id(self):
        """
        Returns:
            type: string
        """
        return self.get_property('cristin_unit_id')

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

class Person(APIResource):
    """ Class desgined after cristins person JSON schema.

    doc comes later
    """

    schema = 'http://api.cristin.no/v2/doc/json-schemas/persons_GET_response.json'
    URL = "https://api.cristin.no/v2/persons"

    def __init__(self, data, lang=DEFAULT_LANG):
        APIResource.__init__(self, data, lang)

        for a in self.affiliations:
            del_lang_tag(a, 'position', lang)
            a['cristin_unit_id'] = a['unit']['cristin_unit_id']
            a['cristin_institution_id'] = a['institution']['cristin_institution_id']

    def __str__(self):
        return f"{self.cristin_person_id} : {self.surname}, {self.firstname}"

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
