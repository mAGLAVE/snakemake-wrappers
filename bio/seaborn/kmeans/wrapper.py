#!/usr/bin/python3.8
# conding: utf-8


"""
This wrapper performs k-means clustering of a counts dataframe

Keep sample names as column names, and rows for each gene expression

This wrapper uses actor-oriented programming scheme to spread the k-means
clustering through multiple threads
"""


__author__ = "Thibault Dayris"
__copyright__ = "Copyright 2021, Thibault Dayris"
__email__ = "thibault.dayris@gustaveroussy.fr"
__license__ = "MIT"


import csv  # Parse tsv/csv files
import logging  # Logging behaviour
import numpy  # Handle large arrays
import os.path  # Handle system related paths
import pandas  # Handle large matrices
import pykka  # Acror oriented programming model
import sklearn  # Regressions and machine learning
import seaborn  # Handle nice plots

import matplotlib.pyplot  # Handle python plots
import scipy.spatial.distance  # Handle distance matrices computations
import sklearn.cluster  # Handle K-Means clustering
import sklearn.decomposition  # Handle dimensional reductions

from typing import Any, Optional, Union  # Type hints for developpers

PCA_type = tuple[Union[pandas.DataFrame, numpy.array]]

# Set logging behaviour
try:
    # Case user provided logging file
    logging.basicConfig(
        filename=snakemake.log[0],
        filemode="w",
        level=logging.DEBUG
    )
except IndexError:
    # Case user did not provide any logging file
    logging.basicConfig(filemode="w", level=logging.DEBUG)
logging.getLogger('pykka').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)


# Clustering class for KMeans
class Pykkmeans(pykka.ThreadingActor):
    """
    This is the Clustering actor. It takes a distance matrix, saves a scatter
    plot of the kmean result given a number of clusters and an output path,
    then return a distortion metric for future elbow graph.
    """
    def __init__(
            self,
            out_prefix: str,
            kparams: dict[str, Any],
            dparams: dict[str, Any],
            sparams: dict[str, Any]
        ):
        super().__init__()
        self.out_prefix = out_prefix
        self.kmeans_params = kparams
        self.distance_params = dparams
        self.scatter_params = sparams


    def on_start(self):
        """
        Logging method automatically called on start
        """
        logging.debug("%s: Starting a Pykkmeans actor", self)


    def on_stop(self) -> None:
        """
        Logging method automatically called on stop
        """
        logging.debug("%s: Stopping a Pykkmeans actor", self)


    def on_failure(self) -> None:
        self.stop()


    def clusterize(
            self,
            distance_matrix: pandas.DataFrame,
            pca: pandas.DataFrame,
            cluster_nb: int,
        ) -> numpy.array:
        """
        Perform the actual actor clustering work
        """
        logging.info(
            "%s: Working on kmeans with %s clusters", self, str(cluster_nb)
        )

        kmeans_cls = sklearn.cluster.KMeans(
            n_clusters=cluster_nb, **self.kmeans_params
        )

        kmeans_transform = kmeans_cls.fit_transform(distance_matrix)
        logging.debug("Kmeans results: %s", str(kmeans_transform))
        pca["predicted_label"] = kmeans_cls.labels_
        distance_matrix["predicted_label"] = kmeans_cls.labels_
        logging.debug(
            "%s: Head of clustering results:\n%s", self, distance_matrix.head()
        )

        distance_matrix.to_csv(
            f"{self.out_prefix}.{cluster_nb}.distance_matrix.tsv",
            sep="\t",
            index=True,
            header=True
        )
        logging.debug(
            "%s: Annotated distance matrix saved at %s",
            self,
            f"{self.out_prefix}.{cluster_nb}.distance_matrix.tsv"
        )
        del distance_matrix["predicted_label"]

        # Save clustered distance matrix
        scatterplot(
            dataframe=pca,
            out_png=f"{self.out_prefix}.{cluster_nb}.scatter.png",
            title=f"PCA: PC{ax1} ({variance[0]:.2f}%) / PC{ax2} ({variance[1]:.2f}%)",
            hue="predicted_label",
            palette="Paired",
            **self.scatter_params
        )
        logging.debug(
            "%s: Annotated satterplot saved at %s",
            self,
            f"{self.out_prefix}.{cluster_nb}.scatter.png"
        )

        # Return distortion value for further elbow plot
        return kmeans_cls.inertia_


