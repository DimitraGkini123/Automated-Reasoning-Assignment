from z3 import *

#s = Solver()
o = Optimize()

# We define a set that includes the nurses 
nurses = {"N1", "N2", "N3", "N4", "N5"}

# We define the number of days that the shifts have to be distributted in
days = 7

# We define the number of weeks that the shifts have been distributed
weeks = 3

# We define a set of the shifts that need to be assigned
shifts = {"DM", "DA", "DN", "WM", "WA", "WN"}

# we define a boolean variable N that is true when the nurse n is working in shift s on day d, otherwise is false
N = [Bool(f"N_{n,d,s}") for n in nurses
                        for d in days
                        for s in shifts] 

# We define the program of each nurse in each week
P = [Bool(f"P_{n,w}") for n in nurses
                      for w in weeks]

# We define the workload of each shift, as it differs
W = [Int(f"W_{n,s}") for n in nurses
                     for s in shifts]

# The sum of workloads for each nurse per week
SW = [Int(f"SW{n}") for n in nurses]

# weekend shifts?


# initial state?

# Each nurse works at most one shift per day
for n in nurses:
    for d in range(days):
        for s1, s2 in shifts:
            if (s1 != s2):
                o.add(Or(Not(N[n,d,s1]), Not[n,d,s2]))


# Each shift has exactly one nurse
# One contraint for having at least one nurse
for n in nurses:
    for d in range(days):
        for s in shifts:
            o.add(Or(N[n,d,s1]))

# Second contraint for having exaclty one nurse
for n1, n2 in nurses:
    for d in range(days):
        for s in shifts: 
            o.add(Or(Not(N[n1,d,s]), Not(N[n2,d,s])))


#Night Shifts
# If a nurse does a morning or afternnon shift in one day then they should not do also a night shift
for n in nurses:
    for d in range(days):
        o.add(Implies(Or(N[n,d,"DM"], N[n,d,"DA"]), Not(N[n,d,"DN"])))

# If a nurse does a night shift then the next day they should not have a morning
# for n in nurses:
#     for d in range(days+1):
#         o.add(Implies(N[n,d,"DN"]), Not(N[n,d,"DN"]))


# We want the workload of each nurse in  each week to be similar
# We have to count the workload based on the shifts that are assigned to every nurse. We do that by converting the boolean value of the shifts of each nurse per day
# to an integer and then taking the sum of those.
for n in nurses:
    for d in days:
        o.add(Implies(Or(N[n,d,"DM"], W[n,"DM"] == 10)))
        o.add(Implies(Or(N[n,d,"DA"], W[n,"DA"] == 66)))
        o.add(Implies(Or(N[n,d,"DN"], W[n,"DN"] == 23)))
        o.add(Implies(Or(N[n,d,"WM"], W[n,"WM"] == 39)))
        o.add(Implies(Or(N[n,d,"WA"], W[n,"WA"] == 44)))
        o.add(Implies(Or(N[n,d,"WN"], W[n,"WN"] == 90)))

for n in nurses:
    SW[n] = Sum([
        If(N[n, d, s], shift_hours[s], 0)
        for d in days
        for s in shifts
    ])

for n in nurses:
    SW[n] = Sum([W[n,d] 
                for d in days])


# We want the schedule of every nurse every week to be similar, without big changes
for n in nurses:
    for w1, w2 in range(weeks):
        if (w1 != w2):
            o.add(Implies(P[n,w1]), P[n,w2] )


# min max