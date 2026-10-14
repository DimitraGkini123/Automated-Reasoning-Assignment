import math
import pandas as pd
from oxidd import bdd

# ==================================================== DIABASMA FILES MOGGER SE GAMAW ==================================================== #

NODES_FILE = "C:/Users/user/Downloads/graphs/congress_nodes.csv"
EDGES_FILE = "C:/Users/user/Downloads/graphs/congress_edges.csv"

nodes_df = pd.read_csv(NODES_FILE, sep=r"\s+")
edges_df = pd.read_csv(EDGES_FILE, sep=r"\s+")

nodes_df.columns = nodes_df.columns.str.strip()
edges_df.columns = edges_df.columns.str.strip()

nodes_df["id"] = nodes_df["id"].astype(int)
edges_df["source"] = edges_df["source"].astype(int)
edges_df["target"] = edges_df["target"].astype(int)

node_ids = set(nodes_df["id"]) #Μετράω unique ids, to set() αφαιρεί duplicates

num_nodes = len(node_ids)
num_edges = len(edges_df)

num_bits = math.ceil(math.log2(num_nodes + 1)) #Ceil() kanei roundup, log2 gia binary representation kai node+1, giati exw vars apo 0 ews n, ara n+1 vars

print("Graph information")
print("-----------------")
print(f"Unique IDs: {num_nodes}")
print(f"Edges: {num_edges}")
print(f"Bits per node ID: {num_bits}")

# ==================================================== START OF A ==================================================== #

# ==================================================== Transitions kai kala ==================================================== #

variable_names = ([f"x{i}" for i in range(num_bits)] + [f"y{i}" for i in range(num_bits)])

manager = bdd.BDDManager(1_000_000, 100_000, 4)
manager.add_named_vars(variable_names) #Den einai int, ara vazw to named

source_vars = [manager.var(i) for i in range(num_bits)] #0 me 8
target_vars = [manager.var(num_bits + i) for i in range(num_bits)] # 9 me 18 

#x0 me x8 kai y0 me y8 (0 me 8 kai 9 me 18). thelw 18 bit gia kathe trans, 9 gia source kai 9 gia target 

# ==================================================== x kai not x, y kai not y representation ==================================================== #

def encode_id(node_id, variables):

    temp1 = format(node_id, f"0{num_bits}b") #metatrepei kathe node_id se binary format 000000 or 010101010 etc. me padded 0s if needed
    representation = None

    for i in range(num_bits):
        if temp1[i] == "1":
            temp2 = variables[i]
        else:
            temp2 = ~variables[i] # To ~ einai to not profanws

        if representation is None:
            representation = temp2
        else:
            representation = representation & temp2

    return representation

#Ksekinaw apo 0 se 4
#To kanw apo 0000 se 0101
#se NOTx0 NOTx1 NOTx2 NOTx3 se NOTy0 y1 NOTy2 y3
#se 1 string !x0!x1!x2!x3!y0y1!y2y3

# ==================================================== TRANSITION BDD CREATION ==================================================== #

transition_bdd = None

for source, target in zip(edges_df["source"], edges_df["target"]): #Me to zip exw pixi ((0), (4))
    transition = (encode_id(source, source_vars) & encode_id(target, target_vars)) #!x0!x1!x2!x3!y0y1!y2y3
    
    if transition_bdd is None:
        transition_bdd = transition
    else:
        transition_bdd = transition_bdd | transition # OR 

# Transition BDD = (X0....Y0...) OR (X0....Y0....) OR ......... EXOUME 19 VARIABLES SE SEIRA X0....X8Y0...Y8 KAI OLOUS TOUS SYNDYASMOUS POY BGAZEI TRUE

# ==================================================== LABELLING BDD CREATION ==================================================== #

label_bdds = {}

for node_id, label in zip(nodes_df["id"], nodes_df["label"]):
    node = encode_id(node_id, source_vars)

    if label not in label_bdds:
        label_bdds[label] = node
    else:
        label_bdds[label] = label_bdds[label] | node

#Label BDDS (2 IN TOTAL, ONE FOR EACH LABEL VALUE) = which node IDs have label 0 and which have label 1, using the x variables to encode each node ID in binary

# ==================================================== BDD VISUALIZATON ==================================================== #

# manager.visualize_with_names(
#     "test_graph",
#     [
#         (transition_bdd, "transition_bdd"),
#         (label_bdds[0], "label_0"),
#         (label_bdds[1], "label_1")
#     ]
# )

# ==================================================== BDD VALUATION ==================================================== #


print("\n\nBDD representation")
print("------------------")
print(f"Boolean variables: {manager.num_vars()}")
print(f"Label BDDs: {sorted(label_bdds.keys())}")

# Count before garbage collection
nodes_before = manager.num_inner_nodes()
print(f"BDD nodes before garbage collection: {nodes_before}")

# Perform garbage collection
removed_nodes = manager.gc()

# Count after garbage collection
nodes_after = manager.num_inner_nodes()
print(f"BDD nodes removed by garbage collection: {removed_nodes}")
print(f"BDD nodes after garbage collection: {nodes_after}")


# ==================================================== END OF A ==================================================== #

# ==================================================== START OF B ==================================================== #

# ==================================================== x0 me xn kai y0 me yn ==================================================== #

start_node = 1

source_quantifier = source_vars[0]
target_quantifier = target_vars[0]

for i in range(1, num_bits):
    source_quantifier = source_quantifier & source_vars[i] # SQ = x0 & ... xn
    target_quantifier = target_quantifier & target_vars[i] # TQ = y0 & ... yn


# ==================================================== EQUALITY BDD ==================================================== #

#Ftiaxnw BDD pou einai true otan x0=y0 klpklp. EINAI O MONOS TROPOS POU BRHKA GIA NA MPORW NA BRW TA PANTA

equality_bdd = None

for i in range(num_bits):
    equal_bit = (
        (source_vars[i] & target_vars[i])
        | (~source_vars[i] & ~target_vars[i])
    )

    if equality_bdd is None:
        equality_bdd = equal_bit
    else:
        equality_bdd = equality_bdd & equal_bit

# ==================================================== CONTINUOUS NEIGHBOUR CHECK ==================================================== #

reachable_x = encode_id(start_node, source_vars)

counter = 0

while True:

    counter += 1

    post_y = (reachable_x & transition_bdd).exists(source_quantifier) 
    #Me to exists afairoume apo to (rx AND tbdd) to sq, diladi ola ta x kai maw menei monoo to y
    #DILADI post_y = ta yo...yn toy KATHE target node, DILADI PIXI POST_Y = {1,2,3,4} = {(001),(010),(011),(100)}

    post_x = (post_y & equality_bdd).exists(target_quantifier)
    #me basei to equality_bdd poy x0=y0 klpklp AFAIRW ta y0...yn poy brika prin kai katalligo me OLA ta x poy psaxnw

    new_reachable_x = reachable_x | post_x

    if new_reachable_x == reachable_x:
        break

    reachable_x = new_reachable_x

#PROFANWS to while loop doyleyei level level, diladi prwta koitame ola ta neighbours tou node 1, meta ola ta neighbours 
#aytwn mexri na min exoume nea neighbours

#reachable_x = OLA TA NODES POU EINAI REACHABLE SE X0......X8 MORFI

# ==================================================== COUNT REACHABLE + UNREACHABLE NODES ==================================================== #

num_reachable = reachable_x.sat_count(num_bits)

print("\n\nSymbolic reachability")
print("---------------------")
print(f"Reachable nodes: {num_reachable}")
print(f"Unreachable nodes: {num_nodes - num_reachable}")

# ==================================================== END OF B ==================================================== #