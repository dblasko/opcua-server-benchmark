from pathlib import Path
import json

import pandas as pd


class ResponsivenessJitterThroughputAnalysis:
    """Process the results of the ResponsivenessJitterThroughputExperiment."""

    MODE_READ = "read"
    MODE_WRITE = "write"

    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        input_dir = Path(f"data/{self.experiment_name}")
        input_file_read = input_dir / "response_times_read.csv"
        input_file_write = input_dir / "response_times_write.csv"

        if not input_dir.exists():
            raise ValueError(
                f"Data directory for the experiment {self.experiment_name}, {input_dir}, does not exist."
            )
        if not input_file_read.exists() and not input_file_write.exists():
            raise ValueError(
                f"No response time results (neither read nor write) in the experiment folder. Make sure to run the experiment first."
            )

        self.response_times_read = (
            pd.read_csv(input_file_read) if input_file_read.exists() else None
        )
        self.response_times_write = (
            pd.read_csv(input_file_write) if input_file_write.exists() else None
        )

    def __generate_response_times(self, mode):
        """Generate the response time analysis for a given mode.

        Args:
            mode (str): MODE_READ or MODE_WRITE

        Returns:
            dict: result summary
        """
        data = (
            self.response_times_read
            if mode == ResponsivenessJitterThroughputAnalysis.MODE_READ
            else self.response_times_write
        )
        data["responsiveness"] = data["end_time"] - data["start_time"]  # in seconds
        data["throughput"] = data["data_size"] / data["responsiveness"]  # in bytes/s

        responsiveness_mean = data.responsiveness.mean()
        jitter = data.responsiveness.std()
        throughput_mean = data.throughput.mean()
        throughput_std = data.throughput.std()

        return {
            "responsiveness_mean": responsiveness_mean,
            "jitter": jitter,
            "throughput_mean": throughput_mean,
            "throughput_std": throughput_std,
        }

    def generate(self):
        """Generates the analysis results to the result file."""
        summary = {}
        if self.response_times_read is not None:
            read_summary = self.__generate_response_times(
                ResponsivenessJitterThroughputAnalysis.MODE_READ
            )
            summary["read_mode"] = read_summary
        if self.response_times_write is not None:
            write_summary = self.__generate_response_times(
                ResponsivenessJitterThroughputAnalysis.MODE_WRITE
            )
            summary["write_mode"] = write_summary

        output_dir = Path(f"data/{self.experiment_name}/results")
        output_file = output_dir / "response_times_summary.json"
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=4)
        print(f"➡️ Analysis written to {str(output_file)}")


if __name__ == "__main__":
    # Example use
    analysis = ResponsivenessJitterThroughputAnalysis(
        "responsiveness_18-04-2023_15-24-34"
    )
    analysis.generate()
