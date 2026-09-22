from z3 import *

trucks = 6
N = [Int(f"N{i}") for i in range(1, trucks+1)]
P = [Int(f"P{i}") for i in range(1, trucks+1)]
S = [Int(f"S{i}") for i in range(1, trucks+1)]
C = [Int(f"C{i}") for i in range(1, trucks+1)]
D = [Int(f"D{i}") for i in range(1, trucks+1)]

#define the weights
W_n = 800
W_p = 405
W_s = 500
W_c = 2500
W_d = 600

#total Weight of each truck 
W = [Int(f"W{i}") for i in range(1, trucks+1)]

s=Optimize() #vriskei lush 
#o=Optimize() #kalyterh lush 

#ksekiname apo to oti ola einai thetika.
for i in range(trucks):
    s.add(N[i] >= 0 )
    s.add(P[i] >= 0 )
    s.add(S[i] >= 0 )
    s.add(C[i] >= 0 )
    s.add(D[i] >= 0 )

#quantity of each product
    s.add(Sum(N) == 6)  
    s.add(Sum(P) == 12)
    s.add(Sum(S) == 15)
    s.add(Sum(C) == 8)

for i in range(trucks):
    s.add( W[i] == W_n * N[i] + W_p * P[i] + W_s * S[i] + W_c * C[i] + W_d * D[i] ) 
    s.add(W[i] <= 8000 )

#every truck can fit max 10 objects
for i in range(trucks):
    s.add( Sum(N[i],P[i],S[i],C[i],D[i]) <= 10)

#prittles--> toul se 5 trucks ara an metrhsw ta trucks pou exoun P prepei na einai >=5
prittles_in_trucks = Sum( (If(P[i]>0,1,0) for i in range(trucks)) )
s.add(prittles_in_trucks >= 5)

#nuzzles
nuzzles_in_trucks = Sum( (If(N[i]>0,1,0) for i in range(trucks)))
s.add(nuzzles_in_trucks == 2)
print(s.check()) #checks if its sat or unsat 

s.maximize(Sum(D))

result = s.check()

m = s.model()
print(m.eval(sum(D)))
print(m)



