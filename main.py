#!/usr/bin/env python
from cristin import rest


def query_collaborators():
    dag_id = 58877
    dag = rest.Person(dag_id)
    dag_results = dag.get_results()
    for res in dag_results:
        print(f"\n{res}")
        for collab in res.get_collaborators():
            print(f"\t{collab}")


class Spider():
    def __init__(self):
        self.results = set()
        self.authors = set()
        self.next_authors = set()

    def crawl(self, start_person):
        current_person = rest.Person(start_person)
        self.authors.add(current_person.cristin_person_id)
        for res in current_person.get_results():
            if res.tittel not in self.results:
                self.results.add(res.tittel)
                list(map(lambda a: self.next_authors.add(a.cristin_person_id),
                    filter(lambda a: a.cristin_person_id not in self.authors, res.get_collaborators())))

        # Print Information
        print(f"Crawled through the first person: {start_person}: Our Lord and Savior - Dag Johansen")
        print(f"\tNum next authors: {len(self.next_authors)} to crawl")
        print(f"\tNum authors: {len(self.authors)}")
        print(f"\tNum results: {len(self.results)}")

        while len(self.next_authors) > 0:
            current_person = rest.Person(self.next_authors.pop())
            self.authors.add(current_person.cristin_person_id)
            for res in current_person.get_results():
                if res.tittel not in self.results:
                    self.results.add(res.tittel)
                    list(map(lambda a: self.next_authors.add(a.cristin_person_id),
                        filter(lambda a: a.cristin_person_id not in self.authors, res.get_collaborators())))

            # Print Information
            print(f"\nCrawled through {current_person.cristin_person_id}: {current_person.firstname} {current_person.surname}")
            print(f"\tNum of authors to crawl: {len(self.next_authors)}")
            print(f"\tNum authors crawled: {len(self.authors)}")
            print(f"\tNum results crawled: {len(self.results)}")
        print(f"\nCrawl complete!")


if __name__ == "__main__":
    dag_id = 58877
    # query_collaborators()
    spider = Spider()
    spider.crawl(dag_id)
