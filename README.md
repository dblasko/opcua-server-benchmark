# opcua-server-benchmark
A tool for the benchmarking and evaluation of OPC UA servers.

## Dependencies
We recommend creating a conda environment to install the project with its dependencies:
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
  
The server is then available on `opc.tcp://localhost:4840`, with the following nodes:

- Id: `ns=2;i=2`: 64 byte read/write node.


### Running (client) experiments on an OPC UA server
All available experiments rely on OPC UA clients that connect to a given server. The server you connect to, and the nodes you query, can be configured before running commands in the `experiments/config.yaml` file. 

If you specify a property configured in that file through a command option, the value from the config file is ignored.

#### Running experiments to generate data
The different implemented experiments can be found under `experiments/clients`: each Python file corresponds to an experiment you can run. The name of the file before the '.py' will be referenced as **EXPERIMENT_NAME** in the following part. 

To run one or multiple experiments, use:
```bash
python bin/experiment_controller.py run-experiment -e EXPERIMENT_NAME [-e EXPERIMENT_NAME2 ...]
```
The **`run-experiment`** command supports the following **options**:

- **`-n` or `--name` (optional)**: name of your experimental session. The experiment's results will be stored under `data/{NAME}`. If a session with that name already exists, the previous results will be replaced if the given experiment had already been run in that session. Otherwise, they will be added next to the results of the other experiments of the session. **By default, the current timestamp will be used.**
- **`-p` or `--post-process` (optional)**: If specified, the results of the experiment are directly post-processed after generation. Disabled by default.

Some options are specific to particular experiments:

- **responsiveness-jitter-throughput**
  - **`-m` or `--mode` (optional)**: used to specify if the requests should only be done as "`read`" or "`write`". **By default, the experiment is run once for each mode.**


#### Processing experimental data
Running experiments generates raw data that is stored in CSV format under `data/{SESSION NAME}`. You can process that data at anytime to generate experimental reports (for example, converting request timestamps to responsiveness, jitter and throughput measurements). The generated results are stored in `data/{SESSION NAME}/results` - previously generated analyses, if they exist, are overwritten. 

To generate the analysis for a given experimental session, use:
```bash
python bin/experiment_controller.py post-process -e SESSION_NAME
```
The experiments that have been run in the session are automatically detected and processed.


____
## Extending and adding experiments 
To implement new experiments, create your experiment file and class under `experiments/clients`. In general, the experiment class should at least implement a `run_experiment` method.

Then, if your experiment takes additional experiment-specific options, you can add those in the `bin/experiment_controller.py` similarly to the other experiments that do so in the file. 

Finally, you should create the experiment post-processing class in a Python file with the same name as the experiment class under `analysis`. The analysis should be wrapped in a `generate` method of the class. 

Your new experiment should then be supported by the controller and can be used as specified by this documentation.

____
## Common issues
### Cannot start the test server because the port is already in use
You can find the PID of the process using the port (generally the test server that has not been stopped properly) with `sudo lsof -i :4840`, and kill that process with `kill -9 PID`.
