import unittest
import warnings
from cristin import ws, rest

def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            test_func(self, *args, **kwargs)
    return do_test

class TestCristinAPI(unittest.TestCase):
    @ignore_warnings
    def test_ws_existing_person(self):
        results = ws.get_results_by_person_id(1)
        for i in results:
            self.assertTrue(isinstance(i, ws.Result))
            self.assertTrue(isinstance(i.tittel, str))
            if isinstance(i.person, dict):
                person = rest.Person(i.person['id'])
            else:
                self.assertTrue(isinstance(i.person, list))
                for p in i.person:
                    person = rest.Person(p['id'])
                    self.assertTrue(isinstance(person.surname, str))
                    self.assertTrue(isinstance(person.cristin_person_id,
                        str))

    @ignore_warnings
    def test_ws_no_person(self):
        results = ws.get_results_by_person_id(2)
        self.assertTrue(isinstance(results, list))
        self.assertTrue(len(results) == 0)

    @ignore_warnings
    def test_rest_persons(self):
        start = 1
        end = 10
        for i in range(start, end):
            p = rest.Person(i)
            self.assertTrue(isinstance(p.surname, str))
            self.assertTrue(isinstance(p.cristin_person_id, str))
