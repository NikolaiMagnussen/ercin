#!/usr/bin/env python
from cristin import rest
from requests_futures.sessions import FuturesSession
import time


def query_collaborators():
    dag_id = 58877
    dag = rest.Person(dag_id)
    dag_results = dag.get_results()
    for res in dag_results:
        print(f"\n{res}")
        for collab in res.get_collaborators():
            print(f"\t{collab}")


class Spider():
    def __init__(self, batch_size=10):
        self.results = set()
        self.authors = set()
        self.next_authors = set()
        self.batch_size = batch_size
        self.request_slots = [None] * batch_size
        self.session = FuturesSession(max_workers=10)

    def print_stats(self, current_person):
        print(f"Crawled through {current_person.cristin_person_id}:"
              f"{current_person.firstname} {current_person.surname}")
        print(f"\tNum of authors to crawl: {len(self.next_authors)}")
        print(f"\tNum authors crawled: {len(self.authors)}")
        print(f"\tNum results crawled: {len(self.results)}\n")

    def process_results(self, results):
        for res in results:
            if res.tittel not in self.results:
                self.results.add(res.tittel)
                list(map(lambda a:
                         self.next_authors.add(a.cristin_person_id),
                         filter(lambda a:
                                a.cristin_person_id not in self.authors,
                                res.get_collaborators())))

    def crawl_sync(self, start_person):
        current_person = rest.Person(start_person)
        self.authors.add(current_person.cristin_person_id)
        self.process_results(current_person.get_results())

        # Print Information
        self.print_stats(current_person)

        while len(self.next_authors) > 0:
            current_person = rest.Person(self.next_authors.pop())
            self.authors.add(current_person.cristin_person_id)
            results = current_person.get_results()
            self.process_results(results)

            # Print Information
            self.print_stats(current_person)
        print(f"\nCrawl complete!")

    def crawl_async_slots(self, start_person):
        # Can do this synchronously
        current_person = rest.Person(start_person)
        self.authors.add(current_person.cristin_person_id)
        self.process_results(current_person.get_results())

        # Print Information
        self.print_stats(current_person)

        # This must be done async!
        last = None
        while len(self.next_authors) > 0:
            start_time = time.perf_counter()
            for i in range(self.batch_size):
                if self.request_slots[i] is None:
                    # New request
                    curr = rest.Person(self.next_authors.pop())
                    self.authors.add(curr.cristin_person_id)
                    self.request_slots[i] = curr.get_results(self.session)
                elif self.request_slots[i].done():
                    # A request is completed
                    resp = self.request_slots[i].result().data
                    self.process_results(resp)
                    self.request_slots[i] = None

            # Print Information
            if curr != last:
                print(f"At least one result crawled in "
                      f"{time.perf_counter()-start_time:.2f}s")
                self.print_stats(curr)
            last = curr
        print(f"\nCrawl complete!")

    def crawl_async_batch(self, start_person):
        # Can do this synchronously
        current_person = rest.Person(start_person)
        self.authors.add(current_person.cristin_person_id)
        self.process_results(current_person.get_results())

        # Print Information
        self.print_stats(current_person)

        # This must be done async!
        while len(self.next_authors) > 0:
            # Spin off a number of requests to get results
            async_reqs = []
            start_time = time.perf_counter()
            for _ in range(self.batch_size):
                # Get next person and add to set of crawled authors
                current_person = rest.Person(self.next_authors.pop())
                self.authors.add(current_person.cristin_person_id)

                # Fire off the request
                async_reqs.append(current_person.get_results(self.session))

            print(f"Spinning of requests took "
                  f"{time.perf_counter()-start_time:.2f}s")
            start_time = time.perf_counter()

            # Handle each request as soon as it finish
            while len(async_reqs) > 0:
                for req in async_reqs:
                    # Handle the finished request and remove it from the list
                    if req.done():
                        self.process_results(req.result().data)
                        async_reqs.remove(req)
                        req_num = self.batch_size-len(async_reqs)
                        print(f"Request {req_num}/{self.batch_size} "
                              f"took {time.perf_counter()-start_time:.2f}s")

            # Print Information
            self.print_stats(current_person)
        print(f"\nCrawl complete!")


if __name__ == "__main__":
    dag_id = 58877
    # query_collaborators()
    spider = Spider(batch_size=20)
    spider.crawl_async_slots(dag_id)
