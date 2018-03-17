#!/usr/bin/env python
from multiprocessing import Process, Queue
from db import CRUD_neo4j
from cristin import rest, ws
import time

dag_id = 58877

def start_db(queue):
    db = CRUD_neo4j(queue)
    db.run()

def start_spider(queue):
    pass

if __name__ == '__main__':
    queue = Queue()
    for pid in range(1):
        db = Process(target=start_db, args=(queue,), daemon=True, name=f"pid:{pid}")
        db.start()

    queue.put(rest.Person(1))

    #for r in ws.get_results_by_person_id(dag_id):
    #    queue.put(r)

    x = input("press Enter to exit\n")
