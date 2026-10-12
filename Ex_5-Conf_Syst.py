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
        order = list(range(1, n + 1))  # an gia kapoio arxeio den uparxei to variable ordering etoimo, epilegoume to x1<x2<...<xn

    mgr = BDDManager(10_000_000, 1_000_000, 1)  ##create the bdd manager
    levels = mgr.add_vars(n)                                   # create as many leveles as the variables
    level_vars = [mgr.var(i) for i in levels]    # BDD of each variable
    
    print("\nBDD levels created:")
    print("First 10 levels:", levels[:10])

    print("\nFirst 10 level_vars:")
    for i in range(min(10, len(level_vars))):
        print(f"level_vars[{i}] =", level_vars[i])

    T = mgr.true()  ##terminal BDD ( true )
    F = mgr.false()   ##terminal BDD ( false )

    var_of = {v: level_vars[p] for p, v in enumerate(order)}   # DIMACS var -> BDD variable
    
    print("\nDIMACS variable -> BDD level mapping:")
    for p, v in enumerate(order[:10]):
        print(f"level {p} -> x{v}")

    clause_bdds = []  ## list that will contain all the bdds that were constructed ( one for every clause )
    for clause in clauses:
        c = F  ##panta ksekiname me false 
        for lit in clause:  ##diasxizoume ta clauses 
            x = var_of[abs(lit)]  ##vriskoume to bdd pou antistoixei se auto to clause 
            c = c | (x if lit > 0 else ~x)  ## an to literal einai thetiko xrhsimopoihse to opws einai alliws valto se arnhsh 
        clause_bdds.append(c) ## add sthn lista

    #Gia na vroume to teliko kai sunoliko bdd prepei na paroume ola ta epimerous BDDs kai na ta kanoume and metaksy tous
    while len(clause_bdds) > 1:  ##oso exw panw apo ena bdd sthn lista mou
        combine = [clause_bdds[i] & clause_bdds[i + 1] for i in range(0, len(clause_bdds) - 1, 2)]
        if len(clause_bdds) % 2:
            combine.append(clause_bdds[-1])
        clause_bdds = combine
    f = clause_bdds[0] if clause_bdds else T ## exoume to teliko bdd otan meinoume me ena clause dld me ena eniaio and apo polla bdd
    return mgr, var_of, f, n


## Afou exw ftiaksei to synoliko bdd , emena me noiazoun ta valid configuartions dld assignments pou kanoun thn f true.##
## Theoritika an eixa to bdd se sxhma tha eprepe na metrhsw ola ta paths pou me kanoun na katalhgw se 1 + ta skipped epipeda. 
##Auto kanei h sat_count.
if __name__ == "__main__":

    files = [
    "buildroot.dimacs",
    "busybox.dimacs",
    "embtoolkit.dimacs",
    "toybox.dimacs",
    "uClinux.dimacs"
]
    
    for path in files:
        mgr, var_of, f, n = build_bdd(path)

        print(path)
        print("nodes:", f.node_count())
        print("valid configurations:", f.sat_count(n))
        print()
    