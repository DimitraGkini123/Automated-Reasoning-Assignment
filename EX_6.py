import math
import pandas as pd
from oxidd import bdd

# ==================================================== Extract Data from .csv Files ==================================================== #

NODES_FILE = "C:/Users/user/Downloads/graphs/congress_nodes.csv"
EDGES_FILE = "C:/Users/user/Downloads/graphs/congress_edges.csv"

# NODES_FILE = "C:/Users/user/Downloads/graphs/pokec-small_nodes.csv"
# EDGES_FILE = "C:/Users/user/Downloads/graphs/pokec-small_edges.csv"

# NODES_FILE = "C:/Users/user/Downloads/graphs/pokec-medium_nodes.csv"
# EDGES_FILE = "C:/Users/user/Downloads/graphs/pokec-medium_edges.csv"

# NODES_FILE = "C:/Users/user/Downloads/graphs/pokec_nodes.csv"
# EDGES_FILE = "C:/Users/user/Downloads/graphs/pokec_edges.csv"

nodes_df = pd.read_csv(NODES_FILE, sep=r"\s+")
edges_df = pd.read_csv(EDGES_FILE, sep=r"\s+")

nodes_df.columns = nodes_df.columns.str.strip()
edges_df.columns = edges_df.columns.str.strip()

nodes_df["id"] = nodes_df["id"].astype(int)
edges_df["source"] = edges_df["source"].astype(int)
edges_df["target"] = edges_df["target"].astype(int)

node_ids = set(nodes_df["id"]) #Count the unique IDs, set() removes the duplicates

num_nodes = len(node_ids) 
num_edges = len(edges_df) 

num_bits = math.ceil(math.log2(num_nodes + 1)) 
#Calculate number of nodes for binary represention and biilean expression

print("Graph information")
print("-----------------")
print(f"Unique IDs: {num_nodes}")
print(f"Edges: {num_edges}")
print(f"Bits per node ID: {num_bits}")

# ==================================================== START OF A ==================================================== #

# ==================================================== Transition Variables ==================================================== #

variable_names = ([f"x{i}" for i in range(num_bits)] + [f"y{i}" for i in range(num_bits)])

manager = bdd.BDDManager(100_000_000, 10_000_000, 4)
manager.add_named_vars(variable_names) #strings so named_vars instead of vars

source_vars = [manager.var(i) for i in range(num_bits)] #x0 to xn
target_vars = [manager.var(num_bits + i) for i in range(num_bits)] #y0 to yn

#
#x0 me x8 kai y0 me y8 (0 me 8 kai 9 me 18). thelw 18 bit gia kathe trans, 9 gia source kai 9 gia target 

# ====================================================Binary Encoding and Boolean Expression ==================================================== #

def encode_id(node_id, variables): #Convert IDs to Bollean expression

    temp1 = format(node_id, f"0{num_bits}b") #Convert IDS to binary encoding with padded 0s if needed
    representation = None

    for i in range(num_bits): #Convert binary encoding to bollean expression
        if temp1[i] == "1":
            temp2 = variables[i] #1 is converted to x
        else:
            temp2 = ~variables[i] #0 is converted to -x

        if representation is None:
            representation = temp2
        else:
            representation = representation & temp2

    return representation #Full boolean expression 

# ==================================================== Transition BDD Creation ==================================================== #

transition_bdd = None

for source, target in zip(edges_df["source"], edges_df["target"]): #zip() creates a tuple ((source id), (target id))
    transition = (encode_id(source, source_vars) & encode_id(target, target_vars)) 
    #Conjuction of x and y varieables after Boolean expression
    
    if transition_bdd is None:
        transition_bdd = transition
    else:
        transition_bdd = transition_bdd | transition #Disjunction of directed edges

# Transition BDD = (X0....Y0...) OR (X0....Y0....) OR ......... 2n variables that lead to True only for valid transitions

# ==================================================== Label BDD Creation ==================================================== #

label_bdds = {}

for node_id, label in zip(nodes_df["id"], nodes_df["label"]): #zip() creates a tuple ((id), (label of id))
    node = encode_id(node_id, source_vars)

    if label not in label_bdds:
        label_bdds[label] = node
    else:
        label_bdds[label] = label_bdds[label] | node

