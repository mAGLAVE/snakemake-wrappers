#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

"""
Rename splitted vcf columns
"""

import pandas
import logging

logging.basicConfig(
    filename=snakemake.log[0],
    filemode="w",
    level=logging.DEBUG
)

def get_variant_type(ref: str, alt: str) -> str:
    """
    Return variant type given the reference and the alternative alleles
    """
    if ref == ".": # Nothing in REF, added in ALT
        return "INS"
    if alt == ".":
        return "DEL" # Something in REF, nothing in ALT

    if len(ref) == 1:
        if len(alt) == 1:
            return "SNP" # REF and ALT only have one nucleotide
        return "ONP" # REF had less nucleotides than ALT

    if len(ref) == 2:
        if len(alt) == 2:
            return "DNP" # REF and ALT have two nucleotides
        return "ONP" # REF has two nucleotides, ALT have unknown

    if len(ref) == 3:
        if len(alt) == 3:
            return "TNP" # REF and ALT have three nucleotides
        return "ONP" # REF has three nucleotides, ALT have unknown
    return "ONP" # More than 3 nucleotides in ref, unknown in ALT


headers = {
    "CHROM": "Chromosome",
    "POS": "Start_Position",
    "ID": "Variant_ID",
    "REF": "REF",
    "ALT": "ALT",
    "FILTER": "Filter",
    "FORMAT_AD": "Format_Allelic_depths",
    "FORMAT_AF": "Format_Allele_Frequency",
    "FORMAT_DP": "Format_Read_Depth",
    "FORMAT_F1R2": "F1R2_orientation",
    "FORMAT_F2R1": "F2R1_orientation",
    "FORMAT_GQ": "Genotype_quality",
    "FORMAT_GT": "Genotype",
    "FORMAT_PGT": "Physical_phasing_haplotype",
    "FORMAT_PID": "Physical_phasing_ID",
    "FORMAT_PL": "Normalized_Phred_scaled_likelihoods",
    "FORMAT_PS": "Phasing_set",
    "FORMAT_SB": "Strand_bias_Fisher_component",
    'AC': 'AlleleCount',
    'AC_afr': 'AlleleCount_African_Ancestry',
    'AC_afr_female': 'AlleleCount_African_Ancestry_female',
    'AC_afr_male': 'AlleleCount_African_Ancestry_male',
    'AC_ami': 'AlleleCount_Amish_Ancestry',
    'AC_ami_female': 'AlleleCount_Amish_Ancestry_female',
    'AC_ami_male': 'AlleleCount_Amish_Ancestry_male',
    'AC_amr': 'AlleleCount_Latino_Ancestry',
    'AC_amr_female': 'AlleleCount_Latino_Ancestry_female',
    'AC_amr_male': 'AlleleCount_Latino_Ancestry_male',
    'AC_asj': 'AlleleCount_Ashkenazi_Jewish_ancestry',
    'AC_asj_female': 'AlleleCount_Ashkenazi_Jewish_ancestry_female',
    'AC_asj_male': 'AlleleCount_Ashkenazi_Jewish_ancestry_male',
    'AC_eas': 'AlleleCount_East_Asian_ancestry',
    'AC_eas_female': 'AlleleCount_East_Asian_ancestry_female',
    'AC_eas_male': 'AlleleCount_East_Asian_ancestry_male',
    'AC_female': 'AlleleCount_female',
    'AC_fin': 'AlleleCount_Finnish_Ancestry',
    'AC_fin_female': 'AlleleCount_Finnish_Ancestry_female',
    'AC_fin_male': 'AlleleCount_Finnish_Ancestry_male',
    'AC_male': 'AlleleCount_male',
    'AC_nfe': 'AlleleCount_Non_Finnish_Europeans',
    'AC_nfe_female': 'AlleleCount_Non_Finnish_Europeans_female',
    'AC_nfe_male': 'AlleleCount_Non_Finnish_Europeans_male',
    'AC_oth': 'AlleleCount_oth',
    'AC_oth_female': 'AlleleCount_oth_female',
    'AC_oth_male': 'AlleleCount_oth_male',
    'AC_raw': 'AlleleCount_raw',
    'AC_sas': 'AlleleCount_South_Asian_ancestry',
    'AC_sas_female': 'AlleleCount_South_Asian_ancestry_female',
    'AC_sas_male': 'AlleleCount_South_Asian_ancestry_male',
    'AF': 'AlleleFrequency',
    'AF_ESP': 'AlleleFrequency_ESP',
    'AF_EXAC': 'AlleleFrequency_EXAC',
    'AF_TGP': 'AlleleFrequency_TGP',
    'AF_afr': 'AlleleFrequency_African_Ancestry',
    'AF_afr_female': 'AlleleFrequency_African_Ancestry_female',
    'AF_afr_male': 'AlleleFrequency_African_Ancestry_male',
    'AF_ami': 'AlleleFrequency_Amish_Ancestry',
    'AF_ami_female': 'AlleleFrequency_Amish_Ancestry_female',
    'AF_ami_male': 'AlleleFrequency_Amish_Ancestry_male',
    'AF_amr': 'AlleleFrequency_Latino_Ancestry',
    'AF_amr_female': 'AlleleFrequency_Latino_Ancestry_female',
    'AF_amr_male': 'AlleleFrequency_Latino_Ancestry_male',
    'AF_asj': 'AlleleFrequency_Ashkenazi_Jewish_ancestry',
    'AF_asj_female': 'AlleleFrequency_Ashkenazi_Jewish_ancestry_female',
    'AF_asj_male': 'AlleleFrequency_Ashkenazi_Jewish_ancestry_male',
    'AF_eas': 'AlleleFrequency_East_Asian_ancestry',
    'AF_eas_female': 'AlleleFrequency_East_Asian_ancestry_female',
    'AF_eas_male': 'AlleleFrequency_East_Asian_ancestry_male',
    'AF_female': 'AlleleFrequency_female',
    'AF_fin': 'AlleleFrequency_Finnish_Ancestry',
    'AF_fin_female': 'AlleleFrequency_Finnish_Ancestry_female',
    'AF_fin_male': 'AlleleFrequency_Finnish_Ancestry_male',
    'AF_male': 'AlleleFrequency_male',
    'AF_nfe': 'AlleleFrequency_Non_Finnish_Europeans',
    'AF_nfe_female': 'AlleleFrequency_Non_Finnish_Europeans_female',
    'AF_nfe_male': 'AlleleFrequency_Non_Finnish_Europeans_male',
    'AF_oth': 'AlleleFrequency_oth',
    'AF_oth_female': 'AlleleFrequency_oth_female',
    'AF_oth_male': 'AlleleFrequency_oth_male',
    'AF_raw': 'AlleleFrequency_raw',
    'AF_sas': 'AlleleFrequency_South_Asian_ancestry',
    'AF_sas_female': 'AlleleFrequency_South_Asian_ancestry_female',
    'AF_sas_male': 'AlleleFrequency_South_Asian_ancestry_male',
    'AN': 'AlleleNumber',
    'AN_afr': 'AlleleNumber_African_Ancestry',
    'AN_afr_female': 'AlleleNumber_African_Ancestry_female',
    'AN_afr_male': 'AlleleNumber_African_Ancestry_male',
    'AN_ami': 'AlleleNumber_Amish_Ancestry',
    'AN_ami_female': 'AlleleNumber_Amish_Ancestry_female',
    'AN_ami_male': 'AlleleNumber_Amish_Ancestry_male',
    'AN_amr': 'AlleleNumber_Latino_Ancestry',
    'AN_amr_female': 'AlleleNumber_Latino_Ancestry_female',
    'AN_amr_male': 'AlleleNumber_Latino_Ancestry_male',
    'AN_asj': 'AlleleNumber_Ashkenazi_Jewish_ancestry',
    'AN_asj_female': 'AlleleNumber_Ashkenazi_Jewish_ancestry_female',
    'AN_asj_male': 'AlleleNumber_Ashkenazi_Jewish_ancestry_male',
    'AN_eas': 'AlleleNumber_East_Asian_ancestry',
    'AN_eas_female': 'AlleleNumber_East_Asian_ancestry_female',
    'AN_eas_male': 'AlleleNumber_East_Asian_ancestry_male',
    'AN_female': 'AlleleNumber_female',
    'AN_fin': 'AlleleNumber_Finnish_Ancestry',
    'AN_fin_female': 'AlleleNumber_Finnish_Ancestry_female',
    'AN_fin_male': 'AlleleNumber_Finnish_Ancestry_male',
    'AN_male': 'AlleleNumber_male',
    'AN_nfe': 'AlleleNumber_Non_Finnish_Europeans',
    'AN_nfe_female': 'AlleleNumber_Non_Finnish_Europeans_female',
    'AN_nfe_male': 'AlleleNumber_Non_Finnish_Europeans_male',
    'AN_oth': 'AlleleNumber_oth',
    'AN_oth_female': 'AlleleNumber_oth_female',
    'AN_oth_male': 'AlleleNumber_oth_male',
    'AN_raw': 'AlleleNumber_raw',
    'AN_sas': 'AlleleNumber_South_Asian_ancestry',
    'AN_sas_female': 'AlleleNumber_South_Asian_ancestry_female',
    'AN_sas_male': 'AlleleNumber_South_Asian_ancestry_male',
    "AS_FilterStatus": "Mutect2_AS_FilterStatus",
    "AS_SB_TABLE": "Mutect2_Allele_specific_Strand_bias",
    "AS_UNIQ_ALT_READ_COUNT": "Mutect2_Unique_alt_variant_count",
    "CONTQ": "Phred_scaled_qualities_non_contamination",
    "DP": "Mutect2_Read_depth",
    "ECNT": "Mutect2_Events_in_haplotype",
    "GERMQ": "Mutect2_Phred_scaled_quality_non_germline",
    "MBQ": "Mutect2_Median_base_quality",
    "MFRL": "Mutect2_Median_fragment_length",
    "MMQ": "Mutect2_Median_mapping_quality",
    "MPOS": "Mutect2_Median_distance_to_end_read",
    "NALOD": "Mutect2_Negative_log_10_odds_of_artifact",
    "NCount": "Mutect2_Pileup_N_base_depth",
    "NLOD": "Mutect2_Normal_log_10_likelihood_ploïdy",
    "OCM": "Mutect2_Non_matching_original_alignment",
    "PON": "Mutect2_Panel_of_Normal",
    "POPAF": "Mutect2_negative_log_10_population_allele_frequencies",
    "ROQ": "Mutect2_Phred_scaled_qualities_not_orientation_bias",
    "RPA": "Mutect2_Number_tandem_repetition",
    "RU": "Mutect2_Repeat_unit",
    "SEQQ": "Mutect2_Phred_scaled_quality_not_sequencing_error",
    "STR": "Mutect2_Is_short_tandem_repeat",
    "STRANDQ": "Mutect2_Phred_scaled_quality_not_strand_bias",
    "STRQ": "Mutect2_Phred_scaled_quality_not_tandem_polymerase_error",
    "TLOD": "Mutect2_Log_10_likelihood_variant_exists",
    "FORMAT_sample_tumor_AF": "Mutect2_Allele_Frequency",
    "ANN[*].ALLELE": "Allele",
    "ANN[*].EFFECT": "Variant_Classification",
    "ANN[*].IMPACT": "IMPACT",
    "ANN[*].GENE": "Hugo_Symbol",
    "ANN[*].GENEID": "Gene",
    "ANN[*].FEATURE": "Feature",
    "ANN[*].FEATUREID": "Transcript_ID",
    "ANN[*].BIOTYPE": "BIOTYPE",
    "ANN[*].RANK": "Exon_Intron_rank",
    "ANN[*].HGVS_C": "HGVSc",
    "ANN[*].HGVS_P": "HGVSp",
    "ANN[*].CDNA_POS": "cDNA_position",
    "ANN[*].CDNA_LEN": "cDNA_Length",
    "ANN[*].CDS_POS": "CDS_position",
    "ANN[*].CDS_LEN": "CDS_length",
    "ANN[*].AA_POS": "Protein_position",
    "ANN[*].AA_LEN": "Protein_length",
    "ANN[*].DISTANCE": "DISTANCE",
    "ANN[*].ERRORS": "Errors",
    "EFF[*].EFFECT": "SnpEff_Effect",
    "EFF[*].IMPACT": "SnpEff_Impact",
    "EFF[*].FUNCLASS": "SnpEff_FunctionalClass",
    "EFF[*].CODON": "SnpEff_Codon",
    "EFF[*].AA": "SnpEff_AminoAcid",
    "EFF[*].AA_LEN": "SnpEff_AminoAcid_Length",
    "EFF[*].GENE": "SnpEff_Gene_Name",
    "EFF[*].BIOTYPE": "SnpEff_Biotype",
    "EFF[*].CODING": "SnpEff_CodingSequence",
    "EFF[*].TRID": "SnpEff_TranscriptID",
    "EFF[*].RANK": "SnpEff_Rank",
    "LOF[*].GENE": "SnpEff_LOF_GeneName",
    "LOF[*].GENEID": "SnpEff_LOF_GeneID",
    "LOF[*].NUMTR": "SnpEff_LOF_TranscriptNb",
    "LOF[*].PERC": "SnpEff_LOF_PctTrancrtipcsAffected",
    "LOF": "SnpEff_LOF_SnpEff",
    "NMD[*].GENE": "SnpEff_NMD_GeneName",
    "NMD[*].GENEID": "SnpEff_NMD_GeneID",
    "NMD[*].NUMTR": "SnpEff_NMD_TranscriptNb",
    "NMD[*].PERC": "SnpEff_NMD_PctTrancrtipcsAffected",
    "NMD": "SnpEff_NMD_SnpEff",
    "NMD": "SnpEff_Nonsense_mediated_decay",
    "VARTYPE": "SnpEff_Variant_types",
    "SNP": "SnpEff_Is_SNP",
    "MNP": "SnpEff_Is_MNP",
    "INS": "SnpEff_Is_INS",
    "DEL": "SnpEff_Is_DEL",
    "MIXED": "SnpEff_Is_MIXED_Polymorphisms",
    "HOM": "SnpEff_Is_Homozygous",
    "HET": "SnpEff_Is_Heterozygous",
    "MSigDb": "MSigDb_Pathways",
    "Kaviar_AC": "Kaviar_Allele_Count",
    "Kaviar_AF": "Kaviar_Allele_Frequency",
    "Kaviar_AN": "Kaviar_Allele_Number",
    "Kaviar_DS": "Kaviar_Database_Source",
    "Kaviar_END": "Kaviar_End_Position",
    "ExistsInKaviar": "Variant_ExistsInKaviar",
    "dbSNP_CDA": "dbSNP_Clinical_Diagnostic_Assay",
    "dbSNP_OTH": "dbSNP_Orthologous_Variants_in_NCBI",
    "dbSNP_S3D": "dbSNP_Has_known_3D_structure",
    "dbSNP_WTD": "dbSNP_Is_Withdrawn_by_submitter",
    "dbSNP_dbSNPBuildID": "dbSNP_BuildID",
    "dbSNP_SLO": "dbSNP_SubmitterLinkOut",
    "dbSNP_NSF": "dbSNP_Has_Non_Synonymous_Frameshift",
    "dbSNP_R3": "dbSNP_3p_variant",
    "dbSNP_R5": "dbSNP_5p_variant",
    "dbSNP_NSN": "dbSNP_Has_Nonsense_Changes_Stop",
    "dbSNP_NSM": "dbSNP_Has_Nonsense_Changes_Peptide",
    "dbSNP_G5A": "dbSNP_Less_5pct_population",
    "dbSNP_COMMON": "dbSNP_Is_common_variant",
    "dbSNP_RS": "dbSNP_RS_id",
    "dbSNP_RV": "dbSNP_Variant_is_reversed",
    "dbSNP_TPA": "dbSNP_Third_party_annotation",
    "dbSNP_CFL": "dbSNP_Has_assembly_conflict",
    "dbSNP_GNO": "dbSNP_Has_Available_genotype",
    "dbSNP_VLD": "dbSNP_Is_Validated",
    "dbSNP_ASP": "dbSNP_Is_Assembly_Specific",
    "dbSNP_ASS": "dbSNP_Acceptor_splice_variant",
    "dbSNP_REF": "dbSNP_Variant_identical_to_reference",
    "dbSNP_U3": "dbSNP_3p_UTR_variant",
    "dbSNP_U5": "dbSNP_5p_UTR_variant",
    "dbSNP_TOPMED": "dbSNP_AF_in_TopMed_db",
    "dbSNP_WGT": "dbSNP_Weight",
    "dbSNP_MTP": "dbSNP_Microattribution_TPA",
    "dbSNP_LSD": "dbSNP_Locus_specific_database",
    "dbSNP_NOC": "dbSNP_Contig_not_in_variant_list",
    "dbSNP_DSS": "dbSNP_Donor_splice_varianP",
    "dbSNP_SYN": "dbSNP_Synonymous_variant",
    "dbSNP_KGPhase3": "dbSNP_1000genome_p3",
    "dbSNP_CAF": "dbSNP_Alleles_in_1000g",
    "dbSNP_VC": "dbSNP_Variant_class",
    "dbSNP_MUT": "dbSNP_Is_cited",
    "dbSNP_KGPhase1": "dbSNP_1000genome_p1",
    "dbSNP_NOV": "dbSNP_Non_Overlapping_Alleles",
    "dbSNP_VP": "dbSNP_Variant_property",
    "dbSNP_SAO": "dbSNP_Variant_Origin",
    "dbSNP_GENEINFO": "dbSNP_Gene_info",
    "dbSNP_INT": "dbSNP_Is_Intronic",
    "dbSNP_G5": "dbSNP_MAF_Over_5pct",
    "dbSNP_OM": "dbSNP_Has_OMIM_OMIA",
    "dbSNP_PMC": "dbSNP_Pubmed",
    "dbSNP_SSR": "dbSNP_Suspect_reason_code",
    "dbSNP_RSPOS": "dbSNP_Position_dbSNP",
    "dbSNP_HD": "dbSNP_High_density_genotyping_kit_dbGaP",
    "dbSNP_PM": "dbSNP_Variant_Precious",
    "ExistsInDBsnp": "Variant_ExistsInDBsnp",
    "cosmic_CDS": "Cosmic_CDS_Annotation",
    "cosmic_AA": "Cosmic_AA_Annotation",
    "cosmic_GENE": "Cosmic_Gene_Name",
    "cosmic_CNT": "Cosmic_Sample_Number",
    "cosmic_SNP": "Cosmic_Is_SNP",
    "cosmic_STRAND": "Cosmic_Gene_Strand",
    "ExistsInCosmic": "Variant_ExistsInCosmic",
    'dbNSFP_ExAC_nonTCGA_SAS_AF': 'dbNSFP_ExAC_nonTCGA_South_Asian_ancestry_AlleleFrequency',
    'dbNSFP_DEOGEN2_pred': 'dbNSFP_DEOGEN2_pred',
    'dbNSFP_clinvar_var_source': 'dbNSFP_clinvar_var_source',
    'dbNSFP_ExAC_SAS_AF': 'dbNSFP_ExAC_South_Asian_ancestry_AlleleFrequency',
    'dbNSFP_GERP___RS': 'dbNSFP_GERP___RS',
    'dbNSFP_ExAC_SAS_AC': 'dbNSFP_ExAC_South_Asian_ancestry_AlleleCount',
    'dbNSFP_HGVSp_ANNOVAR': 'dbNSFP_HGVSp_ANNOVAR',
    'dbNSFP_aaalt': 'dbNSFP_AlternativeAminoAcid',
    'dbNSFP_H1_hESC_fitCons_rankscore': 'dbNSFP_H1_hESC_fitCons_rankscore',
    'dbNSFP_gnomAD_exomes_controls_AMR_AC': 'dbNSFP_gnomAD_exomes_controls_Latino_Ancestry_AlleleCount',
    'dbNSFP_gnomAD_exomes_controls_AMR_AF': 'dbNSFP_gnomAD_exomes_controls_Latino_Ancestry_AlleleFrequency',
    'dbNSFP_1000Gp3_EAS_AC': 'dbNSFP_1000Gp3_East_Asian_ancestry_AlleleCount',
    'dbNSFP_MetaSVM_pred': 'dbNSFP_MetaSVM_pred',
    'dbNSFP_ExAC_nonTCGA_SAS_AC': 'dbNSFP_ExAC_nonTCGA_South_Asian_ancestry_AlleleCount',
    'dbNSFP_M_CAP_score': 'dbNSFP_M_CAP_score',
    'dbNSFP_MutationAssessor_rankscore': 'dbNSFP_MutationAssessor_rankscore',
    'dbNSFP_Aloft_Confidence': 'dbNSFP_Aloft_Confidence',
    'dbNSFP_ExAC_nonpsych_NFE_AF': 'dbNSFP_ExAC_nonpsych_Non_Finnish_Europeans_AlleleFrequency',
    'dbNSFP_gnomAD_genomes_NFE_AN': 'dbNSFP_gnomAD_genomes_Non_Finnish_Europeans_AlleleNumber',
    'dbNSFP_ExAC_nonpsych_NFE_AC': 'dbNSFP_ExAC_nonpsych_Non_Finnish_Europeans_AlleleCount',
    'dbNSFP_1000Gp3_EAS_AF': 'dbNSFP_1000Gp3_East_Asian_ancestry_AlleleFrequency',
    'dbNSFP_Aloft_prob_Tolerant': 'dbNSFP_Aloft_prob_Tolerant',
    'dbNSFP_LRT_converted_rankscore': 'dbNSFP_LRT_converted_rankscore',
    'dbNSFP_gnomAD_genomes_AMI_nhomalt': 'dbNSFP_gnomAD_genomes_Amish_Ancestry_HomozygousIndividuals',
    'dbNSFP_APPRIS': 'dbNSFP_APPRIS',
    'dbNSFP_ExAC_FIN_AC': 'dbNSFP_ExAC_Finnish_Ancestry_AlleleCount',
    'dbNSFP_PrimateAI_rankscore': 'dbNSFP_PrimateAI_rankscore',
    'dbNSFP_fathmm_MKL_coding_pred': 'dbNSFP_fathmm_MKL_coding_pred',
    'dbNSFP_gnomAD_genomes_NFE_AF': 'dbNSFP_gnomAD_genomes_Non_Finnish_Europeans_AlleleFrequency',
    'dbNSFP_fathmm_MKL_coding_score': 'dbNSFP_fathmm_MKL_coding_score',
    'dbNSFP_ExAC_FIN_AF': 'dbNSFP_ExAC_Finnish_Ancestry_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_controls_ASJ_AN': 'dbNSFP_gnomAD_exomes_controls_Ashkenazi_Jewish_ancestry_AlleleNumber',
    'dbNSFP_ESP6500_EA_AC': 'dbNSFP_ESP6500_EA_AlleleCount',
    'dbNSFP_gnomAD_exomes_SAS_nhomalt': 'dbNSFP_gnomAD_exomes_South_Asian_ancestry_HomozygousIndividuals',
    'dbNSFP_gnomAD_exomes_controls_ASJ_AC': 'dbNSFP_gnomAD_exomes_controls_Ashkenazi_Jewish_ancestry_AlleleCount',
    'dbNSFP_gnomAD_genomes_NFE_AC': 'dbNSFP_gnomAD_genomes_Non_Finnish_Europeans_AlleleCount',
    'dbNSFP_FATHMM_score': 'dbNSFP_FATHMM_score',
    'dbNSFP_gnomAD_genomes_FIN_AC': 'dbNSFP_gnomAD_genomes_Finnish_Ancestry_AlleleCount',
    'dbNSFP_gnomAD_exomes_controls_ASJ_AF': 'dbNSFP_gnomAD_exomes_controls_Ashkenazi_Jewish_ancestry_AlleleFrequency',
    'dbNSFP_gnomAD_genomes_FIN_AF': 'dbNSFP_gnomAD_genomes_Finnish_Ancestry_AlleleFrequency',
    'dbNSFP_ExAC_nonTCGA_FIN_AC': 'dbNSFP_ExAC_nonTCGA_Finnish_Ancestry_AlleleCount',
    'dbNSFP_ExAC_nonpsych_FIN_AC': 'dbNSFP_ExAC_nonpsych_Finnish_Ancestry_AlleleCount',
    'dbNSFP_gnomAD_exomes_EAS_nhomalt': 'dbNSFP_gnomAD_exomes_East_Asian_ancestry_HomozygousIndividuals',
    'dbNSFP_phastCons17way_primate': 'dbNSFP_phastCons17way_primate',
    'dbNSFP_ExAC_nonTCGA_FIN_AF': 'dbNSFP_ExAC_nonTCGA_Finnish_Ancestry_AlleleFrequency',
    'dbNSFP_LRT_score': 'dbNSFP_LRT_score',
    'dbNSFP_Ancestral_allele': 'dbNSFP_Ancestral_allele',
    'dbNSFP_ESP6500_EA_AF': 'dbNSFP_ESP6500_EA_AlleleFrequency',
    'dbNSFP_gnomAD_genomes_FIN_AN': 'dbNSFP_gnomAD_genomes_Finnish_Ancestry_AlleleNumber',
    'dbNSFP_MutPred_rankscore': 'dbNSFP_MutPred_rankscore',
    'dbNSFP_ExAC_nonpsych_FIN_AF': 'dbNSFP_ExAC_nonpsych_Finnish_Ancestry_AlleleFrequency',
    'dbNSFP_gnomAD_genomes_FIN_nhomalt': 'dbNSFP_gnomAD_genomes_Finnish_Ancestry_HomozygousIndividuals',
    'dbNSFP_GENCODE_basic': 'dbNSFP_GENCODE_basic',
    'dbNSFP_PrimateAI_pred': 'dbNSFP_PrimateAI_pred',
    'dbNSFP_bStatistic_converted_rankscore': 'dbNSFP_bStatistic_converted_rankscore',
    'dbNSFP_HUVEC_confidence_value': 'dbNSFP_HUVEC_confidence_value',
    'dbNSFP_H1_hESC_confidence_value': 'dbNSFP_H1_hESC_confidence_value',
    'dbNSFP_gnomAD_genomes_SAS_AC': 'dbNSFP_gnomAD_genomes_South_Asian_ancestry_AlleleCount',
    'dbNSFP_GTEx_V8_tissue': 'dbNSFP_GTEx_V8_tissue',
    'dbNSFP_gnomAD_genomes_nhomalt': 'dbNSFP_gnomAD_genomes_HomozygousIndividuals',
    'dbNSFP_Eigen_PC_phred_coding': 'dbNSFP_Eigen_PC_phred_coding',
    'dbNSFP_Ensembl_geneid': 'dbNSFP_Ensembl_geneid',
    'dbNSFP_gnomAD_genomes_SAS_AF': 'dbNSFP_gnomAD_genomes_South_Asian_ancestry_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_NFE_AC': 'dbNSFP_gnomAD_exomes_Non_Finnish_Europeans_AlleleCount',
    'dbNSFP_HGVSc_VEP': 'dbNSFP_HGVSc_VEP',
    'dbNSFP_gnomAD_exomes_nhomalt': 'dbNSFP_gnomAD_exomes_HomozygousIndividuals',
    'dbNSFP_gnomAD_genomes_SAS_AN': 'dbNSFP_gnomAD_genomes_South_Asian_ancestry_AlleleNumber',
    'dbNSFP_HGVSp_snpEff': 'dbNSFP_HGVSp_snpEff',
    'dbNSFP_PROVEAN_pred': 'dbNSFP_PROVEAN_pred',
    'dbNSFP_gnomAD_exomes_controls_AMR_AN': 'dbNSFP_gnomAD_exomes_controls_Latino_Ancestry_AlleleNumber',
    'dbNSFP_phastCons100way_vertebrate': 'dbNSFP_phastCons100way_vertebrate',
    'dbNSFP_MetaSVM_score': 'dbNSFP_MetaSVM_score',
    'dbNSFP_gnomAD_exomes_controls_AFR_AF': 'dbNSFP_gnomAD_exomes_controls_AFR_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_controls_AFR_AC': 'dbNSFP_gnomAD_exomes_controls_AFR_AlleleCount',
    'dbNSFP_gnomAD_genomes_AMI_AF': 'dbNSFP_gnomAD_genomes_Amish_Ancestry_AlleleFrequency',
    'dbNSFP_Denisova': 'dbNSFP_Denisova',
    'dbNSFP_refcodon': 'dbNSFP_refcodon',
    'dbNSFP_clinvar_id': 'dbNSFP_clinvar_id',
    'dbNSFP_gnomAD_exomes_controls_AFR_AN': 'dbNSFP_gnomAD_exomes_controls_AFR_AlleleNumber',
    'dbNSFP_ESP6500_AA_AF': 'dbNSFP_ESP6500_AA_AlleleFrequency',
    'dbNSFP_M_CAP_pred': 'dbNSFP_M_CAP_pred',
    'dbNSFP_gnomAD_genomes_AMI_AN': 'dbNSFP_gnomAD_genomes_Amish_Ancestry_AlleleNumber',
    'dbNSFP_CADD_phred_hg19': 'dbNSFP_CADD_phred_hg19',
    'dbNSFP_ESP6500_AA_AC': 'dbNSFP_ESP6500_AA_AlleleCount',
    'dbNSFP_gnomAD_exomes_controls_AN': 'dbNSFP_gnomAD_exomes_controls_AlleleNumber',
    'dbNSFP_fathmm_XF_coding_score': 'dbNSFP_fathmm_XF_coding_score',
    'dbNSFP_gnomAD_exomes_flag': 'dbNSFP_gnomAD_exomes_flag',
    'dbNSFP_hg19_pos_1_based_': 'dbNSFP_hg19_pos_1_based_',
    'dbNSFP_ExAC_NFE_AF': 'dbNSFP_ExAC_Non_Finnish_Europeans_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_controls_AF': 'dbNSFP_gnomAD_exomes_controls_AlleleFrequency',
    'dbNSFP_BayesDel_addAF_score': 'dbNSFP_BayesDel_addAF_score',
    'dbNSFP_LIST_S2_score': 'dbNSFP_LIST_S2_score',
    'dbNSFP_gnomAD_genomes_AMI_AC': 'dbNSFP_gnomAD_genomes_Amish_Ancestry_AlleleCount',
    'dbNSFP_PROVEAN_converted_rankscore': 'dbNSFP_PROVEAN_converted_rankscore',
    'dbNSFP_DEOGEN2_rankscore': 'dbNSFP_DEOGEN2_rankscore',
    'dbNSFP_bStatistic': 'dbNSFP_bStatistic',
    'dbNSFP_gnomAD_exomes_controls_AC': 'dbNSFP_gnomAD_exomes_controls_AlleleCount',
    'dbNSFP_ref': 'dbNSFP_Reference',
    'dbNSFP_DANN_score': 'dbNSFP_DANN_score',
    'dbNSFP_ExAC_nonpsych_EAS_AC': 'dbNSFP_ExAC_nonpsych_East_Asian_ancestry_AlleleCount',
    'dbNSFP_gnomAD_exomes_AMR_AF': 'dbNSFP_gnomAD_exomes_Latino_Ancestry_AlleleFrequency',
    'dbNSFP_ExAC_nonpsych_EAS_AF': 'dbNSFP_ExAC_nonpsych_East_Asian_ancestry_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_AMR_AC': 'dbNSFP_gnomAD_exomes_Latino_Ancestry_AlleleCount',
    'dbNSFP_Aloft_prob_Recessive': 'dbNSFP_Aloft_prob_Recessive',
    'dbNSFP_Interpro_domain': 'dbNSFP_Interpro_domain',
    'dbNSFP_SiPhy_29way_logOdds_rankscore': 'dbNSFP_SiPhy_29way_logOdds_rankscore',
    'dbNSFP_ClinPred_pred': 'dbNSFP_ClinPred_pred',
    'dbNSFP_Reliability_index': 'dbNSFP_Reliability_index',
    'dbNSFP_gnomAD_exomes_AMR_AN': 'dbNSFP_gnomAD_exomes_Latino_Ancestry_AlleleNumber',
    'dbNSFP_gnomAD_exomes_FIN_nhomalt': 'dbNSFP_gnomAD_exomes_Finnish_Ancestry_HomozygousIndividuals',
    'dbNSFP_gnomAD_exomes_NFE_nhomalt': 'dbNSFP_gnomAD_exomes_Non_Finnish_Europeans_HomozygousIndividuals',
    'dbNSFP_phyloP30way_mammalian': 'dbNSFP_phyloP30way_mammalian',
    'dbNSFP_gnomAD_genomes_ASJ_AF': 'dbNSFP_gnomAD_genomes_Ashkenazi_Jewish_ancestry_AlleleFrequency',
    'dbNSFP_gnomAD_genomes_ASJ_AC': 'dbNSFP_gnomAD_genomes_Ashkenazi_Jewish_ancestry_AlleleCount',
    'dbNSFP_ExAC_nonpsych_AF': 'dbNSFP_ExAC_nonpsych_AlleleFrequency',
    'dbNSFP_MetaLR_score': 'dbNSFP_MetaLR_score',
    'dbNSFP_gnomAD_genomes_ASJ_AN': 'dbNSFP_gnomAD_genomes_Ashkenazi_Jewish_ancestry_AlleleNumber',
    'dbNSFP_chr': 'dbNSFP_chr',
    'dbNSFP_ExAC_nonpsych_AC': 'dbNSFP_ExAC_nonpsych_AlleleCount',
    'dbNSFP_phastCons17way_primate_rankscore': 'dbNSFP_phastCons17way_primate_rankscore',
    'dbNSFP_1000Gp3_AFR_AC': 'dbNSFP_1000Gp3_AFR_AlleleCount',
    'dbNSFP_BayesDel_noAF_score': 'dbNSFP_BayesDel_noAF_score',
    'dbNSFP_HGVSp_VEP': 'dbNSFP_HGVSp_VEP',
    'dbNSFP_ExAC_AMR_AF': 'dbNSFP_ExAC_Latino_Ancestry_AlleleFrequency',
    'dbNSFP_1000Gp3_AFR_AF': 'dbNSFP_1000Gp3_AFR_AlleleFrequency',
    'dbNSFP_gnomAD_genomes_AMR_nhomalt': 'dbNSFP_gnomAD_genomes_Latino_Ancestry_HomozygousIndividuals',
    'dbNSFP_ExAC_AMR_AC': 'dbNSFP_ExAC_Latino_Ancestry_AlleleCount',
    'dbNSFP_ExAC_NFE_AC': 'dbNSFP_ExAC_Non_Finnish_Europeans_AlleleCount',
    'dbNSFP_Eigen_PC_raw_coding_rankscore': 'dbNSFP_Eigen_PC_raw_coding_rankscore',
    'dbNSFP_gnomAD_exomes_FIN_AF': 'dbNSFP_gnomAD_exomes_Finnish_Ancestry_AlleleFrequency',
    'dbNSFP_clinvar_review': 'dbNSFP_clinvar_review',
    'dbNSFP_DEOGEN2_score': 'dbNSFP_DEOGEN2_score',
    'dbNSFP_genename': 'dbNSFP_genename',
    'dbNSFP_REVEL_score': 'dbNSFP_REVEL_score',
    'dbNSFP_gnomAD_exomes_FIN_AN': 'dbNSFP_gnomAD_exomes_Finnish_Ancestry_AlleleNumber',
    'dbNSFP_MutPred_score': 'dbNSFP_MutPred_score',
    'dbNSFP_ExAC_nonTCGA_EAS_AF': 'dbNSFP_ExAC_nonTCGA_East_Asian_ancestry_AlleleFrequency',
    'dbNSFP_PrimateAI_score': 'dbNSFP_PrimateAI_score',
    'dbNSFP_UK10K_AF': 'dbNSFP_UK10K_AlleleFrequency',
    'dbNSFP_BayesDel_addAF_pred': 'dbNSFP_BayesDel_addAF_pred',
    'dbNSFP_CADD_raw_hg19': 'dbNSFP_CADD_raw_hg19',
    'dbNSFP_HUVEC_fitCons_rankscore': 'dbNSFP_HUVEC_fitCons_rankscore',
    'dbNSFP_MVP_score': 'dbNSFP_MVP_score',
    'dbNSFP_UK10K_AC': 'dbNSFP_UK10K_AlleleCount',
    'dbNSFP_hg19_chr': 'dbNSFP_hg19_chr',
    'dbNSFP_gnomAD_genomes_AFR_nhomalt': 'dbNSFP_gnomAD_genomes_AFR_HomozygousIndividuals',
    'dbNSFP_gnomAD_genomes_POPMAX_nhomalt': 'dbNSFP_gnomAD_genomes_PopulationMax_HomozygousIndividuals',
    'dbNSFP_ExAC_nonTCGA_AFR_AC': 'dbNSFP_ExAC_nonTCGA_AFR_AlleleCount',
    'dbNSFP_1000Gp3_AC': 'dbNSFP_1000Gp3_AlleleCount',
    'dbNSFP_ExAC_nonTCGA_AF': 'dbNSFP_ExAC_nonTCGA_AlleleFrequency',
    'dbNSFP_1000Gp3_AF': 'dbNSFP_1000Gp3_AlleleFrequency',
    'dbNSFP_ExAC_AF': 'dbNSFP_ExAC_AlleleFrequency',
    'dbNSFP_ExAC_nonTCGA_AC': 'dbNSFP_ExAC_nonTCGA_AlleleCount',
    'dbNSFP_ExAC_AC': 'dbNSFP_ExAC_AlleleCount',
    'dbNSFP_ExAC_nonTCGA_AFR_AF': 'dbNSFP_ExAC_nonTCGA_AFR_AlleleFrequency',
    'dbNSFP_Uniprot_acc': 'dbNSFP_Uniprot_acc',
    'dbNSFP_gnomAD_genomes_ASJ_nhomalt': 'dbNSFP_gnomAD_genomes_Ashkenazi_Jewish_ancestry_HomozygousIndividuals',
    'dbNSFP_gnomAD_genomes_flag': 'dbNSFP_gnomAD_genomes_flag',
    'dbNSFP_LINSIGHT_rankscore': 'dbNSFP_LINSIGHT_rankscore',
    'dbNSFP_GM12878_fitCons_rankscore': 'dbNSFP_GM12878_fitCons_rankscore',
    'dbNSFP_Eigen_PC_raw_coding': 'dbNSFP_Eigen_PC_raw_coding',
    'dbNSFP_GM12878_confidence_value': 'dbNSFP_GM12878_confidence_value',
    'dbNSFP_gnomAD_exomes_controls_NFE_nhomalt': 'dbNSFP_gnomAD_exomes_controls_Non_Finnish_Europeans_HomozygousIndividuals',
    'dbNSFP_M_CAP_rankscore': 'dbNSFP_M_CAP_rankscore',
    'dbNSFP_MutationTaster_score': 'dbNSFP_MutationTaster_score',
    'dbNSFP_gnomAD_exomes_controls_EAS_nhomalt': 'dbNSFP_gnomAD_exomes_controls_East_Asian_ancestry_HomozygousIndividuals',
    'dbNSFP_LIST_S2_rankscore': 'dbNSFP_LIST_S2_rankscore',
    'dbNSFP_Polyphen2_HVAR_pred': 'dbNSFP_Polyphen2_HVAR_pred',
    'dbNSFP_SIFT_pred': 'dbNSFP_SIFT_pred',
    'dbNSFP_gnomAD_exomes_FIN_AC': 'dbNSFP_gnomAD_exomes_Finnish_Ancestry_AlleleCount',
    'dbNSFP_phastCons30way_mammalian': 'dbNSFP_phastCons30way_mammalian',
    'dbNSFP_gnomAD_exomes_controls_NFE_AC': 'dbNSFP_gnomAD_exomes_controls_Non_Finnish_Europeans_AlleleCount',
    'dbNSFP_gnomAD_genomes_POPMAX_AC': 'dbNSFP_gnomAD_genomes_PopulationMax_AlleleCount',
    'dbNSFP_gnomAD_genomes_POPMAX_AF': 'dbNSFP_gnomAD_genomes_PopulationMax_AlleleFrequency',
    'dbNSFP_Ensembl_transcriptid': 'dbNSFP_Ensembl_transcriptid',
    'dbNSFP_gnomAD_exomes_controls_NFE_AF': 'dbNSFP_gnomAD_exomes_controls_Non_Finnish_Europeans_AlleleFrequency',
    'dbNSFP_phastCons100way_vertebrate_rankscore': 'dbNSFP_phastCons100way_vertebrate_rankscore',
    'dbNSFP_clinvar_MedGen_id': 'dbNSFP_clinvar_MedGen_id',
    'dbNSFP_gnomAD_genomes_POPMAX_AN': 'dbNSFP_gnomAD_genomes_PopulationMax_AlleleNumber',
    'dbNSFP_gnomAD_exomes_controls_NFE_AN': 'dbNSFP_gnomAD_exomes_controls_Non_Finnish_Europeans_AlleleNumber',
    'dbNSFP_ExAC_nonpsych_AMR_AF': 'dbNSFP_ExAC_nonpsych_Latino_Ancestry_AlleleFrequency',
    'dbNSFP_ExAC_nonpsych_AMR_AC': 'dbNSFP_ExAC_nonpsych_Latino_Ancestry_AlleleCount',
    'dbNSFP_MutPred_protID': 'dbNSFP_MutPred_protID',
    'dbNSFP_gnomAD_genomes_AMR_AN': 'dbNSFP_gnomAD_genomes_Latino_Ancestry_AlleleNumber',
    'dbNSFP_FATHMM_pred': 'dbNSFP_FATHMM_pred',
    'dbNSFP_SIFT4G_score': 'dbNSFP_SIFT4G_score',
    'dbNSFP_integrated_fitCons_score': 'dbNSFP_integrated_fitCons_score',
    'dbNSFP_MutPred_Top5features': 'dbNSFP_MutPred_Top5features',
    'dbNSFP_fathmm_XF_coding_rankscore': 'dbNSFP_fathmm_XF_coding_rankscore',
    'dbNSFP_HUVEC_fitCons_score': 'dbNSFP_HUVEC_fitCons_score',
    'dbNSFP_ExAC_nonpsych_Adj_AF': 'dbNSFP_ExAC_nonpsych_Adj_AlleleFrequency',
    'dbNSFP_SIFT4G_pred': 'dbNSFP_SIFT4G_pred',
    'dbNSFP_VindijiaNeandertal': 'dbNSFP_VindijiaNeandertal',
    'dbNSFP_gnomAD_genomes_AMR_AC': 'dbNSFP_gnomAD_genomes_Latino_Ancestry_AlleleCount',
    'dbNSFP_gnomAD_genomes_EAS_nhomalt': 'dbNSFP_gnomAD_genomes_East_Asian_ancestry_HomozygousIndividuals',
    'dbNSFP_gnomAD_exomes_SAS_AC': 'dbNSFP_gnomAD_exomes_South_Asian_ancestry_AlleleCount',
    'dbNSFP_gnomAD_exomes_controls_POPMAX_AF': 'dbNSFP_gnomAD_exomes_controls_PopulationMax_AlleleFrequency',
    'dbNSFP_ExAC_nonpsych_Adj_AC': 'dbNSFP_ExAC_nonpsych_Adj_AlleleCount',
    'dbNSFP_SIFT_score': 'dbNSFP_SIFT_score',
    'dbNSFP_phyloP100way_vertebrate_rankscore': 'dbNSFP_phyloP100way_vertebrate_rankscore',
    'dbNSFP_gnomAD_exomes_SAS_AF': 'dbNSFP_gnomAD_exomes_South_Asian_ancestry_AlleleFrequency',
    'dbNSFP_codon_degeneracy': 'dbNSFP_codon_degeneracy',
    'dbNSFP_gnomAD_exomes_controls_POPMAX_AN': 'dbNSFP_gnomAD_exomes_controls_PopulationMax_AlleleNumber',
    'dbNSFP_gnomAD_genomes_AMR_AF': 'dbNSFP_gnomAD_genomes_Latino_Ancestry_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_SAS_AN': 'dbNSFP_gnomAD_exomes_South_Asian_ancestry_AlleleNumber',
    'dbNSFP_rs_dbSNP151': 'dbNSFP_rs_dbSNP151',
    'dbNSFP_ExAC_nonTCGA_EAS_AC': 'dbNSFP_ExAC_nonTCGA_East_Asian_ancestry_AlleleCount',
    'dbNSFP_MetaSVM_rankscore': 'dbNSFP_MetaSVM_rankscore',
    'dbNSFP_gnomAD_genomes_SAS_nhomalt': 'dbNSFP_gnomAD_genomes_South_Asian_ancestry_HomozygousIndividuals',
    'dbNSFP_DANN_rankscore': 'dbNSFP_DANN_rankscore',
    'dbNSFP_gnomAD_exomes_controls_POPMAX_AC': 'dbNSFP_gnomAD_exomes_controls_PopulationMax_AlleleCount',
    'dbNSFP_Aloft_prob_Dominant': 'dbNSFP_Aloft_prob_Dominant',
    'dbNSFP_BayesDel_noAF_rankscore': 'dbNSFP_BayesDel_noAF_rankscore',
    'dbNSFP_phyloP30way_mammalian_rankscore': 'dbNSFP_phyloP30way_mammalian_rankscore',
    'dbNSFP_1000Gp3_SAS_AC': 'dbNSFP_1000Gp3_South_Asian_ancestry_AlleleCount',
    'dbNSFP_ExAC_EAS_AC': 'dbNSFP_ExAC_East_Asian_ancestry_AlleleCount',
    'dbNSFP_cds_strand': 'dbNSFP_cds_strand',
    'dbNSFP_gnomAD_exomes_POPMAX_nhomalt': 'dbNSFP_gnomAD_exomes_PopulationMax_HomozygousIndividuals',
    'dbNSFP_1000Gp3_SAS_AF': 'dbNSFP_1000Gp3_South_Asian_ancestry_AlleleFrequency',
    'dbNSFP_ExAC_EAS_AF': 'dbNSFP_ExAC_East_Asian_ancestry_AlleleFrequency',
    'dbNSFP_MutationTaster_model': 'dbNSFP_MutationTaster_model',
    'dbNSFP_gnomAD_exomes_controls_EAS_AN': 'dbNSFP_gnomAD_exomes_controls_East_Asian_ancestry_AlleleNumber',
    'dbNSFP_codonpos': 'dbNSFP_codonpos',
    'dbNSFP_ExAC_nonTCGA_Adj_AF': 'dbNSFP_ExAC_nonTCGA_Adj_AlleleFrequency',
    'dbNSFP_ClinPred_score': 'dbNSFP_ClinPred_score',
    'dbNSFP_MPC_score': 'dbNSFP_MPC_score',
    'dbNSFP_VEP_canonical': 'dbNSFP_VEP_canonical',
    'dbNSFP_ExAC_Adj_AC': 'dbNSFP_ExAC_Adj_AlleleCount',
    'dbNSFP_ExAC_Adj_AF': 'dbNSFP_ExAC_Adj_AlleleFrequency',
    'dbNSFP_ExAC_nonpsych_AFR_AF': 'dbNSFP_ExAC_nonpsych_AFR_AlleleFrequency',
    'dbNSFP_BayesDel_addAF_rankscore': 'dbNSFP_BayesDel_addAF_rankscore',
    'dbNSFP_gnomAD_genomes_AC': 'dbNSFP_gnomAD_genomes_AlleleCount',
    'dbNSFP_ClinPred_rankscore': 'dbNSFP_ClinPred_rankscore',
    'dbNSFP_ExAC_nonpsych_AFR_AC': 'dbNSFP_ExAC_nonpsych_AFR_AlleleCount',
    'dbNSFP_gnomAD_genomes_AF': 'dbNSFP_gnomAD_genomes_AlleleFrequency',
    'dbNSFP_SIFT4G_converted_rankscore': 'dbNSFP_SIFT4G_converted_rankscore',
    'dbNSFP_GenoCanyon_rankscore': 'dbNSFP_GenoCanyon_rankscore',
    'dbNSFP_SIFT_converted_rankscore': 'dbNSFP_SIFT_converted_rankscore',
    'dbNSFP_gnomAD_exomes_controls_EAS_AF': 'dbNSFP_gnomAD_exomes_controls_East_Asian_ancestry_AlleleFrequency',
    'dbNSFP_ExAC_nonTCGA_Adj_AC': 'dbNSFP_ExAC_nonTCGA_Adj_AlleleCount',
    'dbNSFP_gnomAD_exomes_controls_EAS_AC': 'dbNSFP_gnomAD_exomes_controls_East_Asian_ancestry_AlleleCount',
    'dbNSFP_Aloft_Fraction_transcripts_affected': 'dbNSFP_Aloft_Fraction_transcripts_affected',
    'dbNSFP_VEST4_score': 'dbNSFP_VEST4_score',
    'dbNSFP_Polyphen2_HDIV_rankscore': 'dbNSFP_Polyphen2_HDIV_rankscore',
    'dbNSFP_MutationTaster_converted_rankscore': 'dbNSFP_MutationTaster_converted_rankscore',
    'dbNSFP_Eigen_raw_coding_rankscore': 'dbNSFP_Eigen_raw_coding_rankscore',
    'dbNSFP_phyloP100way_vertebrate': 'dbNSFP_phyloP100way_vertebrate',
    'dbNSFP_LRT_pred': 'dbNSFP_LRT_pred',
    'dbNSFP_1000Gp3_EUR_AC': 'dbNSFP_1000Gp3_EUR_AlleleCount',
    'dbNSFP_CADD_phred': 'dbNSFP_CADD_phred',
    'dbNSFP_gnomAD_exomes_ASJ_AC': 'dbNSFP_gnomAD_exomes_Ashkenazi_Jewish_ancestry_AlleleCount',
    'dbNSFP_1000Gp3_EUR_AF': 'dbNSFP_1000Gp3_EUR_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_ASJ_AF': 'dbNSFP_gnomAD_exomes_Ashkenazi_Jewish_ancestry_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_controls_FIN_nhomalt': 'dbNSFP_gnomAD_exomes_controls_Finnish_Ancestry_HomozygousIndividuals',
    'dbNSFP_gnomAD_genomes_AN': 'dbNSFP_gnomAD_genomes_AlleleNumber',
    'dbNSFP_Eigen_phred_coding': 'dbNSFP_Eigen_phred_coding',
    'dbNSFP_Uniprot_entry': 'dbNSFP_Uniprot_entry',
    'dbNSFP_clinvar_trait': 'dbNSFP_clinvar_trait',
    'dbNSFP_fathmm_XF_coding_pred': 'dbNSFP_fathmm_XF_coding_pred',
    'dbNSFP_Eigen_raw_coding': 'dbNSFP_Eigen_raw_coding',
    'dbNSFP_clinvar_Orphanet_id': 'dbNSFP_clinvar_Orphanet_id',
    'dbNSFP_gnomAD_exomes_ASJ_AN': 'dbNSFP_gnomAD_exomes_Ashkenazi_Jewish_ancestry_AlleleNumber',
    'dbNSFP_ExAC_nonTCGA_NFE_AF': 'dbNSFP_ExAC_nonTCGA_Non_Finnish_Europeans_AlleleFrequency',
    'dbNSFP_PROVEAN_score': 'dbNSFP_PROVEAN_score',
    'dbNSFP_ALSPAC_AC': 'dbNSFP_ALSPAC_AlleleCount',
    'dbNSFP_BayesDel_noAF_pred': 'dbNSFP_BayesDel_noAF_pred',
    'dbNSFP_VEST4_rankscore': 'dbNSFP_VEST4_rankscore',
    'dbNSFP_gnomAD_genomes_NFE_nhomalt': 'dbNSFP_gnomAD_genomes_Non_Finnish_Europeans_HomozygousIndividuals',
    'dbNSFP_SiPhy_29way_logOdds': 'dbNSFP_SiPhy_29way_logOdds',
    'dbNSFP_gnomAD_exomes_controls_SAS_AC': 'dbNSFP_gnomAD_exomes_controls_South_Asian_ancestry_AlleleCount',
    'dbNSFP_gnomAD_genomes_EAS_AC': 'dbNSFP_gnomAD_genomes_East_Asian_ancestry_AlleleCount',
    'dbNSFP_GERP___NR': 'dbNSFP_GERP___NR',
    'dbNSFP_gnomAD_genomes_EAS_AF': 'dbNSFP_gnomAD_genomes_East_Asian_ancestry_AlleleFrequency',
    'dbNSFP_Polyphen2_HVAR_score': 'dbNSFP_Polyphen2_HVAR_score',
    'dbNSFP_gnomAD_exomes_controls_SAS_AF': 'dbNSFP_gnomAD_exomes_controls_South_Asian_ancestry_AlleleFrequency',
    'dbNSFP_FATHMM_converted_rankscore': 'dbNSFP_FATHMM_converted_rankscore',
    'dbNSFP_HGVSc_ANNOVAR': 'dbNSFP_HGVSc_ANNOVAR',
    'dbNSFP_phastCons30way_mammalian_rankscore': 'dbNSFP_phastCons30way_mammalian_rankscore',
    'dbNSFP_1000Gp3_AMR_AF': 'dbNSFP_1000Gp3_Latino_Ancestry_AlleleFrequency',
    'dbNSFP_ALSPAC_AF': 'dbNSFP_ALSPAC_AlleleFrequency',
    'dbNSFP_ExAC_nonTCGA_AMR_AC': 'dbNSFP_ExAC_nonTCGA_Latino_Ancestry_AlleleCount',
    'dbNSFP_ExAC_nonTCGA_NFE_AC': 'dbNSFP_ExAC_nonTCGA_Non_Finnish_Europeans_AlleleCount',
    'dbNSFP_clinvar_OMIM_id': 'dbNSFP_clinvar_OMIM_id',
    'dbNSFP_gnomAD_genomes_EAS_AN': 'dbNSFP_gnomAD_genomes_East_Asian_ancestry_AlleleNumber',
    'dbNSFP_1000Gp3_AMR_AC': 'dbNSFP_1000Gp3_Latino_Ancestry_AlleleCount',
    'dbNSFP_gnomAD_exomes_NFE_AN': 'dbNSFP_gnomAD_exomes_Non_Finnish_Europeans_AlleleNumber',
    'dbNSFP_ExAC_nonTCGA_AMR_AF': 'dbNSFP_ExAC_nonTCGA_Latino_Ancestry_AlleleFrequency',
    'dbNSFP_phyloP17way_primate_rankscore': 'dbNSFP_phyloP17way_primate_rankscore',
    'dbNSFP_CADD_raw_rankscore_hg19': 'dbNSFP_CADD_raw_rankscore_hg19',
    'dbNSFP_integrated_confidence_value': 'dbNSFP_integrated_confidence_value',
    'dbNSFP_gnomAD_exomes_NFE_AF': 'dbNSFP_gnomAD_exomes_Non_Finnish_Europeans_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_controls_FIN_AN': 'dbNSFP_gnomAD_exomes_controls_Finnish_Ancestry_AlleleNumber',
    'dbNSFP_integrated_fitCons_rankscore': 'dbNSFP_integrated_fitCons_rankscore',
    'dbNSFP_ExAC_AFR_AF': 'dbNSFP_ExAC_AFR_AlleleFrequency',
    'dbNSFP_MutPred_AAchange': 'dbNSFP_MutPred_AAchange',
    'dbNSFP_CADD_raw': 'dbNSFP_CADD_raw',
    'dbNSFP_gnomAD_exomes_controls_FIN_AF': 'dbNSFP_gnomAD_exomes_controls_Finnish_Ancestry_AlleleFrequency',
    'dbNSFP_ExAC_AFR_AC': 'dbNSFP_ExAC_AFR_AlleleCount',
    'dbNSFP_gnomAD_exomes_AF': 'dbNSFP_gnomAD_exomes_AlleleFrequency',
    'dbNSFP_Polyphen2_HVAR_rankscore': 'dbNSFP_Polyphen2_HVAR_rankscore',
    'dbNSFP_fathmm_MKL_coding_rankscore': 'dbNSFP_fathmm_MKL_coding_rankscore',
    'dbNSFP_GERP___RS_rankscore': 'dbNSFP_GERP___RS_rankscore',
    'dbNSFP_gnomAD_exomes_AC': 'dbNSFP_gnomAD_exomes_AlleleCount',
    'dbNSFP_alt': 'dbNSFP_Alternative',
    'dbNSFP_Aloft_pred': 'dbNSFP_Aloft_pred',
    'dbNSFP_Polyphen2_HDIV_score': 'dbNSFP_Polyphen2_HDIV_score',
    'dbNSFP_TSL': 'dbNSFP_TSL',
    'dbNSFP_pos_1_based_': 'dbNSFP_pos_1_based_',
    'dbNSFP_gnomAD_exomes_controls_FIN_AC': 'dbNSFP_gnomAD_exomes_controls_Finnish_Ancestry_AlleleCount',
    'dbNSFP_AltaiNeandertal': 'dbNSFP_AltaiNeandertal',
    'dbNSFP_aapos': 'dbNSFP_AminoAcidPosition',
    'dbNSFP_gnomAD_exomes_AFR_AF': 'dbNSFP_gnomAD_exomes_AFR_AlleleFrequency',
    'dbNSFP_clinvar_clnsig': 'dbNSFP_clinvar_clnsig',
    'dbNSFP_MetaLR_rankscore': 'dbNSFP_MetaLR_rankscore',
    'dbNSFP_gnomAD_exomes_controls_ASJ_nhomalt': 'dbNSFP_gnomAD_exomes_controls_Ashkenazi_Jewish_ancestry_HomozygousIndividuals',
    'dbNSFP_MutationTaster_pred': 'dbNSFP_MutationTaster_pred',
    'dbNSFP_gnomAD_exomes_AFR_AN': 'dbNSFP_gnomAD_exomes_AFR_AlleleNumber',
    'dbNSFP_MetaLR_pred': 'dbNSFP_MetaLR_pred',
    'dbNSFP_gnomAD_exomes_AMR_nhomalt': 'dbNSFP_gnomAD_exomes_Latino_Ancestry_HomozygousIndividuals',
    'dbNSFP_gnomAD_exomes_AN': 'dbNSFP_gnomAD_exomes_AlleleNumber',
    'dbNSFP_MPC_rankscore': 'dbNSFP_MPC_rankscore',
    'dbNSFP_REVEL_rankscore': 'dbNSFP_REVEL_rankscore',
    'dbNSFP_CADD_raw_rankscore': 'dbNSFP_CADD_raw_rankscore',
    'dbNSFP_LIST_S2_pred': 'dbNSFP_LIST_S2_pred',
    'dbNSFP_GTEx_V8_gene': 'dbNSFP_GTEx_V8_gene',
    'dbNSFP_gnomAD_genomes_AFR_AF': 'dbNSFP_gnomAD_genomes_AFR_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_AFR_nhomalt': 'dbNSFP_gnomAD_exomes_AFR_HomozygousIndividuals',
    'dbNSFP_Geuvadis_eQTL_target_gene': 'dbNSFP_Geuvadis_eQTL_target_gene',
    'dbNSFP_fathmm_MKL_coding_group': 'dbNSFP_fathmm_MKL_coding_group',
    'dbNSFP_gnomAD_exomes_ASJ_nhomalt': 'dbNSFP_gnomAD_exomes_Ashkenazi_Jewish_ancestry_HomozygousIndividuals',
    'dbNSFP_MutationAssessor_score': 'dbNSFP_MutationAssessor_score',
    'dbNSFP_TWINSUK_AF': 'dbNSFP_TWINSUK_AlleleFrequency',
    'dbNSFP_TWINSUK_AC': 'dbNSFP_TWINSUK_AlleleCount',
    'dbNSFP_gnomAD_genomes_AFR_AN': 'dbNSFP_gnomAD_genomes_AFR_AlleleNumber',
    'dbNSFP_HGVSc_snpEff': 'dbNSFP_HGVSc_snpEff',
    'dbNSFP_MVP_rankscore': 'dbNSFP_MVP_rankscore',
    'dbNSFP_GM12878_fitCons_score': 'dbNSFP_GM12878_fitCons_score',
    'dbNSFP_gnomAD_exomes_AFR_AC': 'dbNSFP_gnomAD_exomes_AFR_AlleleCount',
    'dbNSFP_Ensembl_proteinid': 'dbNSFP_Ensembl_proteinid',
    'dbNSFP_clinvar_hgvs': 'dbNSFP_clinvar_hgvs',
    'dbNSFP_gnomAD_exomes_controls_AFR_nhomalt': 'dbNSFP_gnomAD_exomes_controls_AFR_HomozygousIndividuals',
    'dbNSFP_gnomAD_genomes_AFR_AC': 'dbNSFP_gnomAD_genomes_AFR_AlleleCount',
    'dbNSFP_MutationTaster_AAE': 'dbNSFP_MutationTaster_AAE',
    'dbNSFP_LINSIGHT': 'dbNSFP_LINSIGHT',
    'dbNSFP_ExAC_nonpsych_SAS_AF': 'dbNSFP_ExAC_nonpsych_South_Asian_ancestry_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_EAS_AN': 'dbNSFP_gnomAD_exomes_East_Asian_ancestry_AlleleNumber',
    'dbNSFP_GenoCanyon_score': 'dbNSFP_GenoCanyon_score',
    'dbNSFP_gnomAD_exomes_POPMAX_AN': 'dbNSFP_gnomAD_exomes_PopulationMax_AlleleNumber',
    'dbNSFP_gnomAD_exomes_controls_SAS_nhomalt': 'dbNSFP_gnomAD_exomes_controls_South_Asian_ancestry_HomozygousIndividuals',
    'dbNSFP_ExAC_nonpsych_SAS_AC': 'dbNSFP_ExAC_nonpsych_South_Asian_ancestry_AlleleCount',
    'dbNSFP_SiPhy_29way_pi': 'dbNSFP_SiPhy_29way_pi',
    'dbNSFP_gnomAD_exomes_EAS_AF': 'dbNSFP_gnomAD_exomes_East_Asian_ancestry_AlleleFrequency',
    'dbNSFP_H1_hESC_fitCons_score': 'dbNSFP_H1_hESC_fitCons_score',
    'dbNSFP_gnomAD_exomes_EAS_AC': 'dbNSFP_gnomAD_exomes_East_Asian_ancestry_AlleleCount',
    'dbNSFP_Polyphen2_HDIV_pred': 'dbNSFP_Polyphen2_HDIV_pred',
    'dbNSFP_gnomAD_exomes_POPMAX_AC': 'dbNSFP_gnomAD_exomes_PopulationMax_AlleleCount',
    'dbNSFP_phyloP17way_primate': 'dbNSFP_phyloP17way_primate',
    'dbNSFP_gnomAD_exomes_controls_AMR_nhomalt': 'dbNSFP_gnomAD_exomes_controls_Latino_Ancestry_HomozygousIndividuals',
    'dbNSFP_LRT_Omega': 'dbNSFP_LRT_Omega',
    'dbNSFP_aaref': 'dbNSFP_AminoAcidReference',
    'dbNSFP_MutationAssessor_pred': 'dbNSFP_MutationAssessor_pred',
    'dbNSFP_gnomAD_exomes_controls_nhomalt': 'dbNSFP_gnomAD_exomes_controls_HomozygousIndividuals',
    'dbNSFP_gnomAD_exomes_POPMAX_AF': 'dbNSFP_gnomAD_exomes_PopulationMax_AlleleFrequency',
    'dbNSFP_gnomAD_exomes_controls_POPMAX_nhomalt': 'dbNSFP_gnomAD_exomes_controls_PopulationMax_HomozygousIndividuals',
    'dbNSFP_gnomAD_exomes_controls_SAS_AN': 'dbNSFP_gnomAD_exomes_controls_South_Asian_ancestry_AlleleNumber',
    "clinvar_DBVARID": "ClinVar_dbvar_AccessionNumber",
    "clinvar_ALLELEID": "ClinVar_Allele_ID",
    "clinvar_CLNSIG": "ClinVar_ClinicalSignificance",
    "clinvar_CLNVCSO": "ClinVar_SequenceOnthology",
    "clinvar_CLNREVSTAT": "ClinVar_ReviewStatus",
    "clinvar_RS": "ClinVar_dbSNP_ID",
    "clinvar_CLNDNINCL": "ClinVar_Disease_ID",
    "clinvar_ORIGIN": "ClinVar_Origin",
    "clinvar_MC": "ClinVar_MolecularConsequences",
    "clinvar_CLNDN": "ClinVar_Disease_Name",
    "clinvar_CLNVC": "ClinVar_VariantType",
    "clinvar_CLNVI": "ClinVar_ClinicalSource",
    "clinvar_AF_EXAC": "ClinVar_ExAC_AlleleFrequency",
    "clinvar_AF_ESP": "ClinVar_ESP_AlleleFrequency",
    "clinvar_CLNSIGINCL": "ClinVar_Haplotype_Significance",
    "clinvar_CLNDISDB": "ClinVar_DiseaseDatabase",
    "clinvar_GENEINFO": "ClinVar_Gene_Info",
    "clinvar_CLNDISDBINCL": "ClinVar_Disease_Gene",
    "clinvar_AF_TGP": "ClinVar_TGP_AlleleFrequency",
    "clinvar_CLNSIGCONF": "ClinVar_SingleVariant_Significance",
    "clinvar_CLNHGVS": "ClinVar_HGVS",
    "clinvar_SSR": "ClinVar_SuspectReasonCode",
    "ExistsInClinVar": "Variant_ExistsInClinVar",
    'faf95_adj': 'FilteredAlleleFrequency95pct_adj',
    'faf95_afr': 'FilteredAlleleFrequency95pct_African_Ancestry',
    'faf95_amr': 'FilteredAlleleFrequency95pct_Latino_Ancestry',
    'faf95_eas': 'FilteredAlleleFrequency95pct_East_Asian_ancestry',
    'faf95_nfe': 'FilteredAlleleFrequency95pct_Non_Finnish_Europeans',
    'faf95_sas': 'FilteredAlleleFrequency95pct_South_Asian_ancestry',
    'faf99_adj': 'FilteredAlleleFrequency99pct_adj',
    'faf99_afr': 'FilteredAlleleFrequency99pct_African_Ancestry',
    'faf99_amr': 'FilteredAlleleFrequency99pct_Latino_Ancestry',
    'faf99_eas': 'FilteredAlleleFrequency99pct_East_Asian_ancestry',
    'faf99_nfe': 'FilteredAlleleFrequency99pct_Non_Finnish_Europeans',
    'faf99_sas': 'FilteredAlleleFrequency99pct_South_Asian_ancestry',
    'lcr': 'lcr',
    'n_alt_alleles': 'n_Alternative_alleles',
    'nhomalt': 'HomozygousIndividuals',
    'nhomalt_afr': 'HomozygousIndividuals_African_Ancestry',
    'nhomalt_afr_female': 'HomozygousIndividuals_African_Ancestry_female',
    'nhomalt_afr_male': 'HomozygousIndividuals_African_Ancestry_male',
    'nhomalt_ami': 'HomozygousIndividuals_Amish_Ancestry',
    'nhomalt_ami_female': 'HomozygousIndividuals_Amish_Ancestry_female',
    'nhomalt_ami_male': 'HomozygousIndividuals_Amish_Ancestry_male',
    'nhomalt_amr': 'HomozygousIndividuals_Latino_Ancestry',
    'nhomalt_amr_female': 'HomozygousIndividuals_Latino_Ancestry_female',
    'nhomalt_amr_male': 'HomozygousIndividuals_Latino_Ancestry_male',
    'nhomalt_asj': 'HomozygousIndividuals_Ashkenazi_Jewish_ancestry',
    'nhomalt_asj_female': 'HomozygousIndividuals_Ashkenazi_Jewish_ancestry_female',
    'nhomalt_asj_male': 'HomozygousIndividuals_Ashkenazi_Jewish_ancestry_male',
    'nhomalt_eas': 'HomozygousIndividuals_East_Asian_ancestry',
    'nhomalt_eas_female': 'HomozygousIndividuals_East_Asian_ancestry_female',
    'nhomalt_eas_male': 'HomozygousIndividuals_East_Asian_ancestry_male',
    'nhomalt_female': 'HomozygousIndividuals_female',
    'nhomalt_fin': 'HomozygousIndividuals_Finnish_Ancestry',
    'nhomalt_fin_female': 'HomozygousIndividuals_Finnish_Ancestry_female',
    'nhomalt_fin_male': 'HomozygousIndividuals_Finnish_Ancestry_male',
    'nhomalt_male': 'HomozygousIndividuals_male',
    'nhomalt_nfe': 'HomozygousIndividuals_Non_Finnish_Europeans',
    'nhomalt_nfe_female': 'HomozygousIndividuals_Non_Finnish_Europeans_female',
    'nhomalt_nfe_male': 'HomozygousIndividuals_Non_Finnish_Europeans_male',
    'nhomalt_oth': 'HomozygousIndividuals_oth',
    'nhomalt_oth_female': 'HomozygousIndividuals_oth_female',
    'nhomalt_oth_male': 'HomozygousIndividuals_oth_male',
    'nhomalt_raw': 'HomozygousIndividuals_raw',
    'nhomalt_sas': 'HomozygousIndividuals_South_Asian_ancestry',
    'nhomalt_sas_female': 'HomozygousIndividuals_South_Asian_ancestry_female',
    'nhomalt_sas_male': 'HomozygousIndividuals_South_Asian_ancestry_male',
    'non_par': 'non_Paralog',
    'variant_type': 'variant_type'
}

