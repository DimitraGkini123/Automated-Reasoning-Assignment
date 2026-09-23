from z3 import *

Maximum_Iterations = 36 #Se kathe iteration to a = a+5 minimum, ara 1+5n=180, ara n=(180-1)/5

a = [Int(f"a{i}") for i in range (Maximum_Iterations + 1)] 
b = [Int(f"b{i}") for i in range (Maximum_Iterations + 1)] 

nondent = [Bool(f"nondent{i}") for i in range (Maximum_Iterations)] #Non deterministic boolean var

for k in range(11):

    s = Solver()
    
    s.add(a[0] == 1)
    s.add(b[0] == 1)

#------------While Loop-------------#

    for i in range(Maximum_Iterations): # Trexei panta 36 fores kai exei "3 states". true, false, terminated (Den mporesa na vrw tropo na kanw kalo while loop)

        True_nondent = And(a[i+1] == a[i] + 2* (b[i] + 3) , b[i+1] == b[i] + 3)

        False_nondent = And(a[i+1] == a[i] +5 , b[i+1] == b[i] + a[i])

        Terminated = And (a[i+1] == a[i], b[i+1] == b[i])

        s.add(If( a[i] < 180, If(nondent[i], True_nondent, False_nondent), Terminated)) 
        #Les an a<180 true alliws false. To false einai to terminated state kai to true state, analoga me to nondent kanei eite to true eite to false path
        #Den to kanw me if a>180 break, giati a kai b einai Z3_Int, to opoio apoti fainetai einai diaforetiko tou aplou int


    s.add(a[Maximum_Iterations] >= 180)     #Elgxoume an eimaste enots tou loop
    s.add(b[Maximum_Iterations] == 190 + k) 

    if s.check() == sat: 

        m = s.model()

        Choices = []    #Kratame to pote to nondent dinei T kai F
        Values = []     #Kratame ta ai kai bi gia na paroyme tis telikes times kai na sygkrinoume me 190+k

        for i in range(Maximum_Iterations): #kratame times ai kai bi otan mas noizei
            a_i = m.eval(a[i]).as_long()    #Den eixa empneysi gia onoma variable
            b_i = m.eval(b[i]).as_long()    #TO .AS_LONG METATREPEI TO Z3 INT SE REAL INT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            if a_i >= 180:
                Values.append((a_i,b_i))
                break

            Values.append((a_i,b_i))  #apothikevw ola ta values gia na deiksw to "provide one complete run leading to that crash" 

            if is_true(m.eval(nondent[i])): #TO IS_TRUE KANEI TO Z3 TRUE SE PYTHON TRUE
                Choices.append("True")
            else:
                Choices.append("False")

        print("For k = ", k, " : ! CRASH !")
        print("Choises: ",Choices)
        print("Values: ",Values)
        print("Final (a,b) = (",Values[-1][0],",",Values[-1][-1],")")
        print("\n")

    else: 
        print("k = ",k, " : SAFE")
        print("\n")






