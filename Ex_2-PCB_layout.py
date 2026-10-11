from z3 import *

# Parameters
W1, H1, W2, H2 = 20, 20, 22, 27
WB1, HB1 = 12, 8
WB2, HB2 = 14, 12
WC1, HC1 = 7, 5         # question (a), for question (b) if the second camera is added in PCB1, and for question (c) if all 1 camera are added in PCB1
WC2, HC2 = 11, 5        # question (b), also for question (c) if the second camera is added in PCB2
WC3, HC3 = 19, 5        # question (c), if all 3 cameras are added in PCB2

D1 = [5,5,4,4,5,3,7,6,6,4,6,5,6,5]
D2 = [6,6,6,10,7,7,7,10,12,10,9,11,10,10]
chips = 14
hot_chips = [0,1,5]

# Variables
p = [Bool(f"p{i}") for i in range(chips)]     # boolean variable to defin in which PCB each chip is located;
                                              # True if chip i is on PCB 1, False if chip i is on PCB 2
x = [Int(f"x{i}") for i in range(chips)]      # x-coordinate of the bottom-left corner of chip i
y = [Int(f"y{i}") for i in range(chips)]      # y-coordinate of the bottom-left corner of chip i
w = [Int(f"w{i}") for i in range(chips)]      # width of chip i
h = [Int(f"h{i}") for i in range(chips)]      # height of chip i

s = Solver()
#s = Optimize()

# Constraints

# Chips may be rotated by 90 degrees, so the width can take the value of the height and vice versa
for i in range(chips):
   s.add(Or(And(w[i] == D1[i], h[i] == D2[i]),
            And(w[i] == D2[i], h[i] == D1[i])))
   
# The x and y coordinates of the chips should be non-negative
   s.add(x[i] >= 0, y[i] >= 0)
   
# Chips should fit in either the PCB1 or PCB2 board, and not overlap over the batteries and the camera
# For question (a), 1 camera is in PCB2 and 0 cameras are in PCB1
   s.add(Or(p[i], 
            And(x[i] + w[i] <= W1, y[i] + h[i] <= H1,
                Or(x[i] >= WB1, y[i] >= HB1))))
   s.add(Or(Not(p[i]),
            And(x[i] + w[i] <= W2, y[i] + h[i] <= H2, 
                Or(x[i] >= WB2, y[i] >= HB2),
                Or(x[i] + w[i] <= W2 - WC1, y[i] + h[i] <= H2 - HC1))))

# # For question (b), 2 cameras are in PCB2 and 0 cameras are in PCB1
#    s.add(Or(p[i], 
#             And(x[i] + w[i] <= W1, y[i] + h[i] <= H1,
#                 Or(x[i] >= WB1, y[i] >= HB1))))
#    s.add(Or(Not(p[i]),
#             And(x[i] + w[i] <= W2, y[i] + h[i] <= H2, 
#                 Or(x[i] >= WB2, y[i] >= HB2),
#                 Or(x[i] + w[i] <= W2 - WC2, y[i] + h[i] <= H2 - HC2))))
   
# # For question (b), 1 camera is in PCB2 and 1 camera is in PCB1
#    s.add(Or(p[i],
#             And(x[i] + w[i] <= W1, y[i] + h[i] <= H1,
#                 Or(x[i] >= WB1, y[i] >= HB1),
#                 Or(x[i] + w[i] <= W1 - WC1, y[i] + h[i] <= H1 - HC1))))
#    s.add(Or(Not(p[i]),
#             And(x[i] + w[i] <= W2, y[i] + h[i] <= H2, 
#                 Or(x[i] >= WB2, y[i] >= HB2),
#                 Or(x[i] + w[i] <= W2 - WC1, y[i] + h[i] <= H2 - HC1))))

