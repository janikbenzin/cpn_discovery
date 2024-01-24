from enum import Enum

PRECISION = 'Precision'
MODEL = 'Model'
RECALL = 'Recall'
RECALL_A = 'R'
RECALL_A_ALL = 'RA'
PRECISION_A = 'P'
SOUNDNESS = 'S'
ORIG = 'reference'
QUALITY_MODE = ""
LOG_TRADITIONAL = ""

LISTS = "lists"
DICTS = "dicts"
TORMI = "tormi"
TORQ = "torq"
EXMI = "exmi"
EXQ = "exq"
EXQG = "exqg"
EXQI = "exqi"
EXECD = "exec-d"
EXECQ = "exec-q"

JAVA17 = "/usr/lib/jvm/java-21-openjdk-21.0.1.0.12-4.rolling.fc39.x86_64/bin/java"
JAVAHEAP = '-Xmx16G'
PATH = "./nesterovartifacts/"
RESULT_PATH = "./results/"
TABLE_PATH = "./tables/"
LOG_PATH = "./artifacts/"
LIU_PATH = "./liuetal/"
CORRADINI_PATH = "./corradinietal/"


WORKERS = 1  # 4

class Miner(Enum):
    ocpd = "ocpd"
    agent = "agent"
    health = "health"
    colliery = "colliery"


EXPORT = False

CONCEPT = "concept:name"
AGENT_OT_3 = "agent_ot3"
AGENT_OT_2 = "agent_ot2"
AGENT_OT_1 = "agent_ot1"
MSG_OT_1 = "msg_a_ot1"
MSG_OT_2 = "msg_b_ot2"
MSG_OT_3 = "msg_c_ot3"
MSG_OT_4 = "msg_d_ot4"
MSG_OT_5 = "msg_aR_ot5"
MSG_OT_6 = "msg_bR_ot6"
MSG_OT_7 = "msg_ackA_ot7"
MSG_OT_8 = "msg_ackB_ot8"

MESSAGE_OTS = [MSG_OT_1, MSG_OT_2, MSG_OT_3, MSG_OT_4, MSG_OT_5, MSG_OT_6, MSG_OT_7, MSG_OT_8]

AGENT1 = "Agent1"
AGENT2 = "Agent2"
AGENT3 = "Agent3"
RES = "org:resource"
GROUP = "org:group"
CORR_COMM = "communicationMode"
CORR_COMM_ALIAS = "msgRole"
CORR_COMM_REC = "receive"
CORR_COMM_SEND = "send"
CORR_MSG_TYPE = "msgType"
CORR_MODE = "msgProtocol"
CORR_MODE_TYPE = "P2P"
CORR_MSG_TYPE_ALIAS = "msgName"
CORR_MSG_INSTANCE = "msgInstanceID"
CORR_EVENT_TYPE = "eventType"


LIU_RES = "resource"
LIU_NULL = "null"
LIU_MESSAGE_REC = "Message:Rec"
LIU_MESSAGE_SENT = "Message:Sent"

agent1_acts = [f't{i + 1}' for i in range(100)] + ["a!_1", "a!_2"]
agent2_acts = [f'e{i + 1}' for i in range(100)] + ["a?_1", "a?_2"]

