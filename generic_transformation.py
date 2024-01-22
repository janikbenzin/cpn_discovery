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
from liu import *
from corradini import *

def filter_agent(log: EventLog, values: List[str],
                 parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Filter log by keeping only events with an attribute value that belongs to the provided values list

    Parameters
    -----------
    log
        log
    values
        Allowed attributes
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log
            Parameters.POSITIVE -> Indicate if events should be kept/removed

    Returns
    -----------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    conversion_parameters = copy(parameters)
    conversion_parameters["deepcopy"] = False

    stream = log_converter.apply(log, variant=log_converter.TO_EVENT_STREAM, parameters=conversion_parameters)

    stream = EventStream(list(filter(lambda x: x["concept:name"] in values, stream)))
    filtered_log = log_converter.apply(stream, variant=log_converter.Variants.TO_EVENT_LOG,
                                       parameters=conversion_parameters)

    return filtered_log

def convert_to_xes_with_meta_transformations(sample, d, agent1s_mapping, agent2s_mapping, agent3s,
                                             i, r, miner,
                                             parameters: Optional[Dict[Union[str, Parameters], Any]] = None):
    if parameters is None:
        parameters = {}

    conversion_parameters = copy(parameters)
    conversion_parameters["deepcopy"] = True

    stream = log_converter.apply(sample, variant=log_converter.TO_EVENT_STREAM, parameters=conversion_parameters)
    if miner == Miner.health.name:
        transformer = partial(transform_to_liu, d=d, agent1s_mapping=agent1s_mapping, agent2s_mapping=agent2s_mapping,
                              agent3s=agent3s)
    elif miner == Miner.colliery.name:
        transformer = partial(transform_to_corradini, d=d, agent1s_mapping=agent1s_mapping,
                              agent2s_mapping=agent2s_mapping, agent3s=agent3s)
    else:
        transformer = lambda e: e
    stream = EventStream(list(map(transformer, stream)))
    transformed_log = log_converter.apply(stream, variant=log_converter.Variants.TO_EVENT_LOG,
                                          parameters=conversion_parameters)
    del stream
    if miner != Miner.colliery.name:
        pm4py.write_xes(transformed_log, build_log_path(d=d,
                                                        i=i,
                                                        r=r,
                                                        miner=miner))
    else:
        agent1_log = filter_agent(transformed_log, values=agent1s_mapping[d])
        if d == "IP-8":
            agent3_log = filter_agent(transformed_log, values=agent3s)
            pm4py.write_xes(transformed_log, build_log_path(d=d,
                                                            i=i,
                                                            r=r,
                                                            miner=miner + AGENT3))
        # Agent 2
        agent2_log = filter_agent(transformed_log, values=agent2s_mapping[d])
        pm4py.write_xes(agent1_log, build_log_path(d=d,
                                                   i=i,
                                                   r=r,
                                                   miner=miner + AGENT1))
        pm4py.write_xes(agent2_log, build_log_path(d=d,
                                                   i=i,
                                                   r=r,
                                                   miner=miner + AGENT2))
    del transformed_log


def transform_to_wf_net(net: PetriNet, i_m: Marking, f_m: Marking):
    source_place_names = [s for s in i_m]
    sink_place_names = [s for s in f_m]
    global_source = PetriNet.Place(f"global_source")
    net.places.add(global_source)
    global_sink = PetriNet.Place("global_sink")
    net.places.add(global_sink)
    im = Marking()
    fm = Marking()
    im[global_source] = 1
    fm[global_sink] = 1
    transition1 = PetriNet.Transition(name="from_global_source", label=None)
    transition2 = PetriNet.Transition(name="to_global_sink", label=None)
    net.transitions.add(transition1)
    net.transitions.add(transition2)
    add_arc_from_to(global_source, transition1, net)
    add_arc_from_to(transition2, global_sink, net)
    for p in net.places:
        if p in source_place_names:
            add_arc_from_to(transition1, p, net)
        if p in sink_place_names:
            add_arc_from_to(p, transition2, net)

    return net, im, fm