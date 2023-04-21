from pathlib import Path
import json

import pandas as pd
import numpy as np


class ScalabilityAnalysis:
    """_summary_"""

    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        input_dir = Path(f"data/{self.experiment_name}/")
        input_files_read = Path(input_dir).glob(
            "ScalabilityExperiment_*_ResponsivenessJitterThroughputExperiment_read.csv"
        )
        input_files_write = Path(input_dir).glob(
            "ScalabilityExperiment_*_ResponsivenessJitterThroughputExperiment_write.csv"
        )

        if not input_dir.exists():
            raise ValueError(
                f"Data directory for the experiment {self.experiment_name}, {input_dir}, does not exist."
            )

        self.read_dataframes = [
            pd.read_csv(e_path) for e_path in input_files_read if e_path.is_file()
        ]
        self.write_dataframes = [
            pd.read_csv(e_path) for e_path in input_files_write if e_path.is_file()
        ]
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

        read_responsivenesses = []
        read_jitters = []
        read_throughput_means = []
        read_throughput_stds = []

        write_responsivenesses = []
        write_jitters = []
        write_throughput_means = []
        write_throughput_stds = []

        if len(self.read_dataframes) != 0:
            for read_dataframe in self.read_dataframes:
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
            summary["read_mode"] = read_summary

        if len(self.write_dataframes) != 0:
            for write_dataframe in self.write_dataframes:
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
            summary["write_mode"] = write_summary

        output_dir = Path(f"data/{self.experiment_name}/results")
        output_file = output_dir / "scalability_summary.json"
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=4)
        print(f"\t➡️ Analysis written to {str(output_file)}")
