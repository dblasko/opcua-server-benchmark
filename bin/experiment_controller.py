import asyncio
import logging
import importlib
from pathlib import Path
from datetime import datetime

import click
import yaml

import experiments.servers.test_server as test_server


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


def ___filename_to_classname(filename, type="Experiment"):
    # type is Experiment or Analysis
    return filename.replace("_", " ").title().replace(" ", "") + (type)


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
@click.option(
    "-nc",
    "--nclients",
    "nclients",
    default=10,
    help="Number of clients to run in parallel",
)
def main_run_experiment(experiments, config, name, post_process, mode, nclients):
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
        if nclients is not None:
            run_experiment_args["n_clients"] = nclients

        try:
            experiment_class_ = getattr(
                importlib.import_module(f"experiments.clients.{experiment}"),
                ___filename_to_classname(experiment, type="Experiment"),
            )
            experiment_client = experiment_class_(**experiment_constructor)
            asyncio.run(experiment_client.run_experiment(**run_experiment_args))
        except Exception as e:
            print(e)
            click.echo(
                "Could not load valid experiment class, check if it exists and if it has a run_experiment method, and server_url, node_id and experiment_name in its constructor arguments. Skipping this experiment."
            )
            pass

        # Post-process if requested
        if post_process:
            try:
                analysis_class_ = getattr(
                    importlib.import_module(f"analysis.{experiment}"),
                    ___filename_to_classname(experiment, type="Analysis"),
                )
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
    "session_names",
    nargs=-1,
    required=True,
    type=str,
)
def main_post_process(session_names):
    # Detect all experiments that have been run in the session folder
    for session_name in session_names:
        click.echo(f"Detecting experiment results in session {session_name}...")
        detected_experiments = set()
        try:
            path = f"data/{session_name}/"
            results_pathlist = Path(path).glob("*")
            for r_path in results_pathlist:
                for experiment in available_experiments:
                    if (
                        r_path.is_file()
                        and "__" not in str(r_path)
                        and str(r_path.name).startswith(
                            ___filename_to_classname(experiment, "Experiment")
                        )
                    ):
                        detected_experiments.add(experiment)
        except:
            click.echo("Could not find the requested session folder in data.")
            pass
        if len(detected_experiments) == 0:
            click.echo("No experimental results found in the session folder.")
            pass

        # For each detected experiment, run the according analyzer
        for experiment in detected_experiments:
            try:
                analysis_class_ = getattr(
                    importlib.import_module(f"analysis.{experiment}"),
                    ___filename_to_classname(experiment, type="Analysis"),
                )
                analysis_client = analysis_class_(experiment_name=session_name)
                analysis_client.generate()
            except Exception as e:
                print(e)
                click.echo(
                    f"Could not post-process results of {experiment}, check if a class with the same name as the experiment is defined with a generate method in the analysis folder. Skipping this experiment."
                )


if __name__ == "__main__":
    exit(main())
