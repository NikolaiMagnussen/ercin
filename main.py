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
        current_results = current_person.get_results()
        for res in current_results:
            if res.tittel not in self.results:
                self.results.add(res.tittel)
                list(map(lambda author: self.next_authors.add(author.cristin_person_id),
                         res.get_collaborators()))
        self.authors.add(current_person.cristin_person_id)
        self.next_authors = self.next_authors.difference(self.authors)

        # Print Information
        print(f"Crawled through the first person: {start_person}: Our Lord and Savior - Dag Johansen")
        print(f"\tNum next authors: {len(self.next_authors)}")
        print(f"\tNum authors: {len(self.authors)}")
        print(f"\tNum results: {len(self.results)}")

        while len(self.next_authors.difference(self.authors)) > 0:
            print(f"Only {len(self.next_authors.difference(self.authors))} remaining authors to crawl")
            current_person = rest.Person(self.next_authors.pop())
            for res in current_person.get_results():
                if res.tittel not in self.results:
                    self.results.add(res.tittel)
                    list(map(lambda author: self.next_authors.add(author.cristin_person_id),
                             res.get_collaborators()))
            self.authors.add(current_person.cristin_person_id)
            self.next_authors = self.next_authors.difference(self.authors)

            # Print Information
            print(f"\nCrawled through {current_person.cristin_person_id}: {current_person.firstname} {current_person.surname}")
            print(f"\tNum next authors: {len(self.next_authors)}")
            print(f"\tNum authors: {len(self.authors)}")
            print(f"\tNum results: {len(self.results)}")
        print(f"\nCrawl complete!")


if __name__ == "__main__":
    dag_id = 58877
    # query_collaborators()
    spider = Spider()
    spider.crawl(dag_id)
