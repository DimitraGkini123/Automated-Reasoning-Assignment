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
    
    #print("\nBDD levels created:")

    T = mgr.true()  ##terminal BDD ( true )
    F = mgr.false()   ##terminal BDD ( false )

    var_of = {v: level_vars[p] for p, v in enumerate(order)}   # DIMACS var -> BDD variable
    
    #print("\nDIMACS variable -> BDD level mapping:")
    #for p, v in enumerate(order[:10]):
    #    print(f"level {p} -> x{v}")

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

def exact_k_bdd(mgr, variables, k):  ##function that returns the bdds that have exactly k features
    memo = {}

##dhladh apo ta existing bdds thelw na ta diasxisw kai na vrw ola ta pithana paths pou exoun akrivws k features selected.
## to kanw anadromika. Dhladh thelw na exw k features. Kathe fora krataw posa mou menoun na valw.
## Kathe fora pou prospernaw ena feature eite to vazw eite oxi , meiwnw ta remaining.
## Episis krataw posa variables mou menoun sunolika sto dentro. An se kapoia fash, mou exoum meinei tosa sto dentro pou den exw prospelasei akoma osa thelw na exw included, prepei anagkastika na ta valw ola
## An oxi, tote exw kai tis dio epiloges gia auto to feature ( kai na to valw kai na mhn to valw ) 
    def build_diff_paths(i, remaining):
        vars_left = len(variables) - i #how many variables are left on the bdd unexplored

        if remaining < 0 or remaining > vars_left : ##fault handling
            return mgr.false()

        if i == len(variables) :
             return mgr.true() if remaining == 0 else mgr.false()

        # if we already solved this state, reuse it
        key = (i, remaining)
        if key in memo:
            return memo[key]

        x = variables[i]

        if remaining == 0: ## we dont need to include any more features, then all the others must become 0
            return ~x & build_diff_paths(i + 1, 0)

        elif remaining == vars_left: #if  I nedd to include exactly the number of features left on the bdd then all should be 1
            return x & build_diff_paths(i + 1, remaining - 1)

        else: ## i have free will and i can choose either 0 or 1
            case_0 = ~x & build_diff_paths(i + 1, remaining)  # chose to not include it, so remaining dont change
            case_1 = x & build_diff_paths(i + 1, remaining - 1)  ## chose to include it and i now need to include one less feature in the future.

        result =  case_0 | case_1
        memo[key] = result
        return result
    return build_diff_paths(0, k)  ## base case, we start from - 


def exact_k_bdd_v2(mgr, variables, k):
    exact = [mgr.false() for _ in range(k + 1)] #lista pou krataei posa features exw. 
    ##an px thelw k=2, tote dhmiourgw exact[0], exact[1], exact[2]
    exact[0] = mgr.true() ##base case, we start with 0 featutes.

    for x in variables: ##iterate through the variables of the bdd
        # Gia kathe neo tropo koitaw me poious pithanous sindiasmous tha petyxw k features

        new_exact = [mgr.false() for _ in range(k + 1)]

        for j in range(k + 1):
            new_exact[j] = new_exact[j] | (~x & exact[j])  ## we dont select the new feature

            if j > 0:
                new_exact[j] = new_exact[j] | (x & exact[j - 1])

        exact = new_exact

    return exact[k]

#twra thelw na parw ola ta epimerous bdd me akrivws k features pou eftiaksa kai na vrw poio exei to minimum + valid.
def find_min_conf(mgr, f, var_of, n):
    

    variables = [var_of[i] for i in range(1, n + 1)]
    #iterate from 0 features until the total number of variables.
    for k in range(n + 1):

        print("Testing k =", k)

        exact_k = exact_k_bdd_v2(mgr, variables, k)

        # BDD that shows all the minimum valid configurations for every k 
        candidates = f & exact_k

        #how many satisfying assignments does the candidate bdd contain
        count = candidates.sat_count(n)

        if count > 0:
            print("Minimum found:", k)
            #when we find the first k that has at least one valid configuration, then we return this candidate which is also the solution 
            return k, candidates

    return None, None

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

        print("FILE:", path)
        print("\n(i) Number of BDD nodes for φ:", f.node_count())
        print("\n(ii) Number of valid configurations |V|:", f.sat_count(n))

        minimum_size, minimum_bdd = find_min_conf(
        mgr, f, var_of, n
    )
        print("\n(iii) Size of a minimum valid configuration:", minimum_size)

        #(iv)
        #define the essential features
        x218 = var_of[218]
        x311 = var_of[311]

        ## we are looking for the configurations that for sure contain the essential features
        f_essential = f & x218 & x311

        minimum_size_essential, minimum_bdd_essential = find_min_conf( mgr, f_essential, var_of, n)

        print("\n(iv) Minimum configuration size with essential features x218 and x311:", minimum_size_essential)
        
        #(v) number of bdd nodes used to represent the set of all valid configurations. Posous komvous exei auto to bdd pou einai to elaxisto.
        print("\n(v) Number of BDD nodes representing all minimum valid configurations:", minimum_bdd.node_count())

        #(vi) poses diaforetikes minimum configurations anaparista auto to bdd ( pou einai kai to solution bdd)
        ##px an vrhkame oti minimum features (k) =2 kai ta configurations einai auta : 1100,1010, 1001 tote #minimum_configurations = 3
        print("\n(vi) Number of minimum valid configurations:", minimum_bdd.sat_count(n))
    