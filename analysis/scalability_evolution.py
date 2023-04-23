from pathlib import Path
import json
import os

import pandas as pd
import numpy as np


class ScalabilityEvolutionAnalysis:
    """_summary_"""

    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        self.evolutions_read = []
        self.read_dataframes = []
        self.evolutions_write = []
        self.write_dataframes = []
        input_dir = Path(f"data/{self.experiment_name}/")
        input_files_read = Path(input_dir).glob(
            "ScalabilityEvolutionExperiment_*_ScalabilityExperiment_*_ResponsivenessJitterThroughputExperiment_read.csv"
        )
        input_files_write = Path(input_dir).glob(
            "ScalabilityEvolutionExperiment_*_ScalabilityExperiment_*_ResponsivenessJitterThroughputExperiment_write.csv"
        )

        if not input_dir.exists():
            raise ValueError(
                f"Data directory for the experiment {self.experiment_name}, {input_dir}, does not exist."
            )

        for filname in input_files_read:
            self.evolutions_read.append(os.path.basename(filname).split("_")[1])
        self.evolutions_read = set(self.evolutions_read)

        for filname in input_files_write:
            self.evolutions_write.append(os.path.basename(filname).split("_")[1])
        self.evolutions_write = set(self.evolutions_write)

        for evolution in self.evolutions_read:
            input_files_read_evo = Path(input_dir).glob(
                "ScalabilityEvolutionExperiment_"+str(evolution)+"_ScalabilityExperiment_*_ResponsivenessJitterThroughputExperiment_read.csv"
            )
            read_dataframes_evo = [
                pd.read_csv(e_path) for e_path in input_files_read_evo if e_path.is_file()
            ]
            if len(read_dataframes_evo) != int(evolution) :
                raise ValueError(
                    f"Number of dataframes for evolution {evolution} is not equal to the number of clients for read."
                )
            self.read_dataframes.append(read_dataframes_evo)

        for evolution in self.evolutions_write:
            input_files_write_evo = Path(input_dir).glob(
                "ScalabilityEvolutionExperiment_"+str(evolution)+"_ScalabilityExperiment_*_ResponsivenessJitterThroughputExperiment_write.csv"
            )
            write_dataframes_evo = [
                pd.read_csv(e_path) for e_path in input_files_write_evo if e_path.is_file()
            ]
            if len(write_dataframes_evo) != int(evolution) :
                raise ValueError(
                    f"Number of dataframes for evolution {evolution} is not equal to the number of clients for write."
                )
            self.write_dataframes.append(write_dataframes_evo)


        if len(self.read_dataframes) == 0 and len(self.write_dataframes) == 0:
            raise ValueError(
                f"No response time results (neither read nor write) in the experiment folder. Make sure to run the experiment first."
            )

    def __analyze_dataframe(self, frame):
        frame["responsiveness"] = frame["end_time"] - frame["start_time"]  # in seconds
        frame["throughput"] = frame["data_size"] / frame["responsiveness"]  # in bytes/s

        return (
            frame.responsiveness.mean(),
            frame.responsiveness.std(),
            frame.throughput.mean(),
            frame.throughput.std(),
        )

    def generate(self):
        """ """
        summary = {}

        for evolution in range(len(self.evolutions_read)):  # for each group of nclient in parallel
            read_responsivenesses = []
            read_jitters = []
            read_throughput_means = []
            read_throughput_stds = []

            write_responsivenesses = []
            write_jitters = []
            write_throughput_means = []
            write_throughput_stds = []

            if len(self.read_dataframes) != 0:
                for read_dataframe in self.read_dataframes[evolution]:
                    (
                        resp_mean,
                        jitter_mean,
                        through_mean,
                        through_std,
                    ) = self.__analyze_dataframe(read_dataframe)
                    read_responsivenesses.append(resp_mean)
                    read_jitters.append(jitter_mean)
                    read_throughput_means.append(through_mean)
                    read_throughput_stds.append(through_std)

                read_summary = {
                    "responsiveness_mean": np.mean(read_responsivenesses),
                    "jitter_mean": np.mean(read_jitters),
                    "throughput_mean": np.mean(read_throughput_means),
                    "throughput_mean_std": np.mean(read_throughput_stds),
                }
                summary[str("read_mode_" + str(len(self.read_dataframes[evolution])))] = read_summary

                if len(self.write_dataframes) != 0:
                    for write_dataframe in self.write_dataframes[evolution]:
                        (
                            resp_mean,
                            jitter_mean,
                            through_mean,
                            through_std,
                        ) = self.__analyze_dataframe(write_dataframe)
                        write_responsivenesses.append(resp_mean)
                        write_jitters.append(jitter_mean)
                        write_throughput_means.append(through_mean)
                        write_throughput_stds.append(through_std)

                    write_summary = {
                        "responsiveness_mean": np.mean(write_responsivenesses),
                        "jitter_mean": np.mean(write_jitters),
                        "throughput_mean": np.mean(write_throughput_means),
                        "throughput_mean_std": np.mean(write_throughput_stds),
                    }
                    summary[str("write_mode_" + str(len(self.read_dataframes[evolution])))] = write_summary

        output_dir = Path(f"data/{self.experiment_name}/results")
        output_file = output_dir / "scalability_Evolution_summary.json"
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=4)
        print(f"\t➡️ Analysis written to {str(output_file)}")
