import asyncio
import random
import time

import numpy as np
from asyncua import Client


class ResponsivenessJitterExperiment:
    def __init__(self, server_url, node_id, num_requests=1000, data_size=64):
        self.server_url = server_url
        self.node_id = node_id
        self.num_requests = num_requests
        self.data_size = data_size

    async def measure_responsiveness(self, client, mode):
        """Measures the responsiveness of a read or write request.

        Args:
            client: opcua client
            mode: "read" or "write"

        Raises:
            ValueError: if mode is not "read" or "write"

        Returns:
            float: responsiveness
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

        return end_time - start_time  # return the responsiveness

    async def run_experiment(self, mode):
        """Runs the experiment and computes the mean responsiveness and jitter.

        Args:
            mode: "read" or "write"
        """
        client = Client(self.server_url)
        await client.connect()

        responsiveness_list = []
        for i in range(self.num_requests):
            responsiveness = await self.measure_responsiveness(client, mode)
            responsiveness_list.append(responsiveness)
            print(
                f"Request {i+1}/{self.num_requests} completed with responsiveness {responsiveness:.3f} seconds"
            )

        await client.disconnect()

        # Computing our experiment metrics
        mean_responsiveness = np.mean(responsiveness_list)
        jitter = np.std(responsiveness_list)
        # Print the results
        print(f"Mean responsiveness: {mean_responsiveness:.3f} seconds")
        print(f"Jitter: {jitter:.3f} seconds")
        # TODO: write to file

    async def list_server_objects(self):
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
    # Define the server URL and the node ID of the data point
    server_url = "opc.tcp://localhost:4840"
    node_id = "ns=2;i=2"
    # Create an instance of the experiment
    experiment = ResponsivenessJitterExperiment(server_url, node_id)
    # asyncio.run(experiment.list_server_objects())
    # Run the experiment with read mode
    asyncio.run(experiment.run_experiment("read"))
    # Run the experiment with write mode
    asyncio.run(experiment.run_experiment("write"))
