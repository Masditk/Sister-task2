from locust import HttpUser, task, between

class DistributedNodeUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def publish_event(self):
        self.client.post("/publish", json={"topic": "sync", "data": "event"})
