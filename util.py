from parameters import *
import json
import numpy as np


def get_log_miner_string(miner):
    if miner == Miner.ocpd.name:
        return ""
    elif miner == Miner.health.name:
        return miner
    elif miner.startswith(Miner.colliery.name):
        return miner
    else:
        ""

def build_path(dataset_name, miner, i, r, suffix):
    return f'{RESULT_PATH}{dataset_name}_{miner}_net_sample_{i}_ratio_{r}.{suffix}'


def build_log_path(d, i, r, traditional=False, miner="", suffix=""):
    if traditional:
        return f'{LOG_TRADITIONAL}{d}/{i}/{r}/{d}_sample_{i}_ratio_{r}'
    else:
        if miner != "":
            return f'{LOG_PATH}{d}_sample_{i}_ratio_{r}{get_log_miner_string(miner)}{suffix}'
        else:
            return f'{LOG_PATH}{d}_sample_{i}_ratio_{r}{suffix}'

def build_result_path(miner, d, i, infix, r, quality=False):
    if quality:
        return f"{miner}_{QUALITY_MODE}_{infix}_{d}_{i}_{r}.json"
    else:
        return f"{miner}_{infix}_{d}_{i}_{r}.json"
def export_list_to_json(my_list, output_file_path):
    with open(f'{RESULT_PATH}/{output_file_path}', 'w') as json_file:
        json.dump(my_list, json_file)

def import_list_from_json(input_file_path):
    with open(input_file_path, 'r') as json_file:
        return json.load(json_file)

def nan_imputation_double(n):
    x, y = explode(n)
    if isinstance(x, str):
        return np.nan, np.nan
    else:
        return x, y

def explode(x):
    return x[0], x[1]

def nan_imputation(x):
    if isinstance(x, str):
        return np.nan
    else:
        return x
