from z3 import *

#s = Solver()
o = Optimize()

# We define a set that includes the nurses 
nurses = {"N1", "N2", "N3", "N4", "N5"}

# We define the number of days that the shifts have to be distributted in
days = 7

# We define a set of the shifts that need to be assigned
shifts = {"DM", "DA", "DN", "WM", "WA", "WN"}

# integer variable that is true when the nurse n is working in shift s on day d, otherwise is false
N = [Bool(f"N_{n,d,s}") for n in nurses
                        for d in days
                        for s in shifts]

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
for n in nurses:
    for d in range(days+1):
        #!!o.add(Implies(N[n,d,"DN"]), Not(N[n,d,"DN"]))


#

# schedule