def load_dataframe(
        xsv: str,
        *args: list[Any],
        **kwargs: dict[str, Any]
    ) -> pandas.DataFrame:
    """Load count dataframe"""
    # Guessing table format (csv, tsv, scsv, ...)
    with open(xsv, "r") as table:
        dialect = csv.Sniffer().sniff(table.readline())
        logging.debug(f"Detected dialect: {dialect.delimiter}")

    # Actually load dataframe
    data = pandas.read_csv(xsv, sep=dialect.delimiter, *args, **kwargs)

    # Removing duplicates and non-numeric data
    data = data[list(data.select_dtypes(include=[numpy.number]).columns.values)]
    data.dropna(axis=1, how='all', inplace=True)

    logging.debug("Head of input dataframe:\n%s", data.head())

    return data


def compute_distance_matrix(
        counts: pandas.DataFrame,
        *args: Optional[list[Any]],
        **kwargs: Optional[dict[str, Any]]
    ) -> pandas.DataFrame:
    """
    Compute distance matrix

    Euclidian distance should be used for KMeans
    """
    distance_array = scipy.spatial.distance.pdist(
        counts, *args, **kwargs
    )
    distance_matrix = pandas.DataFrame.from_records(
        scipy.spatial.distance.squareform(distance_array)
    )
    distance_matrix.columns = counts.index.tolist()
    distance_matrix.index = counts.index
    logging.debug("Distance matrix:\n%s", distance_matrix.head())

    return distance_matrix



def PCA(counts: pandas.DataFrame) -> PCA_type:
    """
    Use PCA to reduce dimensions

    Why PCA ? I need a multidimentional scaling for fit a n-domension matrix
    into a 2 domensions space. Taking euclidian distance
    """
    # Perform PCA
    nbc = len(counts.columns.tolist())
    skpca = sklearn.decomposition.PCA(n_components=nbc)

    # Transforms result to make them readable
    sktransform = skpca.fit_transform(counts.T)
    skvar = skpca.explained_variance_ratio_

    results = pandas.DataFrame(
        sktransform,
        columns=[f"PC{i}" for i in range(1, nbc+1, 1)],
        index=counts.columns.tolist()
    )

    logging.debug("Head of PCA results:\n%s", results.head())
    logging.debug("Head of explained variants:\n%s", skvar[:5])

    return results, skvar


def reduce_dimensions(
        pca: pandas.DataFrame,
        variance: numpy.array,
        ax1: str,
        ax2: str
    ) -> PCA_type:
    """
    Return a subset of the pca and variance data on given axes
    """
    var = numpy.array(
        [variance[int(ax1) - 1] * 100, variance[int(ax2) - 1] * 100]
    )
    xy = pca[[f"PC{str(ax1)}", f"PC{str(ax2)}"]]

    return xy, var



def scatterplot(
        dataframe: pandas.DataFrame,
        out_png: str,
        title: str,
        **kwargs: dict[str, Any]
    ) -> None:
    """Plots a scatterplot of the given dataframe"""
    seaborn.scatterplot(data=dataframe, **kwargs)
    matplotlib.pyplot.title(title)
    matplotlib.pyplot.savefig(out_png, bbox_inches="tight")
    matplotlib.pyplot.clf()
    logging.debug(f"{out_png} saved")


