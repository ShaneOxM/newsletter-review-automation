import multiprocessing
multiprocessing.set_start_method('spawn', force=True)

import redis
from rq import Worker, Queue, Connection

listen = ['default']
redis_conn = redis.Redis()

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()