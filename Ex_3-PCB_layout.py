from z3 import *

#Parameters
W1 = 20
H1 = 20
W2 = 22
H2 = 27
WB1 = 12
HB1 = 8
WB2 = 14
HB2 = 12
WC1 = 7
HC1 = 5
D1 = [5,5,4,4,5,3,7,6,6,4,6,5,6,5]
D2 = [6,6,6,10,7,7,7,10,12,10,9,11,10,10]
chips = 14

#Variables
x = [Int(f"x{i}") for i in range(1, chips+1)]
y = [Int(f"y{i}") for i in range(1, chips+1)]
w = [Int(f"w{i}") for i in range(1, chips+1)]
h = [Int(f"h{i}") for i in range(1, chips+1)]

s = Solver()
#s = Optimize()

#Constraints

#Chips may be rotated by 90 degrees, so the width can take the value of the height and vice versa.
for i in range(chips):
   s.add(Or(And(w[i] == D1[i], h[i] == D2[i]),
            And(w[i] == D2[i], h[i] == D1[i]))
        )    

#Chips should fit in either the PCB1 or PCB2 board, and not overlap over the batteries and the camera.
for i in range(chips):
    s.add(Or(And(x[i] >= 0, y[i] >= 0, Or(x[i] >= WB1, y[i] >= HB1), x[i] + w[i] <= W1,  y[i] + h[i] <= H1),
              And(x[i] >= 0, y[i] >= 0, Or(x[i] >= WB2, y[i] >= HB2), x[i] + w[i] <= W2,  y[i] + h[i] <= H2, Or(x[i] + w[i] <= W2 - WC1, y[i] + h[i] <= H2 - HC1))))

#Chips should not overlap with each other.
for i in range(chips):
    for j in range(i+1, chips):
        s.add(Or(x[i] + w[i] <= w[j], x[j] + w[j] <= x[i], y[i] + h[i] <= y[i], y[j]+ h[j] <= y[i]))

#The centers of hot chips should be 20 units apart from each other
for i in range(0,1,5):
    s.add(Or(x[i] + w[i]/2 + 20 <= x[j] + w[j]/2, x[j] + w[j]/2 + 20 <= x[i] + w[i]/2, y[i] + h[i]/2 + 20 <= y[j] + h[j]/2, y[j] + h[j]/2 + 20 <= y[i] + h[i]/2))


print(s.check())
    
if s.check() == sat :
    m = s.model()
    for i in range(chips):
        print(f"w[{i}] = {m[w[i]]}, h[{i}] = {m[h[i]]}")
        print(f"x[{i}] = {m[x[i]]}, y[{i}] = {m[y[i]]}")

# find which chip is in which PCB
# write additional constraint for b
# write additional constraint for c


