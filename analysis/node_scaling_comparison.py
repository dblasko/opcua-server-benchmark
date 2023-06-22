from turtle import width
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.gridspec as gridspec
import seaborn as sns
import json, glob, os


def __parse_node_nb(string):
    if string == "singlenode":
        return 1
    else:
        string = string.removeprefix("multinode")
        return 63 if string == "ALL" else int(string)


def __load_session_data(experiment_prefix):
    data_files = glob.glob(
        f"{experiment_prefix}*/results/response_times_summary.json", recursive=True
    )
    experiment_summaries = {}
    for file in data_files:
        with open(file, "r") as f:
            content = json.load(f)
            content = content["read_mode"]
        experiment_name = file.split("/")[1]
        content["movement"] = experiment_name.split("_")[-1] == "movementon"
        content["nodes_read"] = __parse_node_nb(experiment_name.split("_")[3])
        experiment_summaries[file.split("/")[1]] = content
    summary_data = pd.DataFrame(experiment_summaries.values()).sort_values(
        by=["movement", "nodes_read"]
    )

    data_files = glob.glob(
        f"{experiment_prefix}*/ResponsivenessJitterThroughputExperiment_read.csv",
        recursive=True,
    )
    experiment_details = {}
    for file in data_files:
        experiment_name = file.split("/")[1]
        experiment_details[experiment_name] = pd.read_csv(file)
        experiment_details[experiment_name]["movement"] = (
            experiment_name.split("_")[-1] == "movementon"
        )
        experiment_details[experiment_name]["nodes_read"] = __parse_node_nb(
            experiment_name.split("_")[3]
        )
        experiment_details[experiment_name]["responsiveness"] = (
            experiment_details[experiment_name]["end_time"]
            - experiment_details[experiment_name]["start_time"]
        )  # in seconds
        experiment_details[experiment_name]["throughput"] = (
            experiment_details[experiment_name]["data_size"]
            / experiment_details[experiment_name]["responsiveness"]
        )  # in bytes/s
        experiment_details[experiment_name].drop(
            ["start_time", "end_time", "mode"], axis=1, inplace=True
        )
    detailed_data = pd.concat(experiment_details.values()).sort_values(
        by=["movement", "nodes_read"]
    )

    return (experiment_summaries, summary_data, experiment_details, detailed_data)


if __name__ == "__main__":
    # Read in data
    EXPERIMENT_PREFIX = "data/wfl_21_june_"
    (
        experiment_summaries,
        summary_data,
        experiment_details,
        detailed_data,
    ) = __load_session_data(EXPERIMENT_PREFIX)

    # Report on data
    style.use("ggplot")
    matplotlib.rcParams["font.family"] = "serif"

    fig = plt.figure(constrained_layout=True, figsize=(10, 11))
    subfigs = fig.subfigures(
        2, 1, height_ratios=[1.5, 1]
    )  # 2 General sections: summary & details

    for outerind, subfig in enumerate(subfigs.flat):
        subfig.suptitle(
            "Scaling the amount of nodes being read - Summary"
            if outerind == 0
            else "Scaling the amount of nodes being read - Details",
            fontsize="large",
        )
        axs = subfig.subplots(2, 2) if outerind == 0 else subfig.subplots(1, 2)
        for innerind, ax in enumerate(axs.flat):
            # Outerind: section
            # Innerind: subplot in section, ltr reading
            if outerind == 0:
                if innerind == 0:
                    title = "Responsiveness mean evolution"
                    attribute = "responsiveness_mean"
                    attribute_name = "Responsiveness mean (s)"
                elif innerind == 1:
                    title = "Jitter evolution"
                    attribute = "jitter"
                    attribute_name = "Jitter (s)"
                elif innerind == 2:
                    title = "Throughput mean evolution"
                    attribute = "throughput_mean"
                    attribute_name = "Throughput mean (bytes/s)"
                elif innerind == 3:
                    title = "Throughput std. dev. evolution"
                    attribute = "throughput_std"
                    attribute_name = "Throughput std. dev. (bytes/s)"
                ax.set_title(title, fontsize="small")
                for movement in [True, False]:
                    summary_df = summary_data[summary_data["movement"] == movement]
                    idx_vals = summary_df["nodes_read"].unique()
                    vals = summary_df[attribute].values
                    ax.plot(
                        idx_vals,
                        vals,
                        label="Movement on" if movement else "Movement off",
                        marker="o",
                        # alpha=0.6,
                    )
                ax.set(
                    xlabel="Number of nodes",
                    ylabel=attribute_name,
                )

                for x in [ax.xaxis.label, ax.yaxis.label]:
                    x.set_fontsize("x-small")
                ax.tick_params(axis="both", which="major", labelsize="x-small")
                ax.set_xticks(
                    idx_vals,
                    idx_vals,
                    minor=False,
                )
            else:
                if innerind % 2 == 0:
                    metric = "responsiveness"
                else:
                    metric = "throughput"
                p = sns.boxplot(
                    data=detailed_data,
                    y=metric,
                    x="nodes_read",
                    hue="movement",
                    ax=ax,
                    hue_order=[True, False],
                    showfliers=True,
                    flierprops={"marker": "o", "markersize": 1},
                    palette={False: "#1f77b490", True: (0.82, 0.33, 0.24)},
                    linewidth=1,
                )
                p.set(xlabel="Number of nodes", ylabel=f"{metric.capitalize()}")
                if innerind == 0:
                    p.get_legend().remove()
                for patch in ax.artists:
                    fc = patch.get_facecolor()
                    patch.set_facecolor(matplotlib.colors.to_rgba(fc, 0.3))

                ax.set_title(
                    f"{metric.capitalize()} distributions for different amounts of nodes being read",
                    fontsize="small",
                )

                for x in [ax.xaxis.label, ax.yaxis.label]:
                    x.set_fontsize("x-small")
                ax.tick_params(axis="both", which="major", labelsize="x-small")

        if outerind == 0:
            handles, labels = axs[0, 0].get_legend_handles_labels()
            axs[0, 1].legend(
                handles,
                labels,
                loc="upper right",
                ncol=2,
                fontsize="x-small",
                borderpad=0.5,
            )
        else:
            handles, labels = axs[1].get_legend_handles_labels()[0], [
                "Movement on",
                "Movement off",
            ]
            axs[1].legend(
                handles,
                labels,
                loc="upper right",
                ncol=2,
                fontsize="x-small",
                borderpad=0.5,
            )

    # plt.show()
    os.mkdir(f"{EXPERIMENT_PREFIX}NODE_SCALING_RESULT")
    plt.savefig(
        f"{EXPERIMENT_PREFIX}NODE_SCALING_RESULT/node_scaling_summary.png", dpi=350
    )
