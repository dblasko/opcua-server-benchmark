import asyncio
import logging

import click
import yaml

import experiments.servers.test_server as test_server


def __load_client_config(path="experiments/clients/config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


main = click.Group(help="Experiment controller")


@main.command("server", help="Start the experimental OPC UA server")
@click.option(
    "-n", "--name", "name", default="TestServer", help="Name of the OPC UA server"
)
@click.option("-p", "--port", "port", default="4840", help="Port of the OPC UA server")
@click.option(
    "-u",
    "--uri",
    "uri",
    default="http://examples.freeopcua.github.io",
    help="URI of the OPC UA server",
)
def main_server(name, port, uri):
    print("test")
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test_server.setup_server(name=name, uri=uri, port=port), debug=True)


# @click.option("--config", default="experiments/clients/config.yaml")
if __name__ == "__main__":
    exit(main())
