from z3 import *

Maximum_Iterations = 36 #Maximum Number of Iterations

a = [Int(f"a{i}") for i in range (Maximum_Iterations + 1)] 
b = [Int(f"b{i}") for i in range (Maximum_Iterations + 1)] 

nondent = [Bool(f"nondent{i}") for i in range (Maximum_Iterations)] #Non deterministic boolean variable

for k in range(11):

    s = Solver()
    
    s.add(a[0] == 1)
    s.add(b[0] == 1)

    for i in range(Maximum_Iterations): # It runs for 36 iterations and produces one of 3 states; true, false, terminated
        
        True_nondent = And(a[i+1] == a[i] + 2* (b[i] + 3) , b[i+1] == b[i] + 3) #True Branch

        False_nondent = And(a[i+1] == a[i] +5 , b[i+1] == b[i] + a[i]) #False Branch

        Terminated = And (a[i+1] == a[i], b[i+1] == b[i]) #Terminated Branch = No change

        s.add(If( a[i] < 180, If(nondent[i], True_nondent, False_nondent), Terminated)) 
        #If a < 180 True, else False.
        #False represents the terminated state
        #True represents that one of the 2 possible changes of var a and var b happen (based on value of nondent)

    s.add(a[Maximum_Iterations] >= 180)     #Check if we are still within the loop
    s.add(b[Maximum_Iterations] == 190 + k) #Add the constraint we are checking for 

    if s.check() == sat: 

        m = s.model()

        Choices = []    #List to store T or F values of nondent for every case iteration
        Values = []     #List to store values of a and b in order to comapre with 190 + k

        for i in range(Maximum_Iterations): 
            a_i = m.eval(a[i]).as_long()    #Convert a_i from Z3 int to Python int
            b_i = m.eval(b[i]).as_long()    #Convert b_i from Z3 int to Python int

            if a_i >= 180:
                Values.append((a_i,b_i)) #Store values of a and b before the break - the final values of a and b
                break

            Values.append((a_i,b_i))   #Store values of a and b 

            if is_true(m.eval(nondent[i])): #Convert Z3 True to Python True
                Choices.append("True") #Store value of nondent
            else:
                Choices.append("False") #Store value of nondent


        print("For k = ", k, " : ! CRASH !")
        print("Choises: ",Choices)
        print("Values: ",Values)
        print("Final (a,b) = (",Values[-1][0],",",Values[-1][-1],")")
        print("\n")

    else: 
        print("k = ",k, " : SAFE")
        print("\n")






