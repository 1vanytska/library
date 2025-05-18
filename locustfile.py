from locust import HttpUser, task, between

class BookApiUser(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def get_books(self):
        self.client.get("/books/?limit=5")
