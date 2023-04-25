from datetime import datetime

from experiments.clients.scalability import (
    ScalabilityExperiment,
)


class ScalabilityEvolutionExperiment:
    """Experiment for measuring the impact of running multiple OPC UA client in parallel. Runs the scalability experiment with various number of clients."""

    def __init__(
        self,
        server_url,
        node_id,
        experiment_name=f'scalability_Evolution_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}',
        num_requests=1000,
        data_size=64,
    ):
        self.server_url = server_url
        self.node_id = node_id
        self.experiment_name = experiment_name
        self.num_requests = num_requests
        self.data_size = data_size

    async def run_experiment(self, l_clients=[1, 3, 5, 10], mode=None):
        """
        Args:
            mode: "read" or "write"

        Raises:
            ValueError: if mode is not "read" or "write"
        """
        for i in range(len(l_clients)):
            await ScalabilityExperiment(
                self.server_url,
                self.node_id,
                self.experiment_name,
                self.num_requests,
                self.data_size,
                l_clients[i],
            ).run_experiment(l_clients[i], mode)
