import asyncio
import logging

from asyncua import Client


logging.basicConfig(filename='logfile.log',
                    filemode='a',
                    format='%(asctime)s, %(name)s %(levelname)s %(message)s',
                    level=logging.DEBUG)
logging.info("Running OPC UA Client")
_logger = logging.getLogger("asyncua")

class HelloClient:
    def __init__(self, endpoint):
        self.client = Client(endpoint)

    async def __aenter__(self):
        await self.client.connect()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()


async def main():
    async with HelloClient("opc.tcp://localhost:4840/freeopcua/server/") as client:
        _logger.info("Root node is: %r", client.nodes.root)
        objects = client.nodes.objects
        _logger.info("Objects node is: %r", objects)

        hellower = await objects.get_child("0:Hellower")

        for i in range(100):
            print (i)
            await hellower.call_method("1:SayHello2", True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())






