#!/usr/bin/python3.8
# conding: utf-8

"""
Rename variant effects from SnpEff to default MafTools
"""

__author__ = "Thibault Dayris"
__copyright__ = "Copyright 2021, Thibault Dayris"
__email__ = "thibault.dayris@gustaveroussy.fr"
__license__ = "MIT"

import logging
import pandas
import numpy
# import snakemake

from snakemake.shell import shell

logging.basicConfig(
    filename=snakemake.log[0],
    filemode="w",
    level=logging.DEBUG
)

# log = snakemake.log_fmt_shell(stdout=False, stderr=True)

accepted_terms = [
    "Frame_Shift_Del",
    "Frame_Shift_Ins",
    "In_Frame_Del",
    "In_Frame_Ins",
    "Missense_Mutation",
    "Nonsense_Mutation",
    "Splice_Site",
    "Synonymous_Variant",
    "5_prime_UTR_variant",
    "3_prime_UTR_variant"
]


translation_dict = {
    "chromosome_number_variation": "Synonymous_Variant",
    "exon_loss_variant": "Splice_Site",
    "frameshift_variant": "Missense_Mutation",
    "stop_gained": "Nonsense_Mutation",
    "stop_lost": "Missense_Mutation",
    "start_lost": "Nonsense_Mutation",
    "splice_acceptor_variant": "Splice_Site",
    "splice_acceptor_variant&intron_variant": "Splice_Site",
    "splice_region_variant&non_coding_transcript_exon_variant": "Splice_Site",
    "splice_region_variant&synonymous_variant": "Splice_Site",
    "splice_donor_variant&intron_variant": "Splice_Site",
    "splice_donor_variant": "Splice_Site",
    "structural_interaction_variant": "Missense_Mutation",
    "rare_amino_acid_variant": "Missense_Mutation",
    "missense_variant": "Missense_Mutation",
    "missense_variant&splice_region_variant": "Splice_Site",
    "disruptive_inframe_insertion": "Frame_Shift_Ins",
    "conservative_inframe_insertion": "In_Frame_Ins",
    "disruptive_inframe_deletion": "Frame_Shift_Del",
    "conservative_inframe_deletion": "In_Frame_Del",
    "5_prime_UTR_truncation+exon_loss_variant": "5_prime_UTR_variant",
    "3_prime_UTR_truncation+exon_loss": "3_prime_UTR_variant",
    "splice_branch_variant": "Splice_Site",
    "splice_region_variant": "Splice_Site",
    "stop_retained_variant": "Nonsense_Mutation",
    "initiator_codon_variant": "Missense_Mutation",
    "synonymous_variant": "Synonymous_Variant",
    "initiator_codon_variant+non_canonical_start_codon": "Missense_Mutation",
    'stop_retained_variant': "Nonsense_Mutation",
    "coding_sequence_variant": "Missense_Mutation",
    "5_prime_UTR_variant": "5_prime_UTR_variant",
    "3_prime_UTR_variant": "3_prime_UTR_variant",
    "5_prime_UTR_premature_start_codon_gain_variant": "5_prime_UTR_variant",
    "upstream_gene_variant": "Synonymous_Variant",
    "downstream_gene_variant": "Synonymous_Variant",
    "TF_binding_site_variant": "Synonymous_Variant",
    "regulatory_region_variant": "Missense_Mutation",
    "miRNA": "Synonymous_Variant",
    "custom": "Synonymous_Variant",
    "sequence_feature": "Missense_Mutation",
    "conserved_intron_variant": "Splice_Site",
    "intron_variant": "Synonymous_Variant",
    "intragenic_variant": "Synonymous_Variant",
    "conserved_intergenic_variant": "Splice_Site",
    "intergenic_region": "Synonymous_Variant",
    "coding_sequence_variant": "Missense_Mutation",
    "non_coding_exon_variant": "Synonymous_Variant",
    "non_coding_transcript_exon_variant": "Synonymous_Variant",
    "nc_transcript_variant": "Synonymous_Variant",
    "gene_variant": "Missense_Mutation",
    "chromosome": "Synonymous_Variant",
    "Variant_Classification": "Variant_Classification",
    "protein_protein_contact": "Missense_Mutation",
    'splice_region_variant&intron_variant': "Splice_Site"
}

logging.debug("Reading MAF file")
df = pandas.read_csv(snakemake.input["maf"], sep="\t", header=0, index_col=None)
logging.debug("Maf file loaded")
df["Variant_Classification"] = [
    translation_dict[v] for v in df["Variant_Classification"]
]
logging.debug("Variant_Classification translated")
df.to_csv(snakemake.output["maf"], sep="\t", index=False)
logging.debug("Variant_Classification translated")

# for idx, (key, value) in enumerate(translation_dict.items()):
#     replacement = "'s/{value}/{key}/g'"
#     if idx == 0:
#         shell("sed {replacement} {snakemake.input.maf} > {snakemake.input.maf}.tmp {log}")
#     else:
#         shell("sed -i {replacement} {snakemake.input.maf}.tmp {log}")
#
# log = snakemake.log_fmt_shell(stdout=True, stderr=True)
# shell("mv -v {snakemake.input.maf}.tmp {snakemake.output.maf} {log}")