# # For question (c), 4 cameras are in PCB2 and 0 camera is in PCB1
#    s.add(Or(p[i], 
#             And(x[i] + w[i] <= W1, y[i] + h[i] <= H1,
#                 Or(x[i] >= WB1, y[i] >= HB1))))
#    s.add(Or(Not(p[i]),
#             And(x[i] + w[i] <= W2, y[i] + h[i] <= H2, 
#                 Or(x[i] >= WB2, y[i] >= HB2),
#                 Or(x[i] + w[i] <= W2 - WC3, y[i] + h[i] <= H2 - HC3))))

# # For question (c), 3 cameras are in PCB2 and 1 cameras are in PCB1
#    s.add(Or(p[i],
#             And(x[i] + w[i] <= W1, y[i] + h[i] <= H1,
#                 Or(x[i] >= WB1, y[i] >= HB1),
#                 Or(x[i] + w[i] <= W1 - WC1, y[i] + h[i] <= H1 - HC1))))
#    s.add(Or(Not(p[i]),
#             And(x[i] + w[i] <= W2, y[i] + h[i] <= H2, 
#                 Or(x[i] >= WB2, y[i] >= HB2),
#                 Or(x[i] + w[i] <= W2 - WC2 - WC1, y[i] + h[i] <= H2 - HC1))))

# # For question (c), 2 cameras are in PCB2 and 2 camera is in PCB1
#    s.add(Or(p[i],
#             And(x[i] + w[i] <= W1, y[i] + h[i] <= H1,
#                 Or(x[i] >= WB1, y[i] >= HB1),
#                 Or(x[i] + w[i] <= W1 - WC2, y[i] + h[i] <= H1 - HC2))))
#    s.add(Or(Not(p[i]),
#             And(x[i] + w[i] <= W2, y[i] + h[i] <= H2, 
#                 Or(x[i] >= WB2, y[i] >= HB2),
#                 Or(x[i] + w[i] <= W2 - WC2, y[i] + h[i] <= H2 - HC2))))

# # For question (c), 1 camera is in PCB2 and 3 cameras are in PCB1
#    s.add(Or(p[i],
#             And(x[i] + w[i] <= W1, y[i] + h[i] <= H1,
#                 Or(x[i] >= WB1, y[i] >= HB1),
#                 Or(x[i] + w[i] <= W1 - WC2 - WC1, y[i] + h[i] <= H1 - HC2))))
#    s.add(Or(Not(p[i]),
#             And(x[i] + w[i] <= W2, y[i] + h[i] <= H2, 
#                 Or(x[i] >= WB2, y[i] >= HB2),
#                 Or(x[i] + w[i] <= W2 - WC1, y[i] + h[i] <= H2 - HC1))))


   
# Chips should not overlap with each other, only when they are on the same PCB
for i in range(chips):
    for j in range(i+1, chips):
        s.add(Or(p[i] != p[j], 
              x[i] + w[i] <= x[j], x[j] + w[j] <= x[i], 
              y[i] + h[i] <= y[j], y[j]+ h[j] <= y[i]))


# The centers of hot chips should be 20 units apart from each other when on the same PCB
for a in range(len(hot_chips)):
    for b in range(a+1, len(hot_chips)):
        i, j = hot_chips[a], hot_chips[b]
        s.add(Or(p[i] != p[j],
                 abs(x[i] + w[i]/2 - x[j] - w[j]/2) >= 20, 
                 abs(y[i] + h[i]/2 - y[j] - h[j]/2) >= 20))

print(s.check())

if s.check() == sat :
    m = s.model()

    x_start = [m[x[i]] for i in range(chips)]
    y_start = [m[y[i]] for i in range(chips)]
    x_end = [0 for i in range(chips)]
    y_end = [0 for i in range(chips)]

    for i in range(chips):
        x_end[i] = x_start[i].as_long() + m[w[i]].as_long()
        y_end[i] = y_start[i].as_long() + m[h[i]].as_long()

        if m[p[i]]:
            print(f"Chip {i+1} is on PCB1")
        else:
            print(f"Chip {i+1} is on PCB2")
        print(f"x = {m[x[i]]}, y = {m[y[i]]}")
        print(f"w = {m[w[i]]}, h = {m[h[i]]}")
        print(f"x_end = {x_end[i]}, y_end = {y_end[i]}") 