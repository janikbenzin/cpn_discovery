import multiprocessing

from ocpd import *
from timed_execution import *
from modified_pm4py_pnml_import import import_net
import traceback

MODELS = 12
DATA = [f"IP-{i + 1}" for i in range(MODELS)]
EXPERIMENT = "PetriNetsPaper2024_alignments_original"
MINERS = [Miner.ocpd, Miner.colliery, Miner.health]
ORIGINAL = True

def sampling_execution(input_tuple):
    pns = {}
    logs = {}
    # Parallelize at dataset level
    model_no, d, ec = input_tuple
    dfgs_original = {}
    dfgs_sample = {}
    sample_error_metrics = {}
    coverages_all = []
    smapes_all = []
    srmspes_all = []
    nrmses_all = []
    nmaes_all = []
    results = define_results_dict()

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
    if ORIGINAL:
        print(f"Discovering dfg for original log {d}\n")
        dfgs_original[d] = pm4py.discover_dfg(log)


        # Model quality with original log
        # start_time = time.time()
        net = pns[d][0]
        im = pns[d][1]
        fm = pns[d][2]
        if im is None or len(im) == 0:
            im = pm4py.objects.petri_net.utils.initial_marking.discover_initial_marking(net)
        if fm is None or len(fm) == 0:
            fm = pm4py.objects.petri_net.utils.final_marking.discover_final_marking(net)
        print(f"{d} - Transforming original net to wf-net...\n")
        # precision_true, recall_true = execute_extract_precision_recall(d, original_i, original_r, '')
        # end_time = time.time()
        wf_net = transform_to_wf_net(net, im, fm)
        s = pm4py.algo.analysis.woflan.algorithm.apply(*wf_net,
                                                       parameters={
                                                           pm4py.algo.analysis.woflan.algorithm.Parameters.RETURN_ASAP_WHEN_NOT_SOUND: True
                                                       })
        results[ORIG][SOUNDNESS].append(s)
        print(f"{d} - original sound: {s}...\n")
        try:
            align_fitness = pm4py.fitness_alignments(log, *wf_net)
            results[ORIG][RECALL_A_ALL].append(align_fitness)
            results[ORIG][RECALL_A].append(align_fitness['log_fitness'])
            align_fitness_score = align_fitness['log_fitness']
        except Exception as e:
            align_fitness_score = EXQI
            results[ORIG][RECALL_A_ALL].append(EXQI)
            results[ORIG][RECALL_A].append(EXQI)
        print(f"{d} - original fitness: {align_fitness_score}...\n")
        try:
            align_precision = pm4py.conformance.precision_alignments(log, *wf_net)
            results[ORIG][PRECISION_A].append(align_precision)
        except Exception as e:
            align_precision = EXQI
            results[ORIG][PRECISION_A].append(align_precision)
        print(f"{d} - original precision: {align_precision}...\n")
    # results[ORIG][PRECISION].append(precision_true)
    #results[ORIG][RECALL].append(recall_true)
    # results[ORIG][EXECQ].append(end_time - start_time)
    # precisions_true.append(precision_true)
    # recalls_true.append(recall_true)
    # print(f"{d} - Original metrics: Precision, recall: {precision_true}, {recall_true}\n")

    # OCPD

    # true_ocpn = discover_ocpd(true_ocel)
    # true_ocpn_pnml = merge_petri_nets_in_ocpn(true_ocpn, d, original_i, original_r)
    # precision, recall = execute_extract_precision_recall(d, original_i, original_r, miner)
    # precisions[miner].append(precision)
    # recalls[miner].append(recall)
    # results[miner][PRECISION].append(precision)
    # results[miner][RECALL].append(recall)

    # OCPD
    if Miner.health in MINERS:
        print(f"{d} - Original log: HEALTH starting...\n")
        miner = Miner.health.name
        try:
            convert_to_xes_with_meta_transformations(log, d, agent1s_mapping, agent2s_mapping, agent3s,
                                                     original_i, original_r, miner)
            execute_evaluate_timed_collaboration_miner(
                sample=log,
                results=results,
                precisions=precisions,
                recalls=recalls,
                timed_miner_function=discover_crosspn,
                miner_input=(d, miner, original_i, original_r),
                d=d,
                i=original_i,
                r=original_r,
                miner=miner,
                only_alignments=True
            )
        except Exception as e:
            miner_exception(d, e, original_i, miner, precisions, original_r, recalls, results)
    if Miner.colliery in MINERS:
        print(f"{d} - Original log: Colliery starting...\n")
        miner = Miner.colliery.name
        try:
            convert_to_xes_with_meta_transformations(log, d, agent1s_mapping, agent2s_mapping, agent3s,
                                                     original_i, original_r, miner)
            execute_evaluate_timed_collaboration_miner(
                sample=log,
                results=results,
                precisions=precisions,
                recalls=recalls,
                timed_miner_function=discover_collaboration_bpmn,
                miner_input=(d, miner, original_i, original_r),
                d=d,
                i=original_i,
                r=original_r,
                miner=miner,
                only_alignments=True
            )
        except Exception as e:
            miner_exception(d, e, original_i, miner, precisions, original_r, recalls, results)

    if Miner.ocpd in MINERS:
        print(f"{d} - Original log: OCPD starting...\n")
        miner = Miner.ocpd.name
        try:
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
        except Exception as e:
            miner_exception(d, e, original_i, miner, precisions, original_r, recalls, results)
    # Liu et al health
    return {LISTS: [coverages_all, smapes_all, srmspes_all, nrmses_all, nmaes_all, precisions_true,
                    recalls_true],
            DICTS: [dfgs_original, dfgs_sample, sample_error_metrics, results, precisions, recalls]}


def miner_exception(d, e, i, miner, precisions, r, recalls, results):
    print(f"{d} - Exception in {miner}: {str(e)}\n")
    traceback.print_exc()
    # EXCEPTION
    precisions[miner].append(EXMI)
    recalls[miner].append(EXMI)
    results[miner][PRECISION].append(EXMI)
    results[miner][RECALL].append(EXMI)
    results[miner][EXMI].append((d, i, r))


if __name__ == '__main__':
    SAMPLING_COLLABORATION_INPUT = [(model_no, d, ec) for model_no, d, ec in
                                    zip(range(len(DATA)), DATA, [100 * i for i in range(len(DATA))])]
    with multiprocessing.Pool(processes=WORKERS) as pool:
        nested_pool_results = pool.map(sampling_execution, SAMPLING_COLLABORATION_INPUT)
        import pickle
        with open(RESULT_PATH + f"nested_results_{EXPERIMENT}.pickle", "wb") as file:
            pickle.dump(nested_pool_results, file)
