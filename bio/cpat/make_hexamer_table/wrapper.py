#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This is the Snakemake Wrapper for CPAT make_hexamer_table.py"""

__author__ = "Thibault Dayris"
__copyright__ = "Copyright 2020, Thibault Dayris"
__email__ = "thibault.dayris@gustaveroussy.fr"
__license__ = "MIT"


from snakemake.shell import shell
log = snakemake.log_fmt_shell(stdout=False, stderr=True)

shell(
    " make_hexamer_tab.py "
    " --cod {snakemake.input.coding} "
    " --noncod {snakemake.input.noncoding} "
    " > {snakemake.output[0]} "
    " {log} "
)