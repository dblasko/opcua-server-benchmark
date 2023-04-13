import asyncio
import logging

from asyncua import Client

url = "opc.tcp://localhost:4840/freeopcua/server/"
namespace = "http://examples.freeopcua.github.io"

logging.basicConfig(filename='logfile.log',
                    filemode='a',
                    format='%(asctime)s, %(name)s %(levelname)s %(message)s',
                    level=logging.DEBUG)
logging.info("Running OPC UA Client")
_logger = logging.getLogger("asyncua")

class MyClient:
    def __init__(self, endpoint):
        self.client = Client(endpoint)

    async def __aenter__(self):
        await self.client.connect()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()


async def main():
    async with MyClient(url) as client:
        # Get namespace index
        nsidx = await client.get_namespace_index(namespace)
        _logger.info(f"Namespace index is: {nsidx}")

        # Get the root node
        root = client.nodes.root
        _logger.info("Root node is: %r", root)

        # Get the objects node -> look like i=85
        objects = client.nodes.objects
        _logger.info("Objects node is: %r", objects)

        # Get the variable node for read / write -> look like 'ns=2;i=3'
        read_only_var = await root.get_child(
            ["0:Objects", f"{nsidx}:MyObject", f"{nsidx}:MyReadOnlyVariable"]
        )

        writtable_var = await root.get_child(
            ["0:Objects", f"{nsidx}:MyObject", f"{nsidx}:MyVariable"]
        )

        # Read the value of the variable 100 times
        _logger.info("Read the value of the variable 1000 times")
        for i in range(1000):
            value = await read_only_var.read_value()

        # Write the value of the variable 100 times
        _logger.info("Write the value of the variable 1000 times")
        for i in range(1000):
            await writtable_var.write_value(50.)

        # Call a method 1000 times
        _logger.info("Call a method 1000 times")
        for i in range(100):
            await client.nodes.objects.call_method(f"{nsidx}:ServerMethod", 5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())






