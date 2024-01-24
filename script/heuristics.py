import sys
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.wf_net import converter as wf_net_converter
from pm4py.objects.bpmn.layout import layouter
import pm4py

#Import log file
log = xes_importer.apply(sys.argv[1])
#Discover petrinet
net, im, fm =  pm4py.discover_petri_net_heuristics(log, dependency_threshold=(float(sys.argv[2])), and_threshold=(float(sys.argv[2])), loop_two_threshold=(float(sys.argv[3])))#, parameters={heuristics_miner.Variants.CLASSIC.value.Parameters.ACTIVITY_KEY: "customClassifier"})

#Tree transformation
tree = wf_net_converter.apply(net, im, fm, variant=wf_net_converter.Variants.TO_BPMN)

#Make BPMN layout
bpmn_graph = layouter.apply(tree)
#BPMN to string
from enum import Enum
from pm4py.objects.bpmn.exporter.variants import etree
from pm4py.util import exec_utils
class Variants(Enum):
    ETREE = etree
DEFAULT_VARIANT = Variants.ETREE
print(exec_utils.get_variant(DEFAULT_VARIANT).get_xml_string(bpmn_graph, parameters={}))

