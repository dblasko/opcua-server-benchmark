import asyncio
import logging
import importlib
from pathlib import Path
from datetime import datetime

import click
import yaml

import experiments.servers.test_server as test_server
import experiments.clients as clients
import analysis


def __load_client_config(path="experiments/clients/config.yaml"):
    with open(path) as f:
        config = yaml.safe_load(f)
        if (
            config is None
            or "server_url" not in config
            or "node_to_query_id" not in config
        ):
            raise Exception
        return config


def __load_experiment_list(path="experiments/clients/"):
    experiments_pathlist = Path(path).glob("*.py")
    return [
        str(e_path).replace(path, "").replace(".py", "")
        for e_path in experiments_pathlist
        if e_path.is_file() and "__" not in str(e_path)
    ]


# CLI SETUP
main = click.Group(help="Experiment controller")
available_experiments = __load_experiment_list()


# SERVER
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
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test_server.setup_server(name=name, uri=uri, port=port), debug=True)


# EXPERIMENTS
@main.command("run-experiment", help="Run an experiment")
@click.argument(
    "experiments", nargs=-1, required=True, type=click.Choice(available_experiments)
)
@click.option("-c", "--config", "config", default="experiments/config.yaml")
@click.option(
    "-n",
    "--name",
    "name",
    default=datetime.now().strftime("%d-%m-%Y_%H-%M-%S"),
    help="Name of the experiment session (and of the result folder)",
)
@click.option(
    "-p",
    "--post-process",
    "post_process",
    default=False,
    is_flag=True,
    help="Post-process the results after the experiment (flag)",
)
# Experiment specific options
@click.option(
    "-m",
    "--mode",
    "mode",
    default=None,
    type=click.Choice(["read", "write"]),
    help="(responsiveness-jitter-throughput ONLY) Specify read or write mode requests, by default both are performed",
)
def main_run_experiment(experiments, config, name, post_process, mode):
    # Load config
    try:
        config = __load_client_config(config)
    except:
        click.echo(
            f"Could not load config file at {config}, or it misses required fields (server_url, node_to_query_id)."
        )
        return
    # Run experiments
    for experiment in experiments:
        click.echo(f"Running requested experiment {experiment}...")
        # TODO: add experiment specific options that go to constructor when necessary
        experiment_constructor = {
            "server_url": config["server_url"],
            "node_id": config["node_to_query_id"],
            "experiment_name": name,
        }
        # Load experiment-specific options that are passed to run_experiment
        run_experiment_args = {}
        if mode is not None:
            run_experiment_args["mode"] = mode

        try:
            experiment_class_ = getattr(clients, experiment)
            experiment_client = experiment_class_(**experiment_constructor)
            experiment_client.run_experiment(**run_experiment_args)
        except Exception:
            click.echo(
                "Could not load valid experiment class, check if it exists and if it has a run_experiment method, and server_url, node_id and experiment_name in its constructor arguments. Skipping this experiment."
            )
            pass

        # Post-process if requested
        if post_process:
            try:
                analysis_class_ = getattr(analysis, experiment)
                analysis_client = analysis_class_(experiment_name=name)
                analysis_client.generate()
            except Exception:
                click.echo(
                    f"Could not post-process results of {experiment}, check if a class with the same name as the experiment is defined with a generate method in the analysis folder. Skipping this step."
                )


# ANALYSIS
@main.command(
    "post-process", help="Generate the analysis of the data from an experiment"
)
@click.argument(
    "session_name",
    nargs=-1,
    required=True,
    type=str,
    help="Name of the experimental session to post-process",
)
def main_post_process(session_name):
    # Detect all experiments that have been run in the session

    # for each, instanciate analyzer & run it w/ log messages
    pass


if __name__ == "__main__":
    exit(main())
