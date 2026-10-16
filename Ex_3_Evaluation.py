from z3 import *

#Trips
#T = 10
#s = Solver()

T=0
# while s.check() == sat:
while True:
    s = Optimize()

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

    # cost of each trip ( in food units and time)
    travel = [Int(f"travel_{i}") for i in range(T)]
    total = [Int(f"total_{t}") for t in range(T + 1)]

    # initial state of villages
    s.add(A[0] == 60)
    s.add(B[0] == 60)
    s.add(C[0] == 60)
    #s.add(Tr[0] == 130)
    s.add(Tr[0] == 150)
    s.add(P[0] == "S")
    s.add(total[0] == 0)
    s.add(d[0] == 0) #redundant

    #add the caps ( for villages and truck )
    for i in range(T+1):
        s.add(And(A[i] >= 0, A[i] <= 90))
        s.add(And(B[i] >= 0, B[i] <= 120))
        s.add(And(C[i] >= 0, C[i] <= 90))
        s.add(And(Tr[i] >= 0, Tr[i] <= 150))

        s.add(Or(P[i]=="S", P[i]=="A", P[i]=="B", P[i]=="C"))

        #The amount of products the truck leaves, has to be less than the amount of products that the truck carries at this time
    #for i in range(T+1):
        s.add(d[i] >= 0)
        s.add(Implies(P[i] == "S", d[i] == 0)) #EBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALAEBALA
        #s.add(Implies(Tr[i] == 0, d[i] == 0))


        #cost of each trip 
    for i in range(T):
        #allowed routes
        s.add(Implies(P[i]== "S", Or(P[i+1]== "A", P[i+1] == "C")))                 # when truck is in S, it can go S-->A or S--> C
        s.add(Implies(P[i]== "A", Or(P[i+1]== "B", P[i+1] == "C", P[i+1] == "S")))  # A--> B or A--> C or A--> S
        s.add(Implies(P[i]== "B", Or(P[i+1]== "A", P[i+1] == "C")))                 # B-->A  or B-->C
        s.add(Implies(P[i]== "C", Or(P[i+1]== "B", P[i+1] == "S", P[i+1] == "A")))  # C--> B or C-->S or S-->A

        #Before the truck starting one route that will take time t1, it has to make sure that all villages have more than t1 units of food available
        s.add(And(A[i] >= travel[i], B[i] >= travel[i], C[i] >= travel[i]))

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


#when truck arrives at truck A, it leaves d[i] products while the other villages still eat the food that corresponds to the time that the truck travelled
#when truck arrives in any village, it drops off d[i] units of food

        s.add(Implies(P[i+1]=="A", And(d[i+1] <= 90 - A[i] + travel[i],
                                    Tr[i+1] == Tr[i] - d[i+1], 
                                    A[i+1] == A[i] - travel[i] + d[i+1], 
                                    B[i+1]==B[i] - travel[i], 
                                    C[i+1]==C[i] - travel[i])))

        s.add(Implies(P[i+1]=="B", And(d[i+1] <= 120 - B[i] + travel[i],
                                    Tr[i+1] == Tr[i] - d[i+1],
                                    A[i+1]==A[i] - travel[i], 
                                    B[i+1] == B[i] - travel[i] + d[i+1], 
                                    C[i+1]==C[i] - travel[i])))

        s.add(Implies(P[i+1]=="C", And(d[i+1] <= 90 - C[i] + travel[i], 
                                    Tr[i+1] == Tr[i] - d[i+1],
                                    A[i+1]==A[i] - travel[i],
                                    B[i+1]==B[i] - travel[i],
                                    C[i+1] == C[i] - travel[i] + d[i+1])))

        s.add(Implies(P[i+1]=="S", And(d[i+1] == 0,
                                    Tr[i+1] == 150,
                                    A[i+1] == A[i] - travel[i],  
                                    B[i+1] == B[i] - travel[i],  
                                    C[i+1] == C[i] - travel[i])))
        
        s.add(total[i+1] == total[i] + travel[i])
        s.add(travel[i] >= 0)
        s.add(total[i] >= 0)

        infPath = Int("infPath")
        infPathStart = Int("loop_start")

        choices = []
        s.add(Or([And(infPathStart == k,
                    P[T] == P[k],
                    Tr[T] >= Tr[k],
                    A[T] >= A[k], B[T] >= B[k], C[T] >= C[k],
                    infPath == total[T] - total[k])
                for k in range(T)])) 
        s.add(infPath > 0)
        print(choices)

        s.minimize(infPath)
        
    if s.check() == sat:
        model = s.model()
        print(s.check())
        print(
        "\nTotal_Time = ", model.eval(total[T]),
        # "\nloop_start[T] = ", model.eval(choices[T]),
        "\n\n\n"
        )

        # for i in range(T):
        #     # print("loop starts at step", model.eval(loop_start[t]), "cycle time", model.eval(cycle))
        #     print(s.check())
        #     print(t)
        #     print(
        #     # "Infinite path = ", model.eval(A[t]), ",", model.eval(B[t]), ",", model.eval(C[t]),
        #     "For i =", i,
        #     "\nA[i] = ", model.eval(A[i]),
        #     "\nB[i] = ", model.eval(B[i]),
        #     "\nC[i] = ", model.eval(C[i]),
        #     "\nTotal_Time = ", model.eval(total[i]),
        #     "\nTravel next dest = ", model.eval(travel[i]),
        #     "\nd will be given to ", model.eval(P[i+1]), " = ", model.eval(d[i+1]),
        #     "\nTr = ", model.eval(Tr[i]),
        #     "\nPostion = ", model.eval(P[i]),
        #     "\nNewPosition = ", model.eval(P[i+1]),
        #     "\n\n\n" 
        #     )
        #     #life = model.eval(total[i+1], model_completion=True).as_long() + min(model.eval(A[i+1], model_completion=True).as_long(), 
        #                                                                         #  model.eval(B[i+1], model_completion=True).as_long(), 
        #                                                                         #  model.eval(A[i+1], model_completion=True).as_long())
        #     print("Total_Time survived = ",
        #         model.eval(total[i], model_completion=True).as_long() + 
        #         min(model.eval(A[i], model_completion=True).as_long(), 
        #             model.eval(B[i], model_completion=True).as_long(), 
        #             model.eval(A[i], model_completion=True).as_long()))
    
        print(T)
        T = T+1
        # #s.maximize(life)
    elif T>10 and (s.check() == unsat or T>=50):
        print("the model is made unsat ")
        break
    else:
        T = T+1



        
        # if(model.eval(A[i], model_completion=True).as_long() - model.eval(travel[i], model_completion=True).as_long() != 0 and 
        #    model.eval(B[i], model_completion=True).as_long() - model.eval(travel[i], model_completion=True).as_long() != 0 and 
        #    model.eval(C[i], model_completion=True).as_long() - model.eval(travel[i], model_completion=True).as_long() != 0):
    
