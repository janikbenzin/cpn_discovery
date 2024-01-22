import pandas as pd
import pickle

from parameters import *
import pickle

import pandas as pd

from parameters import *

MODELS = 12
DATA = [f"IP-{i + 1}" for i in range(MODELS)]
MINERS = [Miner.ocpd, Miner.health, Miner.colliery]
EXPERIMENT = "PetriNetsPaper2024_alignments_original"

with open(RESULT_PATH + f"nested_results_{EXPERIMENT}.pickle", "rb") as file:
    nested_pool_results = pickle.load(file)

# coverages_all = [item for d in nested_pool_results for item in d[LISTS][0]]
# smapes_all = [item for d in nested_pool_results for item in d[LISTS][1]]
# srmspes_all = [item for d in nested_pool_results for item in d[LISTS][2]]
# nrmses_all = [item for d in nested_pool_results for item in d[LISTS][3]]
# nmaes_all = [item for d in nested_pool_results for item in d[LISTS][4]]
precisions_true = [item for d in nested_pool_results for item in d[LISTS][5]]
recalls_true = [item for d in nested_pool_results for item in d[LISTS][6]]
# dfgs_original = {k: v for d in nested_pool_results  for k, v in d[DICTS][0].items()}
# dfgs_sample = {k: v for d in nested_pool_results  for k, v in d[DICTS][1].items()}
# sample_error_metrics = {k: v for d in nested_pool_results  for k, v in d[DICTS][2].items()}
results_temp = [{k: v for k, v in d[DICTS][3].items()} for d in nested_pool_results]
results = define_results_dict()

for d in results_temp:
    for k in d:
        for k2 in d[k]:
            results[k][k2] += d[k][k2]

precisions_temp = [{k: v for k, v in d[DICTS][6].items()} for d in nested_pool_results]
precisions = {d.name: [] for d in Miner}
for d in precisions_temp:
    for k in d:
        precisions[k] += d[k]

recalls_temp = [{k: v for k, v in d[DICTS][7].items()} for d in nested_pool_results]
recalls = {d.name: [] for d in Miner}
for d in recalls_temp:
    for k in d:
        recalls[k] += d[k]


def format_spearman(cell):
    if isinstance(cell, tuple):
        stat, p = cell
        if p < 0.001:
            return "\\textbf{" + str(round(stat, 3)) + "}"
        else:
            return str(round(stat, 3))
    elif isinstance(cell, float):
        return round(cell, 3)
    else:
        return cell



original_i = -1
original_r = 1


map_names = {
    "health": "CCHP",
    "ocpd": "OCPD",
    "colliery": "Colliery",
    "reference": "Reference",
}

map_error_codes = {
    TORQ: "t/o",
    EXQI: "ex",
    EXQ: "si",
    False: "no",
    True: "yes"
}


def reformat_cell(cell):
    if isinstance(cell, float):
        if cell in maxs_list:
            return "\\textbf{" + f"{min(round(cell, 3), 1)}" + "}"
        else:
            return f" {min(round(cell, 3), 1)}"
    else:
        try:
            return f"{map_error_codes[cell]}"
        except KeyError:
            return cell

map_metric = {
    RECALL: "R",
    PRECISION: "P"
}

maxs = {"R": {i: 0 for i in range(12)},
        "P": {i: 0 for i in range(12)}
        }

maxs_list = [maxs[k][i] for k in maxs for i in maxs[k]]

flat_data = []
for category, metrics in results.items():

    for metric_name, values in metrics.items():

        if metric_name in ['R', 'P', 'S']:  # Filtering for simplicity
            for i, value in enumerate(values):
                if isinstance(value, float) and value > maxs[metric_name][i]:
                    maxs[metric_name][i] = value
                flat_data.append([map_names[category], metric_name, i, value])
df = pd.DataFrame(flat_data, columns=['CPD', 'Metric', 'Log', 'Value'])
pivot_df = df.pivot_table(index=['CPD', 'Metric'], columns='Log', values='Value', aggfunc='first')
pivot_df = pivot_df.reindex(pd.MultiIndex.from_product(
    [pivot_df.index.get_level_values(0).unique(),
     ['R', 'P', 'S']],
    names=pivot_df.index.names))
maxs_list = [maxs[k][i] for k in maxs for i in maxs[k]]
with (open(f"{TABLE_PATH}petri_nets.tex", "w") as t):
    pivot_df.map(reformat_cell).to_latex(buf=t,
                                         float_format="{:0.3f}".format,
                                         label=f"fig:results",
                                         column_format="p{1cm}P{0.3cm}P{0.8cm}P{0.8cm}P{0.8cm}P{0.8cm}P{0.8cm}P{0.8cm}P{0.8cm}P{0.8cm}P{0.8cm}P{0.8cm}P{0.8cm}P{0.8cm}",
                                         caption=f"Evaluation results of discovering collaboration Petri nets for the 12 benchmark event logs "
                                                 f"with our discovery framework and three publicly available collaboration process discovery (CPD) techniques.")