# Gather parameters
add_cols = snakemake.params.get("add_cols", True)
ncbi_build = snakemake.params.get("ncbi_build", "GRCh38")
center = snakemake.params.get("center", "GustaveRoussy")
#caller = snakemake.params.get("caller", "mutect2")
logging.info("Parameters retrieved")

# Load user's data
variants = pandas.read_csv(
    snakemake.input["tsv"],
    sep="\t",
    header=0,
    index_col=None
)
logging.info("Variants loaded in memory")

# Replace header names
new_header = []
# translation_table = (
#     headers_mutect2
#     if caller.lower() == "mutect2"
#     else None
# )
translation_table = headers

for idx, colname in enumerate(variants.columns.tolist()):
    new_colname = translation_table.get(colname, colname)
    if idx == 3 and colname == "REF":
        new_header.append("Reference_Allele")
    else:
        new_header.append(new_colname if new_colname is not None else colname)
variants.columns = new_header
logging.info("New header defined")
logging.debug(variants.columns.tolist())

# Add new columns on demand
if add_cols is True:
    if "Center" not in variants.columns:
        logging.debug("Adding Sequencing Center information")
        variants["Center"] = variants["Hugo_Symbol"]

    if "NCBI_Build" not in variants.columns:
        logging.debug("Adding NCBI build information")
        variants["NCBI_Build"] = variants["Hugo_Symbol"]

    if "End_Position" not in variants.columns:
        logging.debug("Adding End position")
        if "Reference_Allele" not in variants.columns.tolist():
            variants["Reference_Allele"] = variant["REF"]
        variants["End_Position"] = [
            start - (len(ref) - 1)
            for start, ref in zip(
                variants["Start_Position"], variants["Reference_Allele"]
            )
        ]

    if "Variant_Type" not in variants.columns:
        logging.debug("Adding variant type")
        logging.debug(variants.head())
        variants["Variant_Type"] = [
            get_variant_type(ref, alt)
            for ref, alt
            in zip(variants["Reference_Allele"], variants["ALT"])
        ]

    if "SYMBOL" not in variants.columns:
        logging.debug("Adding gene symbols")
        variants["SYMBOL"] = variants["Hugo_Symbol"]

    if "HGNC_ID" not in variants.columns:
        logging.debug("Adding hugo symbols")
        variants["HGNC_ID"] = variants["Hugo_Symbol"]

    if ("ExAC_AF_AFR" not in variants.columns) and ("Allele_Frequency_African_Ancestry" in variants.columns):
        logging.debug("Adding ExAC_AF_AFR symbols")
        variants["ExAC_AF_AFR"] = variants["Allele_Frequency_African_Ancestry"]

    if ("ExAC_AF_AMR" not in variants.columns) and ("Allele_Frequency_Latino_Ancestry" in variants.columns):
        logging.debug("Adding ExAC_AF_AMR symbols")
        variants["ExAC_AF_AMR"] = variants["Allele_Frequency_Latino_Ancestry"]

    if ("ExAC_AF_EAS" not in variants.columns) and ("Allele_Frequency_East_Asian_ancestry" in variants.columns):
        logging.debug("Adding ExAC_AF_EAS symbols")
        variants["ExAC_AF_EAS"] = variants["Allele_Frequency_East_Asian_ancestry"]

    if ("ExAC_AF_FIN" not in variants.columns) and ("Allele_Frequency_Finnish_ancestry" in variants.columns):
        logging.debug("Adding ExAC_AF_FIN symbols")
        variants["ExAC_AF_FIN"] = variants["Allele_Frequency_Finnish_ancestry"]

    if ("ExAC_AF_NFE" not in variants.columns) and ("Allele_Frequency_Non_Finnish_Europeans" in variants.columns):
        logging.debug("Adding ExAC_AF_NFE symbols")
        variants["ExAC_AF_NFE"] = variants["Allele_Frequency_Non_Finnish_Europeans"]

    if ("ExAC_AF_OTH" not in variants.columns) and ("Allele_Frequency_Other_Ancestry" in variants.columns):
        logging.debug("Adding ExAC_AF_OTH symbols")
        variants["ExAC_AF_OTH"] = variants["Allele_Frequency_Other_Ancestry"]

    if ("ExAC_AF_SAS" not in variants.columns) and ("Allele_Frequency_South_Asian_ancestry" in variants.columns):
        logging.debug("Adding ExAC_AF_SAS symbols")
        variants["ExAC_AF_SAS"] = variants["Allele_Frequency_South_Asian_ancestry"]

    # if "vcf_region" not in variants.columns:
    #     logging.debug("Adding VCF regions")
    #     logging.debug(variants[["Chromosome", "Start_Position", "Variant_ID", "Reference_Allele", "Tumor_Seq_Allele2"]].shape)
    #     variants["vcf_region"] = [
    #         ":".join(map(str, [chr, pos, id, ref, alt]))
    #         for chr, pos, id, ref, alt in zip(
    #             variants["Chromosome"],
    #             variants["Start_Position"],
    #             variants["Variant_ID"],
    #             variants["Reference_Allele"],
    #             variants["Tumor_Seq_Allele1"]
    #         )
    #     ]

    if "Variant_Origin" in variants.columns:
        logging.debug("Translating Variant_Origin")
        translation = {
            "0": "unspecified",
            "0.0": "unspecified",
            "nan": "unspecified",
            "1": "germline",
            "1.0": "germline",
            "2": "somatic",
            "2.0": "somatic",
            "3": "both_germline_somatic",
            "3.0": "both_germline_somatic"
        }

        variants["Variant_Origin_Readable"] = [
            translation[str(i)] for i in variants["Variant_Origin"]
        ]

    if "Suspect_reason_code" in variants.columns:
        translation = {
            "0": "unspecified",
            "1": "Paralog",
            "2": "byEST",
            "4": "oldAlign",
            "8": "Para_EST",
            "16": "1kg_failed",
            "1024": "other",
            "0.0": "unspecified",
            "1.0": "Paralog",
            "2.0": "byEST",
            "4.0": "oldAlign",
            "8.0": "Para_EST",
            "16.0": "1kg_failed",
            "1024.0": "other",
            "nan": "unspecified"
        }

        variants["Suspect_reason_code_Readable"] = [
            translation[str(i)] for i in variants["Suspect_reason_code"]
        ]

    if "Tumor_Sample_Barcode" in snakemake.params.keys() and "Tumor_Sample_Barcode" not in variants.columns.tolist():
        variants["Tumor_Sample_Barcode"] = [
            snakemake.params["Tumor_Sample_Barcode"]
            for _ in variants["Start_Position"]
        ]

    if "Matched_Norm_Sample_Barcode" in snakemake.params.keys() and "Matched_Norm_Sample_Barcode" not in variants.columns.tolist():
        variants["Matched_Norm_Sample_Barcode"] = [
            snakemake.params["Matched_Norm_Sample_Barcode"]
            for _ in variants["Start_Position"]
        ]

variants.to_csv(snakemake.output["tsv"], sep="\t", index=False)