import asyncio
import random
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from asyncua import Client
from tqdm import tqdm


class ResponsivenessJitterThroughputExperiment:
    """Experiment for measuring the responsiveness, jitter and throughput of an OPC UA server."""

    def __init__(
        self,
        server_url,
        node_id,
        experiment_name=f'responsiveness_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}',
        num_requests=1000,
        data_size=64,
    ):
        self.server_url = server_url
        self.node_id = node_id
        self.experiment_name = experiment_name
        self.num_requests = num_requests
        self.data_size = data_size

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
        node = client.get_node(self.node_id)  # Get the node object from the node ID
        # Create a random data value of the given size
        data = bytes([random.randint(0, 255) for _ in range(self.data_size)])

        start_time = time.time()
        if mode == "read":
            await node.read_value()
        elif mode == "write":
            await node.write_value(data)
        else:
            raise ValueError("Invalid mode")
        end_time = time.time()

        return (start_time, end_time)

    async def run_experiment(self, mode):
        """Runs the experiment and measures start- and end-times of requests.

        Args:
            mode: "read" or "write"
        """
        client = Client(self.server_url)
        await client.connect()

        measurements = []
        for i in tqdm(
            range(self.num_requests),
            desc=f"Running {mode} mode responsiveness/jitter/throughput experiment",
            unit=" requests",
        ):
            start_time, end_time = await self.measure_response_times(client, mode)
            measurements.append(
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "data_size": self.data_size,
                    "mode": mode,
                }
            )
        await client.disconnect()

        # Computing our experiment metrics
        # mean_responsiveness = np.mean(responsiveness_list)
        # jitter = np.std(responsiveness_list)
        # Print the results
        # print(f"\t➡️ Mean responsiveness: {mean_responsiveness:.3f} seconds")
        # print(f"\t➡️ Jitter: {jitter:.3f} seconds")
        # Format and store the raw experiment results
        df = pd.DataFrame().from_records(measurements)
        output_file = f"response_times_{mode}.csv"
        output_dir = Path(f"data/{self.experiment_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_dir / output_file, index=False)
        print(f"\t➡️ Measurements written to {str(output_dir / output_file)}")

    async def list_server_objects(self):
        """For debug purposes only. Lists all objects in the server to understand their id's/structure."""
        client = Client(self.server_url)
        await client.connect()
        root = client.get_objects_node()
        children = await root.get_children()
        for node in children:
            dname = await node.read_display_name()
            print(f"Node ID: {node.nodeid} display name: {dname.Text}")

        node = client.get_node("ns=2;i=1")
        children = await node.get_children()
        for node in children:
            dname = await node.read_display_name()
            print(f"Node ID: {node.nodeid} display name: {dname.Text}")

        client.disconnect()


if __name__ == "__main__":
    # Example use

    # Define the server URL and the node ID of the data point
    server_url = "opc.tcp://localhost:4840"
    node_id = "ns=2;i=2"
    # Create an instance of the experiment
    experiment = ResponsivenessJitterThroughputExperiment(server_url, node_id)
    # asyncio.run(experiment.list_server_objects())
    # Run the experiment with read mode
    asyncio.run(experiment.run_experiment("read"))
    # Run the experiment with write mode
    asyncio.run(experiment.run_experiment("write"))