def heatmap(
        dataframe: pandas.DataFrame,
        out_png: str,
        title: str,
        **kwargs: dict[str, Any]
    ) -> None:
    """Plots a heatmap of the given dataframe"""
    cmap = seaborn.diverging_palette(
        h_neg=240,
        h_pos=10,
        as_cmap=True
    )
    seaborn.heatmap(data=dataframe, cmap=cmap, **kwargs)
    matplotlib.pyplot.title(title)
    matplotlib.pyplot.savefig(out_png, bbox_inches="tight")
    matplotlib.pyplot.clf()
    logging.debug(f"{out_png} saved")


def clusterize(
        pool_size: int,
        max_cluster: int,
        distance_matrix: pandas.DataFrame,
        pca: pandas.DataFrame,
        output_prefix: str,
        kmeans_params: dict[str, Any],
        distance_params: dict[str, Any],
        scatter_params: dict[str, Any]
    ) -> dict[str, float]:
    """Run multi-actor K-Means clustering"""
    logging.info("Starting K-Means clustering")
    actors = [
        Pykkmeans.start(
            out_prefix=output_prefix,
            kparams=kmeans_params,
            dparams=distance_params,
            sparams=scatter_params
        ).proxy()
        for _ in range(pool_size)
    ]

    hosts = [
        actors[idx % len(actors)].clusterize(
            distance_matrix=distance_matrix.copy(),
            pca=pca.copy(),
            cluster_nb=cluster
        )
        for idx, cluster in enumerate(range(2, max_cluster + 1))
    ]

    distortions = dict(zip(range(1, max_cluster), pykka.get_all(hosts)))
    logging.info(str(distortions))
    pykka.ActorRegistry.stop_all()

    return distortions


try:
    counts = load_dataframe(
        snakemake.input["counts"],
        **snakemake.params.get("read_csv", {})
    )
    distance_matrix = compute_distance_matrix(
        counts.T, **snakemake.params.get("distance_params", {})
    )

    if (outdm := snakemake.output.get("distance_tsv", None)) is not None:
        distance_matrix.to_csv(outdm, sep="\t")
        logging.debug("Distance matrix saved as TSV")

    ax1, ax2 = snakemake.params.get("axes", [1, 2])
    pca, variance = PCA(counts)
    pca, variance = reduce_dimensions(pca, variance, ax1, ax2)


    if (outuscat := snakemake.output.get("distance_scatter", None)) is not None:
        scatterplot(
            dataframe=pca,
            out_png=outuscat,
            title=f"PCA: PC{ax1} ({variance[0]:.2f}%) / PC{ax2} ({variance[1]:.2f}%)",
            x=f"PC{ax1}",
            y=f"PC{ax2}"
        )

    if (outuheat := snakemake.output.get("distance_heatmap", None)) is not None:
        heatmap(
            dataframe=distance_matrix,
            out_png=outuheat,
            title="Heatmap of the unclusterized distance matrix",
            robust=True,
            square=True
        )

    outp = os.path.commonprefix(snakemake.output["kmeans"])[:-1]
    logging.debug("All KMeans will have the following output prefix: %s", outp)
    distortions = clusterize(
        pool_size=snakemake.threads,
        max_cluster=snakemake.params.get("max_cluster", 5),
        distance_matrix=distance_matrix,
        pca=pca,
        output_prefix=outp,
        kmeans_params=snakemake.params.get("kmeans_params", {}),
        distance_params=snakemake.params.get("distance_matrix", {}),
        scatter_params=dict(x=f"PC{ax1}", y=f"PC{ax2}")
    )
    distortions = pandas.DataFrame.from_dict(distortions, orient="index")
    distortions.reset_index(inplace=True)
    distortions.columns = ["cluster", "inertia"]
    logging.debug("K-Mmeans are over:\n%s", distortions)

    if (outelbow := snakemake.output.get("elbow", None)) is not None:
        seaborn.lineplot(data=distortions, x="cluster", y="inertia")
        matplotlib.pyplot.title('The Elbow Method showing the optimal k')
        matplotlib.pyplot.savefig(outelbow, bbox_inches="tight")
        matplotlib.pyplot.clf()
        logging.debug(f"{outelbow} saved")
except Exception as e:
    logging.error(e)
    raise