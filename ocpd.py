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


def convert_to_ocel_with_transformations(log_to_ocpd, dataset_name, agent1s_mapping, agent2s_mapping, agent3s, i=-1,
                                         r=-1.0):
    for t in log_to_ocpd._list:
        prefix = t.attributes[CONCEPT].split(" ")[1]
        # seen_messages_sent = set()
        # seen_message_rec = set()
        sc = {MSG_OT_1: 0,
              MSG_OT_2: 0,
              MSG_OT_3: 0,
              MSG_OT_4: 0,
              MSG_OT_5: 0,
              MSG_OT_6: 0,
              MSG_OT_7: 0,
              MSG_OT_8: 0}
        rc = {MSG_OT_1: 0,
              MSG_OT_2: 0,
              MSG_OT_3: 0,
              MSG_OT_4: 0,
              MSG_OT_5: 0,
              MSG_OT_6: 0,
              MSG_OT_7: 0,
              MSG_OT_8: 0}
        for e in t._list:
            # Agents with sync activities
            activity = e._dict[CONCEPT]
            if activity in agent1s_mapping[dataset_name] and activity in agent2s_mapping[dataset_name]:
                e._dict[AGENT_OT_1] = prefix + "_agent1"
                e._dict[AGENT_OT_2] = prefix + "_agent2"
                e._dict[AGENT_OT_3] = ""
            elif activity in agent1s_mapping[dataset_name]:
                e._dict[AGENT_OT_1] = prefix + "_agent1"
                e._dict[AGENT_OT_2] = ""
                e._dict[AGENT_OT_3] = ""
            elif activity in agent2s_mapping[dataset_name]:
                e._dict[AGENT_OT_1] = ""
                e._dict[AGENT_OT_2] = prefix + "_agent2"
                e._dict[AGENT_OT_3] = ""
            elif dataset_name == "IP-8" and activity in agent3s:
                e._dict[AGENT_OT_1] = ""
                e._dict[AGENT_OT_2] = ""
                e._dict[AGENT_OT_3] = prefix + "_agent3"
            # Message exchanges

            if activity.startswith("a") and "R" not in activity and "A" not in activity and "B" not in activity:
                # OT1
                set_message_ot(activity, e, prefix, rc, sc, MSG_OT_1)
            elif activity.startswith("bR"):
                set_message_ot(activity, e, prefix, rc, sc, MSG_OT_6)
            elif activity.startswith("aR"):
                set_message_ot(activity, e, prefix, rc, sc, MSG_OT_5)
            elif activity.startswith("b") and "R" not in activity:
                set_message_ot(activity, e, prefix, rc, sc, MSG_OT_2)
            elif activity.startswith("c"):
                set_message_ot(activity, e, prefix, rc, sc, MSG_OT_3)
            elif activity.startswith("d"):
                set_message_ot(activity, e, prefix, rc, sc, MSG_OT_4)
            elif activity.startswith("ackA"):
                set_message_ot(activity, e, prefix, rc, sc, MSG_OT_7)
            elif activity.startswith("ackB"):
                set_message_ot(activity, e, prefix, rc, sc, MSG_OT_8)
            else:
                for ot in MESSAGE_OTS:
                    e._dict[ot] = ""
                # message_types_rec = [cname for cname in agent1s_mapping + agent2s_mapping if "?" in cname]
                # message_types_send = [cname for cname in agent1s_mapping + agent2s_mapping if "!" in cname]

    ocel_log = pm4py.convert_log_to_ocel(log_to_ocpd, activity_column=CONCEPT,
                                         object_types=[AGENT_OT_1, AGENT_OT_2, AGENT_OT_3, MSG_OT_1, MSG_OT_2, MSG_OT_3,
                                                       MSG_OT_4, MSG_OT_5, MSG_OT_6, MSG_OT_7, MSG_OT_8],
                                         obj_separator=",")
    pm4py.write_ocel_json(ocel_log, build_log_path(dataset_name, i, r))
    return ocel_log