# log = pm4py.read_xes(f'{PATH}{DATA[0]}/{DATA[0]}_initial_log.xes')
# log1 = filter_agent(log, values=agent1_acts)
agent1s_mapping = {
    "IP-1": [f't{i + 1}' for i in range(100)] + ["a!_1", "a!_2"],  # 1
    "IP-2": [f't{i + 1}' for i in range(100)] + ["a!_1", "a!_2", "b!"],  # 2
    "IP-3": [f't{i + 1}' for i in range(100)] + ["a!", "b!"],  # 3
    "IP-4": [f't{i + 1}' for i in range(100)] + ["a!_1", "a!_2", "b?_1", "b?_2"],  # 4
    "IP-5": [f't{i + 1}' for i in range(100)] + ["a!", "b!_1", "b!_2", "c?", "d?_1", "d?_2"],  # 5
    "IP-6": [f't{i + 1}' for i in range(100)] + ["a!", "b!_1", "b!_2", "c?", "d?_1", "d?_2"],  # 6
    "IP-7": [f't{i + 1}' for i in range(100)] + ["a?_1", "a?_2", "b!_1", "b!_2", "c!_1", "c!_2"],  # 7
    "IP-8": [f't{i + 1}' for i in range(100)] + ["a!_1", "a!_2", "bR?", "ackA?", "a?_u"],  # 8
    "IP-9": [f't{i + 1}' for i in range(100)] + ["s_1", "s_2", "s_3", "s_4", "a!_1", "a!_2", "b?_1", "b?_2"],  # 9
    "IP-10": [f't{i + 1}' for i in range(100)] + ["s_1", "s_2", "a!", "b?_1", "b?_2"],  # 10
    "IP-11": [f't{i + 1}' for i in range(100)] + ["s", "a!_1", "a!_2", "b?"],  # 11
    "IP-12": [f't{i + 1}' for i in range(100)] + ["s", "a!", "b?"],  # 12
}
agent2s_mapping = {
    "IP-1": [f'e{i + 1}' for i in range(100)] + ["a?_1", "a?_2"],  # 1
    "IP-2": [f'q{i + 1}' for i in range(100)] + ["a?", "b?_1", "b?_2"],  # 2
    "IP-3": [f'q{i + 1}' for i in range(100)] + ["a?", "b?"],  # 3
    "IP-4": [f'e{i + 1}' for i in range(100)] + ["a?", "b!_1", "b!_2"],  # 4
    "IP-5": [f'q{i + 1}' for i in range(100)] + ["a?_1", "a?_2", "b?", "c!", "d!"],  # 5
    "IP-6": [f'q{i + 1}' for i in range(100)] + ["a?", "b?", "c!_1", "c!_2", "d!"],  # 6
    "IP-7": [f'q{i + 1}' for i in range(100)] + ["a!_1", "a!_2", "b?_1", "b?_2", "c?_1", "c?_2"],  # 7
    "IP-8": [f'q{i + 1}' for i in range(100)] + ["a?", "bR!", "ackA!", "b?", "aR!", "ackB!"],  # 8
    "IP-9": [f'q{i + 1}' for i in range(100)] + ["s_1", "s_2", "s_3", "s_4", "a?", "b!_1", "b!_2"],  # 9
    "IP-10": [f'q{i + 1}' for i in range(100)] + ["s_1", "s_2", "a?_1", "a?_2", "b!_1", "b!_2"],  # 10
    "IP-11": [f'q{i + 1}' for i in range(100)] + ["s", "a?_1", "a?_2", "b!_1", "b!_2"],  # 11
    "IP-12": [f'q{i + 1}' for i in range(100)] + ["s", "a?", "b!_1", "b!_2"],  # 12
}

agent3s = [f'r{i + 1}' for i in range(100)] + ["b!_1", "b!_2", "b?_u", "aR?", "ackB?"]  # 8


def define_results_dict():
    ret = {
        d.name: {RECALL: [],
                 PRECISION: [],
                 RECALL_A_ALL: [],
                 RECALL_A: [],
                 PRECISION_A: [],
                 SOUNDNESS: [],
                 TORMI: [],
                 TORQ: [],
                 EXMI: [],
                 EXQ: [],
                 EXECD: [],
                 EXECQ: []} for d in Miner
    }
    ret[ORIG] = {RECALL: [],
                 PRECISION: [],
                 RECALL_A_ALL: [],
                 RECALL_A: [],
                 PRECISION_A: [],
                 SOUNDNESS: [],
                 TORMI: [],
                 TORQ: [],
                 EXMI: [],
                 EXQ: [],
                 EXECD: [],
                 EXECQ: []}
    return ret
