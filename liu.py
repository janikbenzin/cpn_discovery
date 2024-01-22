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

import pm4py
from pm4py.objects.log.obj import EventStream
from pm4py.objects.log.util.sampling import sample_log
from pm4py.statistics.attributes.log.get import *
from parameters import *
from util import *


def add_resource_to_event(event, d, agent1s_mapping, agent2s_mapping, agent3s):
    activity = event._dict[CONCEPT]
    if activity in agent1s_mapping[d] and activity in agent2s_mapping[d]:
        event._dict[RES] = f"{AGENT1}, {AGENT2}"
    elif d == "IP-8" and activity in agent3s:
        event._dict[RES] = AGENT3
    elif activity in agent1s_mapping[d]:
        event._dict[RES] = AGENT1
    elif activity in agent2s_mapping[d]:
        event._dict[RES] = AGENT2
    event._dict[LIU_RES] = LIU_NULL

def transform_to_liu(event, d, agent1s_mapping, agent2s_mapping, agent3s):
    add_resource_to_event(event, d, agent1s_mapping, agent2s_mapping, agent3s)
    activity = event._dict[CONCEPT]
    if activity.startswith("a"):
        if "?" in activity:
            if len(activity) > 2:
                event._dict[LIU_MESSAGE_REC] = "a" + activity[2:]
                event._dict[LIU_MESSAGE_SENT] = LIU_NULL
            else:
                event._dict[LIU_MESSAGE_REC] = "a"
                event._dict[LIU_MESSAGE_SENT] = LIU_NULL
        else:
            if len(activity) > 2:
                event._dict[LIU_MESSAGE_REC] = LIU_NULL
                event._dict[LIU_MESSAGE_SENT] = "a" + activity[2:]
            else:
                event._dict[LIU_MESSAGE_REC] = LIU_NULL
                event._dict[LIU_MESSAGE_SENT] = "a"
    elif activity.startswith("b"):
        if "?" in activity:
            if len(activity) > 2:
                event._dict[LIU_MESSAGE_REC] = "b" + activity[2:]
                event._dict[LIU_MESSAGE_SENT] = LIU_NULL
            else:
                event._dict[LIU_MESSAGE_REC] = "b"
                event._dict[LIU_MESSAGE_SENT] = LIU_NULL
        else:
            if len(activity) > 2:
                event._dict[LIU_MESSAGE_REC] = LIU_NULL
                event._dict[LIU_MESSAGE_SENT] = "b" + activity[2:]
            else:
                event._dict[LIU_MESSAGE_REC] = LIU_NULL
                event._dict[LIU_MESSAGE_SENT] = "b"
    elif activity.startswith("c"):
        if "?" in activity:
            if len(activity) > 2:
                event._dict[LIU_MESSAGE_REC] = "c" + activity[2:]
                event._dict[LIU_MESSAGE_SENT] = LIU_NULL
            else:
                event._dict[LIU_MESSAGE_REC] = "c"
                event._dict[LIU_MESSAGE_SENT] = LIU_NULL
        else:
            if len(activity) > 2:
                event._dict[LIU_MESSAGE_REC] = LIU_NULL
                event._dict[LIU_MESSAGE_SENT] = "c" + activity[2:]
            else:
                event._dict[LIU_MESSAGE_REC] = LIU_NULL
                event._dict[LIU_MESSAGE_SENT] = "c"
    elif activity.startswith("d"):
        if "?" in activity:
            if len(activity) > 2:
                event._dict[LIU_MESSAGE_REC] = "d" + activity[2:]
                event._dict[LIU_MESSAGE_SENT] = LIU_NULL
            else:
                event._dict[LIU_MESSAGE_REC] = "d"
                event._dict[LIU_MESSAGE_SENT] = LIU_NULL
        else:
            if len(activity) > 2:
                event._dict[LIU_MESSAGE_REC] = LIU_NULL
                event._dict[LIU_MESSAGE_SENT] = "d" + activity[2:]
            else:
                event._dict[LIU_MESSAGE_REC] = LIU_NULL
                event._dict[LIU_MESSAGE_SENT] = "d"
    else:
        event._dict[LIU_MESSAGE_SENT] = LIU_NULL
        event._dict[LIU_MESSAGE_REC] = LIU_NULL
    return event

def discover_crosspn(miner_input):
    dataset_name, miner, i, r = miner_input
    outpath = build_path(dataset_name=dataset_name,
                         miner=miner,
                         i=i,
                         r=r,
                         suffix="pnml")
    cmd = ["cp",
           build_log_path(d=dataset_name,
                          miner=miner,
                          i=i,
                          r=r,
                          suffix=".xes"),
           build_log_path(d=dataset_name,
                          miner=miner,
                          i=i,
                          r=r,
                          suffix=".xes") + ".beforezip"]
    subprocess.run(cmd)
    cmd = ["gzip", "-f",
           build_log_path(d=dataset_name,
                                  miner=miner,
                                  i=i,
                                  r=r,
                          suffix=".xes")]
    subprocess.run(cmd)
    cmd = ["mv",
           build_log_path(d=dataset_name,
                          miner=miner,
                          i=i,
                          r=r,
                          suffix=".xes") + ".beforezip",
           build_log_path(d=dataset_name,
                          miner=miner,
                          i=i,
                          r=r,
                          suffix=".xes")]
    subprocess.run(cmd)

    cmd = [f"{LIU_PATH}run.sh",
           "-log", build_log_path(d=dataset_name,
                                  miner=miner,
                                  i=i,
                                  r=r,
                                  suffix=".xes") + ".gz",
           "-target", build_path(dataset_name=dataset_name,
                                 miner=miner,
                                 i=i,
                                 r=r,
                                 suffix="pnml")]
    print(cmd)
    print('\n')
    # Open a subprocess with stdout as a pipe
    try:
        #with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True) as process:
        #    # Read and print each line of the output
        #    output_lines = []
        #    for line in process.stdout:
        #        line = line.strip()
        #        print(line)
        #        output_lines.append(line)

        # Wait for the subprocess to complete (optional)
        #process.wait()
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
        print(f"{dataset_name} - Success in Liu mining JAR for configuration {i}, {r}: {result.stdout}.\n")
        #captured_output = '\n'.join(output_lines)
        return pm4py.read_pnml(outpath)
    except (concurrent.futures.TimeoutError, subprocess.TimeoutExpired) as e:
        print(f"{dataset_name} - Timeout in Liu mining JAR for configuration {i}, {r}.\n")
        return None
    except subprocess.CalledProcessError:
        print(f"{dataset_name} - Exception in Liu mining JAR for configuration {i}, {r}.\n")
        return EXMI
    except Exception as e:
        print(f"{dataset_name} - Exception in calling Liu mining for configuration {i}, {r} with error message: {str(e)}\n")
        return EXMI

