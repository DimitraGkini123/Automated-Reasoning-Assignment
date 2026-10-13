
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
print(f"Nodes: {num_nodes}")
print(f"Edges: {num_edges}")
print(f"Bits per node ID: {num_bits}")

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

# ==================================================== BDD CREATION ???? ==================================================== #

transition_bdd = None

for source, target in zip(edges_df["source"], edges_df["target"]): #Me to zip exw pixi ((0), (5))
    transition = encode_id(source, source_vars) & encode_id(target, target_vars) #twra exw ((0000000000000000), (00000000101))

    if transition_bdd is None:
        transition_bdd = transition
    else:
        transition_bdd = transition_bdd | transition # OR kai oxi AND giati eimai anapofasistos (stin tyxh mphke)

#THEWRITIKA twra exw ena prama trans_bdd = OR TRANS(source,target)(x0,......,y0,........) gia kathe value
#einai auto bdd? den kserw.... den einai, apla exw ftiaksei ola ta transitions poy mporei na ginoyn