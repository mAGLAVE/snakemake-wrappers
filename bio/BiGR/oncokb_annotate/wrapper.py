#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

"""
Annotate a VCF with a CSV file from OncoKB
"""

import datetime
import gzip
import logging
import pandas
import numpy
import re

from typing import Any
from snakemake.shell import shell

log = snakemake.log_fmt_shell(stdout=True, stderr=True)

logging.basicConfig(
    filename=snakemake.log[0],
    filemode="w",
    level=logging.DEBUG
)


def open_function(file: str):
    """Return the correct opening function"""
    if file.endswith(".gz"):
        return gzip.open(file, "rb")
    return open(file, "r")


def get_headers(cols: list[str], description: dict[str, Any]) -> str:
    """
    From a list of column name, and an optional list of description,
    build VCF headers.
    """
    colnames = None
    version = 1.0
    name = "oncokb_annotate"
    url = f"github.com/tdayris/snakemake-wrappers/tree/Unofficial/bio/BiGR/{name}/wrapper.py"
    headers = [
        f"""##BiGRCommandLine=<ID={name},CommandLine="{url}",Version={version},Date={datetime.date.today()}>\n"""
    ]
    headers += [
        f"""##INFO=<ID=OncoKB_{key},Number={value["nb"]},Type={value["type"]},Description="{value["desc"]}">\n"""
        for key, value in description.items()
    ]
    return "".join(headers)


def dict_to_info(annot: dict[str, Any]) -> str:
    """Convert dict to VCF INFO annotation tag"""
    res = []
    for key, value in annot.items():
        if isinstance(value, bool):
            res.append(f"OncoKB_{key}")
        elif (value == "") or (value is None):
            continue
        else:
            value = str(value)
            value = value.translate(
                value.maketrans(
                    "-/ ()#,;\\\t\"",
                    "___..n|.___"
                )
            )
            res.append(f"OncoKB_{key}={value}")

    return ";".join(res)


def annotate(line: str, csv: pandas.DataFrame) -> str:
    """
    Annotate a VCF formatted line with OnkoKB
    """
    # Extract transcript if from VCF line (must be annotated with SnpEff!)
    try:
        ensembl_transcript = [
            i.split("=")[-1]
            for i in line[:-1].split("\t")[7].split(";")
            if i.startswith("ANN")
        ][0].split("|")[6].split(".")[0]
    except IndexError:
        logging.error(f"Could not find SnpEff annotation in: {line}")
    else:
        try:
            annot = dict_to_info(csv.loc[ensembl_transcript].to_dict())
            chomp = line[:-1].split("\t")
            if chomp[7] == "":
                chomp[7] = annot
            else:
                chomp[7] += f";{annot}"

            line = "\t".join(chomp) + "\n"
        except KeyError:
            logging.warning(f"No annotation for {ensembl_transcript} from {line}")
            pass

    return line


# Load OncoKB CSV file
logging.info("Loading annotation DB")
csv  = pandas.read_csv(
    snakemake.input["oncokb"],
    sep="\t",
    header=0,
    true_values=["Yes"],
    false_values=["No"]
)
logging.debug(csv.head())
logging.debug(csv.columns.tolist())

# Some characters are not allowed in VCF. They are replaced here.
new_cols = []
for colname in csv .columns.tolist():
    new_cols.append(colname.replace("-", "_")
                           .replace("/", "_")
                           .replace("\\", "_")
                           .replace(' ', '_')
                           .replace("(", "")
                           .replace(")", "")
                           .replace("#", "nb")
                           .replace("\t", "_"))

csv.columns = new_cols
csv.set_index("GRCh38_Isoform", inplace=True)

description = {
    "Hugo_Symbol": {
        "type": "String",
        "nb": "1",
        "desc": "Onco KB Hugo Symbol"
    },
    "Entrez_Gene_ID": {
        "type": "String",
        "nb": "1",
        "desc": "Onco KB Entrez Gene ID"
    },
    "GRCh37_Isoform": {
        "type": "String",
        "nb": "1",
        "desc": "Onco KB Ensembl GRCh37 transcript ID"
    },
    "GRCh37_RefSeq": {
        "type": "String",
        "nb": "1",
        "desc": "Onco KB Refseq ID in GRCh37"
    },
    "GRCh38_RefSeq": {
        "type": "String",
        "nb": "1",
        "desc": "Onco KB Refseq ID in GRCh38"
    },
    "GRCh37_Isoform": {
        "type": "String",
        "nb": "1",
        "desc": "Onco KB Ensembl GRCh38 transcript ID"
    },
    "nb_of_occurrence_within_resources_Column_D_J": {
        "type": "Integer",
        "nb": "1",
        "desc": "Onco KB number of occurrence within resources Column DJ"
    },
    "OncoKB_Annotated": {
        "type": "Flag",
        "nb": "0",
        "desc": "The gene is annotated by OncoKB"
    },
    "Is_Oncogene": {
        "type": "Flag",
        "nb": "0",
        "desc": "The gene is annotated as an oncogene by OncoKB"
    },
    "Is_Tumor_Suppressor_Gene": {
        "type": "Flag",
        "nb": "0",
        "desc": "The gene is annotated as tumor suppressor by OncoKB"
    },
    "MSK_IMPACT": {
        "type": "Flag",
        "nb": "0",
        "desc": "Gene has OncoKB integrated mutation profiling of actionable cancer targets"
    },
    "MSK_HEME": {
        "type": "Flag",
        "nb": "0",
        "desc": "Gene has OncoKB integrated mutation profiling of actionable cancer targets within blood"
    },
    "FOUNDATION_ONE": {
        "type": "Flag",
        "nb": "0",
        "desc": "The gene is annotated by OncoKB as belonging to FoundationOne CDx"
    },
    "FOUNDATION_ONE_HEME": {
        "type": "Flag",
        "nb": "0",
        "desc": "The gene is annotated by OncoKB as belonging to FoundationOne CDx, blood samples"
    },
    "Vogelstein": {
        "type": "Flag",
        "nb": "0",
        "desc": "The gene is annotated by OncoKB as belonging Vogelstein 2013 publication"
    },
    "SANGER_CGC05_30_2017": {
        "type": "Flag",
        "nb": "0",
        "desc": "The gene is annotated by OncoKB as belonging to Cancer Gene Sensus"
    }
}

# Annotating input VCF
logging.debug("Opening VCFs")
if str(snakemake.output["vcf"]).endswith("vcf.gz"):
    out_vcf = snakemake.output["vcf"][:-3]
else:
    out_vcf = snakemake.output["vcf"]

with (open_function(snakemake.input["vcf"]) as in_vcf,
      open(out_vcf, 'w') as out_vcf):
    for line in in_vcf:
        if isinstance(line, bytes):
            line = line.decode("utf-8")

        if line.startswith("##"):
            pass

        elif line.startswith("#"):
            new_headers = get_headers(
                csv .columns.tolist(),
                description
            )
            line = new_headers + line
            logging.info("Header modified")

        else:
            line = annotate(line, csv)

        out_vcf.write(line)

if str(snakemake.output["vcf"]).endswith("vcf.gz"):
    logging.info(f"Compressing {out_vcf}")
    shell("pbgzip -c {out_vcf} > {snakemake.output['vcf']} 2> {log}")
    logging.info(f"Indexing {snakemake.output['call']}")
    shell("tabix -p vcf {snakemake.output['vcf']} >> {log} 2>&1")
    logging.info(f"Removing temporary file {out_vcf}")
    shell("rm --verbose {out_vcf} >> {log} 2>&1")