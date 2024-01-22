import concurrent.futures
import time

from generic_transformation import *


def execute_evaluate_timed_collaboration_miner(sample, results, precisions, recalls, timed_miner_function, miner_input,
                                               d, i, r, miner, only_alignments=False):
    pnml_path = build_path(d, miner, i, r, "pnml")
    if os.path.exists(pnml_path):
        sample_ocpn = pm4py.read_pnml(pnml_path)
    else:
        with concurrent.futures.ThreadPoolExecutor() as executor_ocpd:
            future_ocpd = executor_ocpd.submit(timed_miner_function, miner_input)
            d_start_time = time.time()
            try:
                sample_ocpn = future_ocpd.result()
            except (concurrent.futures.TimeoutError, subprocess.TimeoutExpired) as e:
                print(f"{d} - Timeout in mining for configuration {miner}, {i}, {r}.\n")
                sample_ocpn = None
            d_end_time = time.time()
        # sample_ocpn = pm4py.discover_oc_petri_net(sample_ocel)
        results[miner][EXECD].append(d_end_time - d_start_time)
    if only_alignments:
        # Check for im, fm
        net = sample_ocpn[0]
        im = sample_ocpn[1]
        fm = sample_ocpn[2]
        if miner == Miner.ocpd.name:
            # Fix the wrong parsing of silent transitions by pm4py
            for t in net.transitions:
                if "tau" in t.label:
                    t.label = None
        if len(im) == 0 and len(fm) == 0:
            im = pm4py.objects.petri_net.utils.initial_marking.discover_initial_marking(net)
            fm = pm4py.objects.petri_net.utils.final_marking.discover_final_marking(net)
        print(f"{d} - Transforming net of {miner} to wf-net...\n")
        wf_net = transform_to_wf_net(net, im, fm)
        j = int(d.split("-")[1]) - 1
        print(f"{d} - Checking soundness for {miner} ...\n")
        s = pm4py.algo.analysis.woflan.algorithm.apply(*wf_net,
                                                           parameters={
                                                               pm4py.algo.analysis.woflan.algorithm.Parameters.RETURN_ASAP_WHEN_NOT_SOUND: True
                                                           })
        print(f"{d} - {miner} sound: {s}...\n")
        results[miner][SOUNDNESS].append(s)
        export_list_to_json(results[miner][SOUNDNESS], build_result_path(miner, d, i, "soundness", r))


        print(f"{d} - Computing alignment-based fitness for {miner} ...\n")
        try:
            align_fitness = pm4py.fitness_alignments(sample, *wf_net)
            results[miner][RECALL_A_ALL].append(align_fitness)
            results[miner][RECALL_A].append(align_fitness['log_fitness'])
            align_fitness_score = align_fitness['log_fitness']
        except Exception as e:
            align_fitness_score = EXQI
            results[miner][RECALL_A_ALL].append(EXQI)
            results[miner][RECALL_A].append(EXQI)
        print(f"{d} - {miner} fitness: {align_fitness_score}...\n")
        export_list_to_json(results[miner][RECALL_A], build_result_path(miner, d, i, "recall_align", r))
        print(f"{d} - Computing alignment-based precision for {miner} ...\n")
        try:
            align_precision = pm4py.conformance.precision_alignments(sample, *wf_net)
            results[miner][PRECISION_A].append(align_precision)
        except Exception as e:
            align_precision = EXQI
            results[miner][PRECISION_A].append(align_precision)
        print(f"{d} - {miner} precision: {align_precision}...\n")
        export_list_to_json(results[miner][PRECISION_A], build_result_path(miner, d, i, "precision_align", r))
    else:
            # EXCEPTION this should not happen
        print(f"{d} - Something is wrong for {i}, {r}, {miner}")
        precisions[miner].append(EXMI)
        recalls[miner].append(EXMI)
        results[miner][PRECISION].append(EXMI)
        results[miner][RECALL].append(EXMI)
        results[miner][EXMI].append((d, i, r))
