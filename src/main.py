#!/usr/bin/env python
from multiprocessing import Process, Queue
from db import CristinDB
from spider import Spider
import time
import os
import gc


def start_db(queue):
    CristinDB(queue, verbose=False, threads=10)
    print("[INFO] CristinDB is done running - exiting")
    gc.collect()


def start_sp(queue, parent_queue):
    sp = Spider(queue, parent_queue, verbose=True, batch_size=10)
    sp.crawl_async_slots()
    print("[INFO] I am done crawling - handing over to someone else")
    gc.collect()


if __name__ == '__main__':
    queue = Queue()
    parent_queue = Queue()
    procs = []

    # Initial person is 58877
    parent_queue.put(set())
    parent_queue.put(set())
    parent_queue.put({58877})

    db = Process(target=start_db, args=(queue,), daemon=True, name=f"neo4j")
    sp = Process(target=start_sp, args=(queue, parent_queue,), daemon=True, name=f"spider")
    procs.append(db)
    procs.append(sp)

    for p in procs:
        p.start()

    while(len(procs)):
        time.sleep(10)
        procs = list(filter(lambda x: x.is_alive(), procs))
        print(f"[INFO] Remaining processes: {procs}")

        # Get sets from child
        results = parent_queue.get()
        authors = parent_queue.get()
        next_authors = parent_queue.get()

        # Close previous queue and create new one
        parent_queue.close()
        start_wait = time.perf_counter()
        sp.join()
        print(f"[INFO] Waited {time.perf_counter()-start_wait:.2f} seconds for DB to digest")
        parent_queue = Queue()

        sp = Process(target=start_sp, args=(queue, parent_queue,), daemon=True, name=f"spider")
        procs.append(sp)
        sp.start()

        # Put sets back into child
        parent_queue.put(results)
        parent_queue.put(authors)
        parent_queue.put(next_authors)

    print("[INFO] Exiting")
