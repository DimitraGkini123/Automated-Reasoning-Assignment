from z3 import *
#time limit
T = 25
#define each village as a list with the time as the parameter
A = [Int(f"A_{t}") for t in range(T + 1)]
B = [Int(f"B_{t}") for t in range(T + 1)]
C = [Int(f"C_{t}") for t in range(T + 1)]
#truck also is a list
Tr = [Int(f"Tr_{t}") for t in range(T + 1)]
#truck position.
P = [String(f"P_{t}") for t in range(T + 1)]
#ammount of products that the truck is leaving 
d = [Int(f"d_{t}") for t in range(T + 1)]
s = Solver()

#Possible positions are {S,A,B,C}
for i in range(T+1):
    s.add(Or(P[i]=="S",P[i]=="A",P[i]=="B", P[i]=="C"))
#initial state of villages
s.add(A[0] == 60 )
s.add(B[0] == 60 )
s.add(C[0] == 60 )

s.add(Tr[0] == 130 )
s.add(P[0]== "S")

#add the caps ( for villages and truck )
for i in range(T+1):
    s.add(And(A[i] >= 0, A[i] <= 90))
    s.add(And(B[i] >= 0, B[i] <= 120))
    s.add(And(C[i] >= 0, C[i] <= 90))
    s.add(And(Tr[i] >= 0, Tr[i] <= 130))

#allowed routes
for i in range(T):
    s.add(Implies(P[i]== "S", Or(P[i+1]== "A", P[i+1] == "C"))) #when truck is in S, it can go S-->A or S--> C
    s.add(Implies(P[i]=="A", Or(P[i+1]== "B", P[i+1] == "C", P[i+1]=="S")))  #A--> B or A--> C or A--> S
    s.add(Implies(P[i]=="B", Or(P[i+1]== "A", P[i+1] == "C")))  #B-->A  or B-->C
    s.add(Implies(P[i]=="C", Or(P[i+1]== "B", P[i+1] == "S", P[i+1] == "A"))) # C--> B or C-->S or S-->A

# cost of each trip ( in food units and time)
travel = [Int(f"travel_{i}") for i in range(T)]
s.add(travel[i] > 0)
#cost of each trip 
for i in range(T):
    #from S
    s.add(Implies(And(P[i] == "S", P[i+1] == "A"), travel[i] == 15))
    s.add(Implies(And(P[i] == "S", P[i+1] == "C"), travel[i] == 15))
    #from A
    s.add(Implies(And(P[i] == "A", P[i+1] == "S"), travel[i] == 15))
    s.add(Implies(And(P[i] == "A", P[i+1] == "B"), travel[i] == 17))
    s.add(Implies(And(P[i] == "A", P[i+1] == "C"), travel[i] == 12))
    #from C
    s.add(Implies(And(P[i] == "C", P[i+1] == "S"), travel[i] == 15))
    s.add(Implies(And(P[i] == "C", P[i+1] == "A"), travel[i] == 12))  
    s.add(Implies(And(P[i] == "C", P[i+1] == "B"), travel[i] == 9))

    #from B
    s.add(Implies(And(P[i] == "B", P[i+1] == "C"), travel[i] == 13))
    s.add(Implies(And(P[i] == "B", P[i+1] == "A"), travel[i] == 17))

#Before the truck starting one route that will take time t1, it has to make sure that all villages have more than t1 units of food available
for i in range(T):
    s.add(And( A[i] >= travel[i], B[i] >= travel[i], C[i] >= travel[i]) )

#The ammount of products the truck leaves, has to be less than the ammount of products that the truck carries at this time
for i in range(T):
    s.add(And(d[i]>=0, d[i]<=Tr[i]))

for i in range(T):
    #when truck arrives at truck A, it leaves d[i] products while the other villages still eat the food that corresponds to the time that the truck travelled
    s.add(Implies(P[i+1]=="A", A[i+1]==A[i]-travel[i] + d[i]))
    s.add(Implies(P[i+1]=="A", B[i+1]==B[i]-travel[i]))
    s.add(Implies(P[i+1]=="A", C[i+1]==C[i]-travel[i]))


    #same for villages B and C
    s.add(Implies(P[i+1]=="B", B[i+1]==B[i]-travel[i]+d[i]))
    s.add(Implies(P[i+1]=="B", C[i+1]==C[i]-travel[i]))
    s.add(Implies(P[i+1]=="B", A[i+1]==A[i]-travel[i]))

    s.add(Implies(P[i+1]=="C", C[i+1]==C[i]-travel[i]+d[i]))
    s.add(Implies(P[i+1]=="C", A[i+1]==A[i]-travel[i]))
    s.add(Implies(P[i+1]=="C", B[i+1]==B[i]-travel[i]))


    #when truck arrives in any village, it drops off d[i] units of food
    s.add(Implies( Or(P[i+1] == "A", P[i+1] == "B", P[i+1] == "C"), Tr[i+1] == Tr[i] - d[i]))

    #truck is refilling at S village while the villages are still losing prducts
    s.add(Implies(P[i+1] == "S", And (  A[i+1] == A[i] - travel[i],  B[i+1] == B[i] - travel[i],  C[i+1] == C[i] - travel[i],Tr[i+1] == 130)) )

print(s.check())
    