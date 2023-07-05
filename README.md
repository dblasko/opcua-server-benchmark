# opcua-server-benchmark
A tool for the benchmarking and evaluation of OPC UA servers.

## Dependencies
We recommend creating a conda environment to install the project with its dependencies (*optional step*):
```bash
conda create -n opcua python==3.10
conda activate opcua
```
Then, you can simply install the project with its dependencies as a package (from the root folder):
```bash
pip install -e .
```

## Usage
All commands should be execute from the root folder of the project (*where `setup.py` is located*). For general usage that will be described in this section, everything is controlled through the CLI: `bin/experiment_controller.py`. To modify the experiments or add new ones, refer to the next section "Extending and adding experiments".

### Running a local test OPC UA server
You can start an OPC UA server locally to run the different experiments on your machine. To do so, use:
```bash
python bin/experiment_controller.py server
```
The **`server`** command supports the following **options**:

- **`-n` or `--name` (optional)**: To specify a custom server name. **Defaults to "TestServer"**.
- **`-u` or `--uri` (optional)**: To specify a custom base URI.
- **`-p` or `--port` (optional)**: To specify the port the server should be exposed on. **Defaults to 4840**.
  
The server is then available on `opc.tcp://localhost:4840`, with the following nodes:

- Id: `ns=2;i=2`: 64 byte read/write node.


### Running (client) experiments on an OPC UA server
All available experiments rely on OPC UA clients that connect to a given server. The server you connect to, and the nodes you query, can be configured before running commands in the `experiments/config.yaml` file. 

If you specify a property configured in that file through a command option, the value from the config file is ignored.

Example contents of such a configuration file:
```yaml
# Server configuration:
server_url: opc.tcp://{SERVER IP}:{SERVER PORT}
server_user: {SERVER USERNAME}
server_password: {SERVER PASSWORD}
# The three following properties are only necessary if the connexion requires a certificate:
server_certificate_application_uri: {SERVER CERTIFICATE APPLICATION URI, e.g. urn:DESKTOP-MENVCAI%253AUnifiedAutomation%253AUaExpert)}
server_public_cert: {PATH TO PUBLIC CERT, e.g. "uaexpert.der"}
server_private_cert: {PATH TO PRIVATE CERT, e.g. "uaexpert.pem"}

# The following properties are used to configure the nodes to query in the experiments:
nodes_to_query_ids:
  - identifier: {NODE ID, e.g. /Channel/State/progStatus or DMU75_1.VAR1}
  # List as many nodes as you want to query in the experiments.
```
*Note: If the server requires a connexion with certificates, we recommend generating the certificates with a software like UAExpert, and copying the two certificate files to the root of the project.*

#### Running experiments to generate data
The different implemented experiments can be found under `experiments/clients`: each Python file corresponds to an experiment you can run. The name of the file before the '.py' will be referenced as **EXPERIMENT_NAME** in the following part. 

To run one or multiple experiments, use:
```bash
python bin/experiment_controller.py run-experiment EXPERIMENT_NAME [EXPERIMENT_NAME2 ...]
```
The **`run-experiment`** command supports the following **options**:

- **`-n` or `--name` (optional)**: name of your experimental session. The experiment's results will be stored under `data/{NAME}`. If a session with that name already exists, the previous results will be replaced if the given experiment had already been run in that session. Otherwise, they will be added next to the results of the other experiments of the session. **By default, the current timestamp will be used.**
- **`-p` or `--post-process` (optional)**: If specified, the results of the experiment are directly post-processed after generation. Disabled by default.
- **`-c` or `--config` (optional)**: Allows to specify a custom experiment config file (used instead of `experiments/config.yaml`). 

Some options are specific to particular experiments:

- **responsivess_jitter_throughput & scalability**
  - **`-m` or `--mode` (optional)**: used to specify if the requests should only be done as "`read`" or "`write`". **By default, the experiment is run once for each mode.**
  - **`-nn` or `--nnodes` (optional)**: used to specify a limit to the number of nodes to be read at the same time in the experiment. If you provide a list of nodes in the configuration file and specify a value for this option, only the n first nodes listed will be used. By default, all nodes specified in the configuration file are used.
- **scalability**
  - **`-nc` or `--nclients` (optional)**: used to specify how many clients/experiments to run in parallel. **Defaults to 10.**
- **scalability_evolution**
  - **`-lc` or `--listclients` (optional)**: used to specify the list of numbers of clients for which to run the scalability experiment. In the form `1,10,50,...` - leads to measure the metrics for 1 client, 10 clients and 50 clients in parallel.  **Defaults to 1,3,5,10.**


#### Processing experimental data
Running experiments generates raw data that is stored in CSV format under `data/{SESSION NAME}`. You can process that data at anytime to generate experimental reports (for example, converting request timestamps to responsiveness, jitter and throughput measurements). The generated results are stored in `data/{SESSION NAME}/results` - previously generated analyses, if they exist, are overwritten. 

To generate the analysis for a given experimental session, use:
```bash
python bin/experiment_controller.py post-process SESSION_NAME [SESSION_NAME2 ...]
```
The experiments that have been run in the session are automatically detected and processed.

**Multi-node experiments summary**: When running multiple experiments that query multiple nodes, and doing that for different numbers of nodes (to observe scaling), you end up with one experiment-session folder per number of nodes. An extra script has been written under `analysis/node_scaling_comparison.py` to generate a visual summary of the multiple experiments. To run it, please update the `EXPERIMENT_PREFIX` constant in the code to the prefix the different experiment-session folders have in common (e.g. `"data/wfl_21_june_"` if you have `"data/wfl_21_june_10_nodes"` and `"data/wfl_21_june_20_nodes"`).


____
## Extending and adding experiments 
To implement new experiments, create your experiment file and class under `experiments/clients`. The experiment class should at least implement a `run_experiment` method. The files generated as an ouput of the experiment should be prefixed with the class name (`self.__class__.__name__`) to be automatically detected when analysis is run by the user. Name the file as "experiment_name" with underscores as separators. The class in the file should be named as "ExperimentNameExperiment", with "Experiment" at the end.

Then, if your experiment takes additional experiment-specific options, you can add those in the `bin/experiment_controller.py` similarly to the other experiments that do so in the file. 

Finally, you should create the experiment post-processing class in a Python file with the same name as the experiment class (but replace "Experiment" with "Analysis") under `analysis`. The analysis should be wrapped in a `generate` method of the class. 

Your new experiment should then be supported by the controller and can be used as specified by this documentation.

____
## Common issues
### Cannot start the test server because the port is already in use
You can find the PID of the process using the port (generally the test server that has not been stopped properly) with `sudo lsof -i :4840`, and kill that process with `kill -9 PID`.
