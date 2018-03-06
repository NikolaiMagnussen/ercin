import requests
import ws


class Person():
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
    def first_name(self):
        return self.__attributes['first_name']

    @property
    def surname(self):
        return self.__attributes['surname']

    @property
    def private_email(self):
        return self.__attributes['private_email']

    @property
    def tel(self):
        return self.__attributes['tel']

    @property
    def cristin_person_id(self):
        return self.__attributes['cristin_person_id']

    @property
    def identified_cristin_person(self):
        return self.__attributes['identified_cristin_person']

    @property
    def date_of_birth(self):
        return self.__attributes['date_of_birth']

    @property
    def picture_url(self):
        return self.__attributes['picture_url']

    @property
    def cristin_profile_url(self):
        return self.__attributes['cristin_profile_url']

    @property
    def affiliations(self):
        return self.__attributes['affiliations']