#Label BDDS are 2 in total, one for each label 0,1
#Label BDD {0} = All the IDs with a label of 0 in boolean expression
#Label BDD {1} = All the IDs with a label of 1 in boolean expression

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

# ==================================================== Source and Target Quantifiers ==================================================== #

start_node = 1 #Set starting node to 1

source_quantifier = source_vars[0]
target_quantifier = target_vars[0]

for i in range(1, num_bits):
    source_quantifier = source_quantifier & source_vars[i] # SQ = x0 & ... xn
    target_quantifier = target_quantifier & target_vars[i] # TQ = y0 & ... yn


# ==================================================== Equality BDD ==================================================== #

#A path of this BDD is True when all x variables are equal to the corresponding y variables

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

#It is used to transfer the Target ID to the Source ID after every iteraton of Symbolic Reachability

# ==================================================== Symbolic Reachability ==================================================== #

reachable_x = encode_id(start_node, source_vars) #Node 1 is considered the first reachable node, since it is also the starting node

counter = 0

while True:

    counter += 1

    new_y = (reachable_x & transition_bdd).exists(source_quantifier) 
    #With existential quantification we remove the source id (x variables) from the Transition BDD
    #so we end up only with the target id (y variables)
    #new_y = y0....

    new_x = (new_y & equality_bdd).exists(target_quantifier)
    #With existential quantification we remove the target id we just calculated (y variables) from the Equality BDD
    #so we end up only with the new source id (x variables), which is the same as the previous target id
    #new_x = x0....

    new_reachable_x = reachable_x | new_x

    if new_reachable_x == reachable_x:
        break

    reachable_x = new_reachable_x

#At the end of the while loop, reachable_x contains all the node IDs that are reachable from using node 1 as a starting node

# ==================================================== Count Reachable + Unreachable Nodes ==================================================== #

num_reachable = reachable_x.sat_count(num_bits)

print("\n\nSymbolic reachability")
print("---------------------")
print(f"Reachable nodes: {num_reachable}")
print(f"Unreachable nodes: {num_nodes - num_reachable}")

# ==================================================== END OF B ==================================================== #

# ==================================================== START OF C ==================================================== #

# ==================================================== Label1 + Label 0 ==================================================== #

label0_y = (label_bdds[0] & equality_bdd).exists(source_quantifier)
label1_y = (label_bdds[1] & equality_bdd).exists(source_quantifier)

# ==================================================== Alternating Label Reachability ==================================================== #

reachable_even_x = encode_id(start_node, source_vars)
reachable_odd_x = reachable_even_x & ~reachable_even_x

counter = 0

while True:

    counter += 1

    new_odd_y = ((reachable_even_x & transition_bdd).exists(source_quantifier) & label1_y)
    #Same as before, but with the added constraint of nodes needing to have a label 1

    new_odd_x = (new_odd_y & equality_bdd).exists(target_quantifier)
    #Same as before

    new_even_y = ((reachable_odd_x & transition_bdd).exists(source_quantifier)& label0_y)
    #Same as before, but with the added constraint of nodes needing to have a label 0

    new_even_x = (new_even_y & equality_bdd).exists(target_quantifier)
    #Same as before

    new_reachable_even_x = reachable_even_x | new_even_x
    new_reachable_odd_x = reachable_odd_x | new_odd_x

    if (new_reachable_even_x == reachable_even_x and new_reachable_odd_x == reachable_odd_x):
        break

    reachable_even_x = new_reachable_even_x
    reachable_odd_x = new_reachable_odd_x

#At the end of the while loop, reachable_even_x contains all the node IDs that are reachable from using node 1 as a starting node and have label 0
#At the end of the while loop, reachable_odd_x contains all the node IDs that are reachable from using node 1 as a starting node and have label 1

# ==================================================== Count Reachable + Unreachable Nodes ==================================================== #

alternating_reachable_x = reachable_even_x | reachable_odd_x

num_alternating_reachable = alternating_reachable_x.sat_count(num_bits)

print("\n\nAlternating-label reachability")
print("------------------------------")
print(f"Starting node: {start_node}")
print(f"Reachable nodes: {num_alternating_reachable}")
print(f"Unreachable nodes: {num_nodes - num_alternating_reachable}")

# ==================================================== END OF C ==================================================== #