import concurrent
import json
import math
import re
import subprocess
from copy import copy
from functools import partial
import random
import numpy as np
import scipy as sp
import pandas as pd
import os
from modified_pm4py_bpmn_import import *
from modified_bpmn_petri_conversion import *
from modified_pm4py_pnml_export import *

import pm4py
from pm4py.objects.log.obj import EventStream
from pm4py.objects.log.util.sampling import sample_log
from pm4py.statistics.attributes.log.get import *
from parameters import *
from parameters import *
from util import *


def incrementing_key_generator(start=0):
    """A generator function that yields an incrementing key."""
    current = start
    while True:
        yield current
        current += 1


def add_resource_to_event(event, d, agent1s_mapping, agent2s_mapping, agent3s):
    activity = event._dict[CONCEPT]
    if activity in agent1s_mapping[d] and activity in agent2s_mapping[d]:
        event._dict[GROUP] = f"{AGENT1}, {AGENT2}"
    elif d == "IP-8" and activity in agent3s:
        event._dict[GROUP] = AGENT3
    elif activity in agent1s_mapping[d]:
        event._dict[GROUP] = AGENT1
    elif activity in agent2s_mapping[d]:
        event._dict[GROUP] = AGENT2


# Have to sample from transformed log for colliery otherwise it will give wrong instances
instance_dict = {
    "a!_1": incrementing_key_generator(),
    "a!_2": incrementing_key_generator(),
    "a!": incrementing_key_generator(),
    "a?_1": incrementing_key_generator(),
    "a?_2": incrementing_key_generator(),
    "a?": incrementing_key_generator(),
    "b!_1": incrementing_key_generator(),
    "b!_2": incrementing_key_generator(),
    "b!": incrementing_key_generator(),
    "b?_1": incrementing_key_generator(),
    "b?_2": incrementing_key_generator(),
    "b?": incrementing_key_generator(),
    "bR?": incrementing_key_generator(),
    "bR!": incrementing_key_generator(),
    "ackA?": incrementing_key_generator(),
    "ackA!": incrementing_key_generator(),
    "ackB?": incrementing_key_generator(),
    "ackB!": incrementing_key_generator(),
    "c?": incrementing_key_generator(),
    "c!": incrementing_key_generator(),
    "d?": incrementing_key_generator(),
    "d!": incrementing_key_generator(),
    "c?_1": incrementing_key_generator(),
    "c!_1": incrementing_key_generator(),
    "c?_2": incrementing_key_generator(),
    "c!_2": incrementing_key_generator(),
    "d?_1": incrementing_key_generator(),
    "d!_1": incrementing_key_generator(),
    "d?_2": incrementing_key_generator(),
    "d!_2": incrementing_key_generator(),
    "a?_u": incrementing_key_generator(),
    "a!_u": incrementing_key_generator(),
    "aR!": incrementing_key_generator(),
    "aR?": incrementing_key_generator(),
    "b?_u": incrementing_key_generator(),
    "b!_u": incrementing_key_generator()
}


def transform_to_corradini(event, d, agent1s_mapping, agent2s_mapping, agent3s):
    add_resource_to_event(event, d, agent1s_mapping, agent2s_mapping, agent3s)
    activity = event._dict[CONCEPT]
    if activity.startswith("a") and "R" not in activity and "A" not in activity and "B" not in activity:
        set_message_corradini(activity, event, "a")
    elif activity.startswith("bR"):
        set_message_corradini(activity, event, "bR")
    elif activity.startswith("aR"):
        set_message_corradini(activity, event, "aR")
    elif activity.startswith("b") and "R" not in activity:
        set_message_corradini(activity, event, "b")
    elif activity.startswith("c"):
        set_message_corradini(activity, event, "c")
    elif activity.startswith("d"):
        set_message_corradini(activity, event, "d")
    elif activity.startswith("ackA"):
        set_message_corradini(activity, event, "ackA")
    elif activity.startswith("ackB"):
        set_message_corradini(activity, event, "ackB")
    return event


def set_message_corradini(activity, event, act):
    if "?" in activity:
        event._dict[CORR_MSG_TYPE] = act
        event._dict[CORR_MSG_TYPE_ALIAS] = event._dict[CORR_MSG_TYPE]
        event._dict[CORR_COMM] = CORR_COMM_REC
        event._dict[CORR_COMM_ALIAS] = event._dict[CORR_COMM]
        event._dict[CORR_MSG_INSTANCE] = f"{event._dict[CORR_MSG_TYPE]}_{next(instance_dict[activity])}"
        event._dict[CORR_MODE] = CORR_MODE_TYPE
    else:
        event._dict[CORR_MSG_TYPE] = act
        event._dict[CORR_MSG_TYPE_ALIAS] = event._dict[CORR_MSG_TYPE]
        event._dict[CORR_COMM] = CORR_COMM_SEND
        event._dict[CORR_COMM_ALIAS] = event._dict[CORR_COMM]
        event._dict[CORR_MSG_INSTANCE] = f"{event._dict[CORR_MSG_TYPE]}_{next(instance_dict[activity])}"
        event._dict[CORR_MODE] = CORR_MODE_TYPE


def discover_collaboration_bpmn(miner_input):
    dataset_name, miner, i, r = miner_input
    curr_dir = os.getcwd()
    outpath = curr_dir + build_path(dataset_name=dataset_name,
                         miner=miner,
                         i=i,
                         r=r,
                         suffix="bpmn")[1:]
    if dataset_name == "IP-8":
        cmd = [f"{CORRADINI_PATH}run.sh"] + [
            curr_dir + build_log_path(d=dataset_name,
                           i=i,
                           r=r,
                           miner=miner + agent,
                           suffix=".xes")[1:] for agent in [AGENT1, AGENT2, AGENT3]
        ] + [outpath]
    else:
        cmd = [f"{CORRADINI_PATH}run.sh"] + [
            curr_dir + build_log_path(d=dataset_name,
                           i=i,
                           r=r,
                           miner=miner + agent,
                           suffix=".xes")[1:] for agent in [AGENT1, AGENT2]
        ] + [outpath]
    try:
        # with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True) as process:
        #    # Read and print each line of the output
        #    output_lines = []
        #    for line in process.stdout:
        #        line = line.strip()
        #        print(line)
        #        output_lines.append(line)

        # Wait for the subprocess to complete (optional)
        # process.wait()
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
        print(f"{dataset_name} - Success in Corradini mining JAR for configuration {i}, {r}: {result.stdout}.\n")
        # captured_output = '\n'.join(output_lines)
        bp = apply(outpath)
        petri = to_petri_net(bp)

        pnml_outputpath = build_path(dataset_name=dataset_name,
                                     miner=miner,
                                     i=i,
                                     r=r,
                                     suffix="pnml")
        export_net(petri[0], petri[1], pnml_outputpath, petri[2])
        return petri
    except (concurrent.futures.TimeoutError, subprocess.TimeoutExpired) as e:
        print(f"{dataset_name} - Timeout in Corradini mining JAR for configuration {i}, {r}.\n")
        return None
    except subprocess.CalledProcessError:
        print(f"{dataset_name} - Exception in Corradini mining JAR for configuration {i}, {r}.\n")
        return EXMI
    except Exception as e:
        print(
            f"{dataset_name} - Exception in calling Corradini mining for configuration {i}, {r} with error message: {str(e)}\n")
        return EXMI
