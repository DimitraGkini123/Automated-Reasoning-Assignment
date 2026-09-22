from z3 import *
T = 10000
#define each village as a list with the time as the parameter
A = [Int(f"A_{t}") for t in range(T + 1)]
B = [Int(f"B_{t}") for t in range(T + 1)]
C = [Int(f"C_{t}") for t in range(T + 1)]
#truck also is a list
T = [Int(f"T_{t}") for t in range(T + 1)]

s = Solver()

#initial state of villages
s.add(A[0] == 60 )
s.add(B[0] == 60 )
s.add(C[0] == 60 )

s.add(T[0] == 130 )

#add the caps ( for villages and truck )
for i in range(T+1):
    s.add(A[i]<= 90)
    s.add(B[i]<= 120)
    s.add(C[i]<= 90)
    s.add(T[i]<= 130)