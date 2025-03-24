import redis
import json


class RedisQueue:
    def __init__(self, host="localhost", port=6379, db=0, queue_name="ride_queue"):
        self.queue_name = queue_name
        self.redis_client = redis.Redis(host=host, port=port, db=db)

    def __enter__(self):
        return self

    def publish(self, message):
        """Push a message to the Redis queue."""
        data = json.dumps(message)
        self.redis_client.lpush(self.queue_name, data)
        print(f"Published: {data}")

    def consume(self):
        """Pop a message from the Redis queue (blocking)."""
        _, message = self.redis_client.brpop(self.queue_name)
        data = json.loads(message)
        print(f"Consumed: {data}")
        return data

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Handle cleanup if needed."""
        print("Closing RedisQueue context.")
