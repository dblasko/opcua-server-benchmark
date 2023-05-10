import time
from datetime import datetime
import asyncio

from experiments.clients.responsiveness_jitter_throughput import (
    ResponsivenessJitterThroughputExperiment,
)


class ScalabilityExperiment:
    """Experiment for measuring the scalability of an OPC UA server. Runs n_client responsiveness-jitter-throughput experiments in parallel."""

    def __init__(
        self,
        server_url,
        node_id,
        server_user,
        server_password,
        server_cert_app_uri,
        server_pub_cert,
        server_priv_cert,
        experiment_name=f'scalability_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}',
        num_requests=1000,
        data_size=64,
        experiment_number="",
    ):
        self.server_url = server_url
        self.node_id = node_id
        self.experiment_name = experiment_name
        self.num_requests = num_requests
        self.data_size = data_size
        self.experiment_number = str(experiment_number)
        self.server_user = server_user
        self.server_password = server_password
        self.server_cert_app_uri = server_cert_app_uri
        self.server_pub_cert = server_pub_cert
        self.server_priv_cert = server_priv_cert

    async def run_experiment(self, n_clients=10, mode=None):
        """

        Args:
            mode: "read" or "write"

        Raises:
            ValueError: if mode is not "read" or "write"
        """
        experiment_clients = []
        for i in range(n_clients):
            experiment_clients.append(
                ResponsivenessJitterThroughputExperiment(
                    self.server_url,
                    self.node_id,
                    self.server_user,
                    self.server_password,
                    self.server_cert_app_uri,
                    self.server_pub_cert,
                    self.server_priv_cert,
                    self.experiment_name,
                    self.num_requests,
                    self.data_size,
                    i,
                    self.experiment_number,
                ).run_experiment(mode)
            )
        await asyncio.gather(*experiment_clients)
