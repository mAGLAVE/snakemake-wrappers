#!/usr/bin/python3.8
# conding: utf-8

"""
A set of scripts designed to question iRODS and return formatted
answers.
"""

__author__ = "Thibault Dayris"
__copyright__ = "Copyright 2020, Thibault Dayris"
__email__ = "thibault.dayris@gustaveroussy.fr"
__license__ = "MIT"

from typing import Dict
from yaml import dump

file_path = None
attributes = {}

current_attribute = None


def get_key_val(line: str) -> Dict[str, str]:
    """
    Split key:value string
    """
    key, *val = line.split(":")
    return {key.strip(" "): ":".join(val).strip(" ")}


with open(snakemake.input[0], "r") as text:
    for line in text:
        if line.startswith("AVUs"):
            file_path = line[:-1].split(" ")[-1].strip(":")
        elif line.startswith(("----", "\n")):
            continue
        elif line.startswith("attribute:"):
            current_attribute = get_key_val(line=line[:-1])["attribute"]
            if file_path in attributes.keys():
                if current_attribute not in attributes[file_path].keys():
                    attributes[file_path][current_attribute] = {}
            else:
                attributes[file_path] = {current_attribute: {}}
        elif line.startswith(("value:", "units:")):
            key, val = list(get_key_val(line[:-1]).items())[0]
            if current_attribute in attributes[file_path].keys():
                if key in attributes[file_path][current_attribute].keys():
                    attributes[file_path][current_attribute][key] += f";{val}"
                else:
                    attributes[file_path][current_attribute][key] = val
            else:
                attributes[file_path][current_attribute][key] = val
        else:
            raise ValueError(f"Unknown line format: {line}")

with open(snakemake.output[0], "w") as yaml:
    dump(attributes, yaml, default_flow_style=False)