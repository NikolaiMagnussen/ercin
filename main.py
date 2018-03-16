#!/usr/bin/env python
from multiprocessing import Process, Queue
from db import CRUD_neo4j
from cristin import rest
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

    queue.put(rest.Person(dag_id))

    x = input("press Enter to exit\n")
