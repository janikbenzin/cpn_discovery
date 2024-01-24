import multiprocessing

from ocpd import *
from timed_execution import *
from modified_pm4py_pnml_import import import_net

MODELS = 12
DATA = [f"IP-{i + 1}" for i in range(MODELS)]
EXPERIMENT = "PetriNetsPaper2024_alignments_original"
MINERS = [Miner.ocpd, Miner.health, Miner.colliery]

pns = {}
logs = {}
    # Parallelize at dataset level

dfgs_original = {}
dfgs_sample = {}
sample_error_metrics = {}
coverages_all = []
smapes_all = []
srmspes_all = []
nrmses_all = []
nmaes_all = []
results = define_results_dict()
d = "IP-8"
precisions = {d.name: [] for d in Miner}
precisions_true = []
recalls = {d.name: [] for d in Miner}
recalls_true = []
recalls_a = {d.name: [] for d in Miner}
recalls_a_true = []
coverages = []
smapes = []
srmspes = []
nrmses = []
nmaes = []
print(f"Reading Petri net: {PATH}{d}/{d}_ref_model.pnml\n")
pns[d] = import_net(f"{PATH}{d}/{d}_ref_model.pnml")
try:
    log_read = pm4py.read_xes(f'{PATH}{d}/{d}_init_log.xes')
except:
    log_read = pm4py.read_xes(f'{PATH}{d}/{d}_initial_log.xes')
conversion_parameters = dict(deepcopy=False)
original_i = -1
original_r = 1
log = log_converter.apply(log_read, variant=log_converter.TO_EVENT_LOG, parameters=conversion_parameters)


miner = Miner.ocpd.name

true_ocel = convert_to_ocel_with_transformations(log, d, agent1s_mapping, agent2s_mapping, agent3s,
                                                             original_i, original_r)
execute_evaluate_timed_collaboration_miner(
                sample=log,
                results=results,
                precisions=precisions,
                recalls=recalls,
                timed_miner_function=discover_ocpd,
                miner_input=(true_ocel, d, original_i, original_r),
                d=d,
                i=original_i,
                r=original_r,
                miner=miner,
                only_alignments=True
            )
