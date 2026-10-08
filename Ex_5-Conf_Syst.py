import re
import sys
from oxidd.bdd import BDDManager, BDDFunction
from pysat.formula import CNF


def read_dimacs(path):
    """Return (num_vars, clauses, order). order = DIMACS variables 1..n, top to bottom (or None)."""
    num_vars = 0
    clauses, current = [], []
    order = None

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("c"):
                if line.startswith("c vo"):
                    nums = [int(t) for t in re.findall(r"\d+", line[4:])]
                    order = nums                      # shifted to 1-based below, once n is known
                continue                              # all other comments are skipped
            if line.startswith("p"):
                num_vars = int(line.split()[2])       # p cnf <vars> <clauses>
                continue
            for tok in line.split():
                lit = int(tok)
                if lit == 0:
                    clauses.append(current)
                    current = []
                else:
                    current.append(lit)
    if current:
        clauses.append(current)

    if order is not None:
        if min(order) == 0:                           # 0-based indices -> DIMACS numbers
            order = [v + 1 for v in order]
        assert sorted(order) == list(range(1, num_vars + 1)), "invalid variable order"
    return num_vars, clauses, order



def build_bdd(path):
    n, clauses, order = read_dimacs(path)
    if order is None:
        order = list(range(1, n + 1))

    mgr = BDDManager(10_000_000, 1_000_000, 1)
    levels = mgr.add_vars(n)                                   # adds n variables, top to bottom
    level_vars = [BDDFunction.var(mgr, i) for i in levels]     # BDD of each variable
    T = BDDFunction.true(mgr)
    F = BDDFunction.false(mgr)
    var_of = {v: level_vars[p] for p, v in enumerate(order)}   # DIMACS var -> BDD variable

    clause_bdds = []
    for clause in clauses:
        c = F
        for lit in clause:
            x = var_of[abs(lit)]
            c = c | (x if lit > 0 else ~x)
        clause_bdds.append(c)

    while len(clause_bdds) > 1:
        nxt = [clause_bdds[i] & clause_bdds[i + 1] for i in range(0, len(clause_bdds) - 1, 2)]
        if len(clause_bdds) % 2:
            nxt.append(clause_bdds[-1])
        clause_bdds = nxt
    f = clause_bdds[0] if clause_bdds else T
    return mgr, var_of, f, n

if __name__ == "__main__":
    #path = sys.argv[1] if len(sys.argv) > 1 else "/Users/antonitaarvanitaki/Downloads/conf-dimacs/toybox.dimacs"   # no argument needed any more

    cnf = CNF(from_file="/Users/antonitaarvanitaki/Downloads/conf-dimacs/toybox.dimacs")
    n = cnf.nv            # number of variables
    clauses = cnf.clauses
    print(clauses)
    mgr, var_of, f, n = build_bdd(path)
    print("nodes:", f.node_count())
    print("valid configurations:", f.sat_count(n))
    