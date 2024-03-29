import asyncio
import random
import time
from datetime import datetime
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from asyncua import Client
from tqdm import tqdm


class ResponsivenessJitterThroughputExperiment:
    """Experiment for measuring the responsiveness, jitter and throughput of an OPC UA server."""

    def __init__(
        self,
        server_url,
        node_ids,
        server_user,
        server_password,
        server_cert_app_uri,
        server_pub_cert,
        server_priv_cert,
        experiment_name=f'responsiveness_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}',
        num_requests=1000,
        data_size=64,
        filename_prefix="",
        experiment_number="",
    ):
        self.server_url = server_url
        self.node_ids = node_ids
        self.experiment_name = experiment_name
        self.num_requests = num_requests
        self.data_size = data_size
        self.filename_prefix = str(filename_prefix)
        self.experiment_number = str(experiment_number)
        self.server_user = server_user
        self.server_password = server_password
        self.server_cert_app_uri = server_cert_app_uri
        self.server_pub_cert = server_pub_cert
        self.server_priv_cert = server_priv_cert

    async def measure_response_times(self, client, mode):
        """Measures the response time of a read or write request.

        Args:
            client: opcua client
            mode: "read" or "write"

        Raises:
            ValueError: if mode is not "read" or "write"

        Returns:
            float: start time of the request
            float: end time of the request
        """
        # node = client.get_node(self.node_id)  # Get the node object from the node ID
        nodes_to_read = [client.get_node(node_id) for node_id in self.node_ids]
        # Create a random data value of the given size
        data = bytes([random.randint(0, 255) for _ in range(self.data_size)])
        size_read = None

        start_time = time.time()
        if mode == "read":
            read = await client.read_values(nodes_to_read)
            size_read = np.sum([sys.getsizeof(r) for r in read])
        elif mode == "write":
            await client.write_values(
                nodes_to_read, [data for i in range(len(nodes_to_read))]
            )
        else:
            raise ValueError("Invalid mode")
        end_time = time.time()

        return (start_time, end_time, size_read)

    async def run_experiment(self, mode=None):
        """Runs the experiment and measures start- and end-times of requests.

        Args:
            mode: "read" or "write"
        """
        if mode is None:  # If no mode is specified, run both read and write mode
            await self.run_experiment(mode="read")
            await self.run_experiment(mode="write")
            return

        client = Client(self.server_url)
        client.set_user(self.server_user)
        client.set_password(self.server_password)
        if self.server_cert_app_uri is not None:
            client.application_uri = self.server_cert_app_uri
            await client.set_security_string(
                "Basic256,Sign,uaexpert.der,uaexpert_key.pem"
            )
        try:
            await client.connect()
        except Exception as e:
            print(f"Error: {e}")

        measurements = []
        for i in tqdm(
            range(self.num_requests),
            desc=f"Running {mode} mode responsiveness/jitter/throughput experiment",
            unit=" requests",
        ):
            start_time, end_time, data_size_read = await self.measure_response_times(
                client, mode
            )
            measurements.append(
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "data_size": self.data_size if mode == "write" else data_size_read,
                    "mode": mode,
                }
            )
        await client.disconnect()

        df = pd.DataFrame().from_records(measurements)
        output_file = f"{('ScalabilityEvolutionExperiment_'+self.experiment_number+'_') if self.experiment_number != '' else ''}{('ScalabilityExperiment_' + self.filename_prefix + '_') if self.filename_prefix != '' else ''}{self.__class__.__name__}_{mode}.csv"  # Important to have the experiment class name at the beginning of the output file for automatic detection by the analyzer
        output_dir = Path(f"data/{self.experiment_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_dir / output_file, index=False)
        print(f"\t➡️ Measurements written to {str(output_dir / output_file)}")


if __name__ == "__main__":
    # Example use

    # Define the server URL and the node ID of the data point
    server_url = "opc.tcp://localhost:4840"
    node_id = "ns=2;i=2"
    # Create an instance of the experiment
    experiment = ResponsivenessJitterThroughputExperiment(server_url, node_id)
    # Run the experiment with read mode
    asyncio.run(experiment.run_experiment("read"))
    # Run the experiment with write mode
    asyncio.run(experiment.run_experiment("write"))
