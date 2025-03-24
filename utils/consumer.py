from redis_queue import RedisQueue

with RedisQueue() as queue:
    while True:
        queue.consume()
