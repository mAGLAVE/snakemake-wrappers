#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This is the Snakemake Wrapper for bcl2fastq"""

__author__ = "Thibault Dayris"
__copyright__ = "Copyright 2020, Thibault Dayris"
__email__ = "thibault.dayris@gustaveroussy.fr"
__license__ = "MIT"


from os.path import exists
from snakemake.shell import shell
log = snakemake.log_fmt_shell(stdout=True, stderr=True)


# extra parameters
extra = snakemake.params.get("extra", "")

# Moose previously passed booleans for no_lane_splitting parameter
if config.params.get("no_lane_splitting", False) is True:
    extra += " --no-lane-splitting"


# Moose previously passed base_mask as a string in params
if (base_mask := config.params.get("use_bases_mask", None)) is not None:
    extra += "--use-bases-mask {}".format(base_mask)


# Moose previously passed barcode mismatches through params
if (mismatches := config.params.get("barcode_mismatches", None)) is not None:
    extra += " --barcode-mismatches {mismatches}"



# path to runfolder directory
io_parameters = " --runfolder-dir {} ".format(snakemake.input["run_dir"])

# path to the sample sheet
if "sample_sheet" in snakemake.input.keys():
    io_parameters += " --sample-sheet {} ".format(snakemake.input["sample_sheet"])
else:
    path = "{}/SampleSheet.csv".format(
        snakemake.input["run_dir"]
    )
    if exists(path):
        io_parameters += "--sample-sheet {}/SampleSheet.csv".format(
            snakemake.input["run_dir"]
        )
    else:
        raise FileNotFoundError("Could not find SampleSheet at {}".format(path))


# path to both input and intensities directories
if "input_dir" in snakemake.input.keys():
    io_parameters += " --input-dir {} ".format(snakemake.input["input_dir"])

    # The --intensities-dir parameter requires --input-dir.
    if "intensities" in snakemake.input.keys():
        io_parameters += " --intensities-dir {} ".format(
            snakemake.input["intensities"]
        )
else:
    path = "{}/Data/Intensities/BaseCalls/".format(snakemake.input["run_dir"])
    if exists(path):
        io_parameters += " --input-dir {}".format(path)
    else:
        raise FileNotFoundError("Could not find InputDir at {}".format(path))

    path = "{}/Data/Intensities/".format(snakemake.input["run_dir"])
    if exists(path):
        io_parameters += " --intensities-dir {}".format(path)
    else:
        raise FileNotFoundError("Could not find Intensities at {}".format(path))


## Output parameters
# path to demultiplexed output
out_dir = None
if "out_dir" in snakemake.output.keys():
    out_dir = snakemake.output["out_dir"]
    io_parameters += " --output-dir {} ".format(snakemake.output["out_dir"])
elif "out_dir" in snakemake.params.keys():
    out_dir = snakemake.params["out_dir"]
    io_parameters += " --output-dir {} ".format(snakemake.params["out_dir"])

# path to demultiplexing statistics directory
if "interop_dir" in snakemake.output.keys():
    io_parameters += " --interop-dir {} ".format(snakemake.output["interop_dir"])
elif out_dir is not None:
    io_parameters += " --interop-dir {}/InterOp/".format(out_dir)
else:
    io_parameters += " --interop-dir {}/InterOp/".format(
        snakemake.input["run_dir"]
    )

# path to human-readable demultiplexing statistics directory
if "stats_dir" in snakemake.output.keys():
    io_parameters += " --stats-dir {}".format(snakemake.output["stats_dir"])
elif out_dir is not None:
    io_parameters += " --stats-dir {}/Stats/".format(out_dir)
else:
    io_parameters += " --stats-dir {}/Stats/".format(
        snakemake.input["run_dir"]
    )

# path to reporting directory
if "reports_dir" in snakemake.output.keys():
    io_parameters += " --reports-dir {}".format(snakemake.output["reports_dir"])
elif out_dir is not None:
    io_parameters += " --reports-dir {}/Reports/".format(out_dir)
else:
    io_parameters += " --reports-dir {}/Stats/".format(
        snakemake.input["run_dir"]
    )


# The number of threads shall be spreaded between loading, processing
# and writing. The processing step should have more threads than the
# other ones. Documentation advises on twice more threads.
max_threads = snakemake.threads

if max_threads < 3:
    raise ValueError("At least three threads are required for bcl2fastq.")
elif max_threads == 3:
    # In case of only three threads requested, the code below would fail
    # by returning 0 threds in loading/writing.
    reserved_threads = [1, 1, 1]
else:
    # Optimal division according to documentation, knowing that all number
    # must be plain integers.
    reserved_threads = [
        int(max_threads/4),
        int(max_threads/2),
        int(max_threads/4)
    ]


# With odd number in max_threads, the above will result in less used threads
# than the number reserved by the user. Below, we simply add the difference
# (if any) to the processing step
reserved_threads[1] += max_threads - sum(reserved_threads)


shell(
    "bcl2fastq "
    # Number of threads, as defined above
    " --loading-threads {reserved_threads[0]} "
    " --processing-threads {reserved_threads[1]} "
    " --writing-threads {reserved_threads[2]} "
    " {io_parameters} "  # input/output parameters
    " {extra} "  # Optional parameters
    " {log} "  # Logging
)