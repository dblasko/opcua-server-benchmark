import asyncio
import logging

from asyncua import ua, Server


async def setup_server(name, uri, port):
    _logger = logging.getLogger(__name__)
    # Create OPC-UA server
    server = Server()
    await server.init()
    server.set_endpoint(f"opc.tcp://localhost:{port}/freeopcua/server/")
    server.set_server_name(name)

    # Create address space
    idx = await server.register_namespace(uri)
    root = server.get_objects_node()

    # Create object representing the 64 byte test data point
    obj = await root.add_object(idx, "TestDataPoint")
    var = await obj.add_variable(
        idx, "Value", ua.ByteString(b"\x00" * 64)
    )  # 64 byte data point
    await var.set_writable()

    # Start server
    # await server.start()

    async with server:
        _logger.info("Starting server")
        # Run server indefinitely
        while True:
            await asyncio.sleep(1)


# Start server setup
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(
        setup_server("TestServer", "http://examples.freeopcua.github.io", "4048"),
        debug=True,
    )
