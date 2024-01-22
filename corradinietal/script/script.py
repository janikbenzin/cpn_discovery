import sys
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer

from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner

#Import log file
log = xes_importer.apply("../xes.xes")

if sys.argv[1] == "alpha":
    net, im, fm = alpha_miner.apply(log)
elif sys.argv[1] == "inductive":
    net, im, fm = inductive_miner.apply(log)
elif sys.argv[1] == "heuristics":
    net, im, fm = heuristics_miner.apply(log, parameters={heuristics_miner.Variants.CLASSIC.value.Parameters.DEPENDENCY_THRESH: 0.99})

tree = wf_net_converter.apply(net, im, fm)
from pm4py.objects.conversion.process_tree import converter
bpmn_graph = converter.apply(tree, variant=converter.Variants.TO_BPMN)
from pm4py.objects.bpmn.layout import layouter
bpmn_graph = layouter.apply(bpmn_graph)
from enum import Enum
from pm4py.objects.bpmn.exporter.variants import etree
from pm4py.util import exec_utils
class Variants(Enum):
    ETREE = etree
DEFAULT_VARIANT = Variants.ETREE
print(exec_utils.get_variant(DEFAULT_VARIANT).get_xml_string(bpmn_graph, parameters={}))



#tree = pm4py.discover_tree_inductive(log)

#from pm4py.visualization.process_tree import visualizer as pt_visualizer
#gviz = pt_visualizer.apply(tree)



#from pm4py.objects.conversion.process_tree import converter as pt_converter
#net, im, fm = pt_converter.apply(tree)

#from pm4py.visualization.petrinet import visualizer as pn_visualizer
#gviz = pn_visualizer.apply(net, im, fm)





#from pm4py.objects.petri.exporter import exporter as pnml_exporter
#pnml_exporter.apply(net, im, "petri.pnml")

