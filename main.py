#!/usr/bin/env python
from multiprocessing import Process, Queue
from db import CristinDB
from spider import Spider
import time


def start_db(queue):
    CristinDB(queue, verbose=False, threads=10)


def start_sp(queue):
    sp = Spider(queue, verbose=True, batch_size=10)
    sp.crawl_async_slots(58877)


if __name__ == '__main__':
    queue = Queue()
    procs = []

    db = Process(target=start_db, args=(queue,), daemon=True, name=f"neo4j")
    sp = Process(target=start_sp, args=(queue,), daemon=True, name=f"spider")
    procs.append(db)
    procs.append(sp)

    for p in procs:
        p.start()

    while(len(procs)):
        procs = list(filter(lambda x: x.is_alive(), procs))
        time.sleep(60)

    print("Exiting")
