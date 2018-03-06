import requests
import ws


class Person():
    """ Class desgined after cristins person JSON schema.

    doc comes later
    """
    URL = "https://api.cristin.no/v2/persons"

    def __init__(self, id=None, **kwargs):
        if id is not None:
            res = requests.get(f"{self.URL}/{id}")
            if res.status_code == 200:
                self.__attributes = res.json()
            else:
                raise LookupError
        elif id is None and kwargs != {}:
            self.__attributes = kwargs
        else:
            raise TypeError

    def get_results(self):
        return ws.get_results_by_person_id(self.cristin_person_id)

    @property
    def cristin_person_id(self):
        """
        Note:
            Required field in the person JSON schema

        Returns:
            type: string
        """
        return self.__attributes['cristin_person_id']

    @property
    def firstname(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        try:
            return self.__attributes['firstname']
        except KeyError:
            return ''

    @property
    def surname(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        try:
            return self.__attributes['surname']
        except KeyError:
            return ''

    @property
    def private_email(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        try:
            return self.__attributes['private_email']
        except KeyError:
            return ''

    @property
    def tel(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        try:
            return self.__attributes['tel']
        except KeyError:
            return ''

    @property
    def identified_cristin_person(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: boolean
        """
        try:
            return self.__attributes['identified_cristin_person']
        except KeyError:
            return False

    @property
    def date_of_birth(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        try:
            return self.__attributes['date_of_birth']
        except KeyError:
            return ''

    @property
    def picture_url(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        try:
            return self.__attributes['picture_url']
        except KeyError:
            return ''

    @property
    def cristin_profile_url(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: string
        """
        try:
            return self.__attributes['cristin_profile_url']
        except KeyError:
            return ''

    @property
    def affiliations(self):
        """
        Note:
            Optional field in the person JSON schema

        Returns:
            type: list
        """
        try:
            return self.__attributes['affiliations']
        except KeyError:
            return []


if __name__ == '__main__':
    start = 1
    end = 100000
    for i in range(start, end):
        # TESTING
        try:
            p = Person(id=i)
            if p.identified_cristin_person is False:
                print("icp: " + p.identified_cristin_person)
            if len(p.date_of_birth) != 0:
                print("dob: " + p.date_of_birth)
            if len(p.tel) != 0:
                print("tel: " + p.tel)

        except LookupError:
            continue
