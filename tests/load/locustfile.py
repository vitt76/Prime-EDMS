from locust import HttpUser, between, task


class AnalyticsUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def asset_bank_top_metrics(self):
        self.client.get('/api/v4/headless/analytics/dashboard/assets/top-metrics/')


