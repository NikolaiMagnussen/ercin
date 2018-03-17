#!/usr/bin/env python
from multiprocessing import Process, Queue
from db import CRUD_neo4j
from spider import Spider
import time

def start_db(queue, **kwarg):
    db = CRUD_neo4j(queue, **kwarg)
    db.run()

def start_spider(queue, **kwarg):
    sp = Spider(queue, **kwarg)
    sp.crawl_sync(58877)

if __name__ == '__main__':
    queue = Queue()
    procs = []

    for pid in range(1):
        db = Process(target=start_db, args=(queue,), kwargs={}, daemon=True, name=f"neo4j:{pid}")
        db.start()
        procs.append(db)

    sp = Process(target=start_spider, args=(queue,), kwargs={}, daemon=True, name=f"spider:{pid}")
    sp.start()
    procs.append(sp)

    while(len(procs)):
        procs = list(filter(lambda x: x.is_alive(), procs))
        time.sleep(60)
