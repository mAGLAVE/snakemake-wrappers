#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Snakemake wrapper for GLeaves translation"""


import allel
import logging

from snakemake.shell import shell
from tempfile import TemporaryDirectory
from typing import Dict, Iterator


def get_sed_command(translation: Dict[str, str]) -> Iterator[str]:
    """Return an iterator of sed commands to avoid too long command lines"""
    cmd = None
    for idx, trans in translation.items():
        from_seq = trans[0]
        to_seq = trans[1]

        try:
            if (from_seq != to_seq) and (to_seq is not None):
                cmd.append(f"s/{from_seq}/{to_seq}/g")
        except AttributeError:
            cmd = [f"s/{from_seq}/{to_seq}/g"]

        if idx % 10 == 0:
            yield cmd
            cmd = None

    yield cmd


def get_bcftools_compression(file: str) -> str:
    """Return the compression argument for BCFtools"""
    if file.endswith("bcf"):
        return "b"
    if file.endswith("gz"):
        return "z"
    return "u"


logging.basicConfig(
    filename=snakemake.log[0],
    filemode="w",
    level=logging.INFO
)

sample = snakemake.wildcards.sample

gleaves_fields = {
        "AC": None,
        "AN": None ,
        "BaseQRankSum": None ,
        "cosmic_coding_ID": None,
        "cosmic_noncoding_ID": None,
        "dbscsnv_ADA_SCORE": None,
        "dbscsnv_RF_SCORE": None,
        "DS": "Kaviar_DS",
        "ExcessHet": None,
        "FS": None,
        "InbreedingCoeff": None ,
        "kg_AFR_AF": "dbNSFP_1000Gp3_AFR_AF" ,
        "kg_AMR_AF": "dbNSFP_1000Gp3_AMR_AF" ,
        "kg_EAS_AF": "dbNSFP_1000Gp3_EAS_AF" ,
        "kg_EUR_AF": "dbNSFP_1000Gp3_EUR_AF" ,
        "kg_SAS_AF": "dbNSFP_1000Gp3_SAS_AF" ,
        "LOF": "LOF" ,
        "MIN_DP": None,
        "MLEAC": None,
        "MLEAF": None,
        "MQ": None,
        "MQRankSum": None,
        "Mutect2_AF": f"{sample}_tumor_AF",
        "OLD_MULTIALLELIC": None,
        "OLD_VARIANT": None,
        "PhastCons":  ,
        "ReadPosRankSum": None,
        "RGQ": None,
        "varkdb_constit": None,
        "varkdb_constit_id": None,
        "varkdb_somatique": None,
        "varkdb_somatique_id": None,
}
if "gleaves_fields" in snakemake.extra.keys():
    gleaves_fields = snakemake.extra["gleaves_fields"]


input_call = snakemake.input["call"]

with TemporaryDirectory() as tempdir:
    bcftools_outtype = get_bcftools_compression(snakemake.input['call'])
    log = snakemake.log_fmt_shell(stdout=False, stderr=True, append=False)

    shell(
        "bcftools view "
        "--threads {snakemake.threads} "
        "--output-type {bcftools_outtype} "
        "{snakemake.input['call']} "
        "> {tempdir}/call.vcf {log}"
    )

    log = snakemake.log_fmt_shell(stdout=True, stderr=True, append=True)
    for sed_cmd in get_sed_command(gleaves_fields):
        shell("sed -i {sed_cmd} {tempdir}/call.vcf {log}")


    bcftools_outtype = get_bcftools_compression(snakemake.output['call'])
    log = snakemake.log_fmt_shell(stdout=False, stderr=True, append=False)

    shell(
        "bcftools view "
        "--threads {snakemake.threads} "
        "--output-type {bcftools_outtype} "
        "{tempdir}/call.vcf "
        "> {snakemake.output['call']} {log}"
    )



outcall = snakemake.output["call"]
if snakemake.output["call"].endswith("gz"):
    min_threads += 1
    outcall = "| gzip -c > {}".format(outcall)
elif snakemake.output["call"].endswith("bcf"):
    min_threads += 1
    outcall = "| bcftools view > {}".format(outcall)
else:
    outcall = "> {}".format(outcall)