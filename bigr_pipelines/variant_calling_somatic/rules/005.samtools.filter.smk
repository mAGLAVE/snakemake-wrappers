rule samtools_filter_bed:
    input:
        "sambamba/sort/{sample}_{status}.bam",
        fasta=config["ref"]["fasta"],
        fasta_idx=get_fai(config["ref"]["fasta"]),
        fasta_dict=get_dict(config["ref"]["fasta"]),
        bed=config["ref"]["capture_kit_bed"],
    output:
        temp("samtools/filter/{sample}_{status}.bam"),
    threads: 10
    resources:
        mem_mb=lambda wildcards, attempt: attempt * 2048,
        time_min=lambda wildcards, attempt: attempt * 15,
        tmpdir="tmp",
    params:
        extra="-h -h",
    log:
        "logs/samtools/filter/{sample}_{status}.log",
    wrapper:
        "bio/samtools/view"