def set_message_ot(activity, e, prefix, rc, sc, set_ot):
    if "?" in activity:
        # seen_message_rec.add(activity)
        e._dict[set_ot] = f"{set_ot}_{prefix}_{rc[set_ot]}"
        rc[set_ot] += 1
    else:
        # seen_messages_sent.add(activity)
        e._dict[set_ot] = f"{set_ot}_{prefix}_{sc[set_ot]}"
        sc[set_ot] += 1
    for ot in MESSAGE_OTS:
        if ot != set_ot:
            e._dict[ot] = ""


def merge_petri_nets_in_ocpn(ocpn, dataset_name, i=-1, r=-1.0):
    from pm4py.objects.petri_net.obj import PetriNet
    net = PetriNet(f'{dataset_name}_sample_{i}_ratio_{r}')
    source_names = []
    sink_names = []
    labels = set()
    transitions = {}
    old_arcs = set()
    for pname, pn in ocpn["petri_nets"].items():
        for p in pn[0].places:
            if p.name == "source":
                new_name = f'{p.name}_{pname}'
                p.name = new_name
                source_names = source_names + [new_name]
                net.places.add(p)
            elif p.name == "sink":
                # new_name = f'{p.name}_{pname}'
                # p.name = new_name
                new_name = f'{p.name}_{pname}'
                p.name = new_name
                sink_names = sink_names + [new_name]
                net.places.add(p)
            else:
                new_name = f'{p.name}_{pname}'
                p.name = new_name
                net.places.add(p)
        for t in pn[0].transitions:
            if t.label in labels:
                # Synchronuous transition already added, so skip it for other object types
                existing_trans = [to for to in net.transitions if to.label == t.label][0]
                if pname not in transitions:
                    transitions[pname] = {t.label: t}
                else:
                    transitions[pname][t.label] = t
                old_arcs = old_arcs.union(t.in_arcs)
                old_arcs = old_arcs.union(t.out_arcs)
                # Add new arcs
                for old_arc in t.in_arcs:
                    new_arc = PetriNet.Arc(old_arc.source, existing_trans, 1)
                    net.arcs.add(new_arc)
                    old_arc.source.out_arcs.add(new_arc)
                    if old_arc in old_arc.source.out_arcs:
                        old_arc.source.out_arcs.remove(old_arc)
                for old_arc in t.out_arcs:
                    new_arc = PetriNet.Arc(existing_trans, old_arc.target, 1)
                    net.arcs.add(new_arc)
                    old_arc.target.in_arcs.add(new_arc)
                    if old_arc in old_arc.target.in_arcs:
                        old_arc.target.in_arcs.remove(old_arc)
            else:
                net.transitions.add(t)
                if t.label is not None:
                    labels.add(t.label)
                else:
                    t.name = f'{t.name}_{pname}'
                    t.label = ''
        for a in pn[0].arcs:
            if a not in old_arcs:
                net.arcs.add(a)
    initial_marking = pm4py.generate_marking(net, {n: 1 for n in source_names})
    final_marking = pm4py.generate_marking(net, {n: 1 for n in sink_names})
    #pm4py.save_vis_petri_net(net, initial_marking, final_marking,
    #                         build_path(dataset_name, Miner.ocpd.name, i, r, "svg"))
    pm4py.write_pnml(net, initial_marking, final_marking,
                     build_path(dataset_name, Miner.ocpd.name, i, r, "pnml"))
    return net, initial_marking, final_marking


def discover_ocpd(miner_input):
    ocel, d, i, r = miner_input
    try:
        sample_ocpn = pm4py.discover_oc_petri_net(ocel)
        sample_ocpn_pnml = merge_petri_nets_in_ocpn(sample_ocpn, d, i, r)
        return sample_ocpn_pnml
    except TimeoutError:
        return None
    except Exception as e:
        return str(e)
