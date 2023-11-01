# -*- coding: utf-8 -*-
from gurobipy import *
model=Model("SimpleLP")

###########################################################  Parámetros  #############################################################

plantas={1:1, 2:2, 3:3, 4:4, 5:5}
importadoras={1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10}
meses = [0, 1, 2, 3, 4]
oferta_max={(1,1):500,(1,2):400,(1,3):400,(1,4):300,(2,1):450,(2,2):400,(2,3):450,(2,4):350,(3,1):450,(3,2):400,(3,3):450,(3,4):350,(4,1):500,(4,2):400,(4,3):450,(4,4):300,
               (5,1):500,(5,2):400,(5,3):400,(5,4):300}

#Oferta Maxima: oferta_max[(planta,mes):cantidad maxima para ofrecer]


demanda={(1,1):100,(1,2):0,(1,3):100,(1,4):300, (2,1):50,(2,2):100,(2,3):200,(2,4):250, (3,1):150,(3,2):100,(3,3):100,(3,4):100, (4,1):150,(4,2):100,(4,3):200,(4,4):50, (5,1):100,(5,2):50,(5,3):100,(5,4):25,
            (6,1):200,(6,2):50,(6,3):200,(6,4):25, (7,1):200,(7,2):50,(7,3):100,(7,4):25, (8,1):200,(8,2):50,(8,3):200,(8,4):25, (9,1):200,(9,2):50,(9,3):100,(9,4):25, (10,1):200,(10,2):50,(10,3):200,(10,4):25} 

#Demanda: demanda[(importadora,mes):cantidad demandada]


costo_k={(1,1):12000,(1,2):10000,(1,3):50000,(1,4):30000,(2,1):13000,(2,2):100000,(2,3):40000,(2,4):30000,(3,1):14000,(3,2):50000,(3,3):30000,(3,4):20000,(4,1):15000,(4,2):50000,(4,3):20000,(4,4):20000,

#Costo fijo por uso: costo_k[(planta,mes):costo]

         
costo_c={(1,1):10,(1,2):10,(1,3):10,(1,4):10,(1,5):10,(1,6):15,(1,7):15,(1,8):15,(1,9):15,(1,10):15,(2,1):5,(2,2):5,(2,3):5,(2,4):5,(2,5):5,(2,6):5,(2,7):5,(2,8):5,(2,9):5,(2,10):5,
         (3,1):8,(3,2):8,(3,3):8,(3,4):8,(3,5):8,(3,6):8,(3,7):10,(3,8):10,(3,9):10,(3,10):10,(4,1):5,(4,2):5,(4,3):5,(4,4):5,(4,5):5,(4,6):5,(4,7):5,(4,8):5,(4,9):5,(4,10):5,
         (5,1):5,(5,2):5,(5,3):5,(5,4):5,(5,5):5,(5,6):6,(5,7):6,(5,8):6,(5,9):6,(5,10):6}

#Costo fijo por transporte y producción: costo_c[(planta,importador):costo]


##############################################################  Variables  ############################################################

x = model.addVars(plantas.keys(), importadoras.keys(), meses, name= 'x', vtype= 'I') #Envío dependiente de planta,importadora y mes
y = model.addVars(plantas.keys(), meses, name= 'y', vtype= 'I') #Produccion dependiente de planta y mes
z = model.addVars(plantas.keys(), meses, name= 'y', vtype= 'I') #Stock dependiente de planta y mes
w = model.addVars(plantas.keys(), meses, name= 'y', vtype= 'I') #Actividad de la planta dependiente de planta y mes

#############################################################  Restricciones  #########################################################

for i in meses[1:]:
    
    for j in plantas:
        model.addConstr(quicksum(x[j,k,i] for k in importadoras)<=oferta_max[j,i])
        model.addConstr(y[j,i]<=oferta_max[j,i])
        
    for j in importadoras:
        model.addConstr(quicksum(x[k,j,i]for k in plantas)==demanda[j,i])
    
    for j in plantas:
        model.addConstr(y[j,i]+z[j,i-1]>=quicksum(x[j,k,i] for k in importadoras))

    for j in plantas:
        model.addConstr(z[j,i]==y[j,i]+z[j,i-1]-quicksum(x[j,k,i] for k in importadoras))
        
    for j in plantas:
        model.addConstr(10000000000000000000000000000000*w[j,i]>=quicksum(x[j,k,i] for k in importadoras))


    model.addConstr(quicksum(y[j,i]+z[j,i-1] for j in plantas)>=quicksum(demanda[j,i] for j in importadoras) )
    for j in plantas:
        for k in importadoras:
            model.addConstr(x[j,k,i]>=0)
    for j in plantas:
        model.addConstr(y[j,i]>=0)
        model.addConstr(z[j,i]>=0)
        model.addConstr(w[j,i]>=0)
for i in plantas:
    model.addConstr(z[i,0]==0)
    model.addConstr(z[i,4]==0)
    
model.setObjective(quicksum(quicksum(w[j,i]*costo_k[j,i]+2*z[j,i]+ quicksum(x[j,k,i]*costo_c[j,k]for k in importadoras) for i in meses[1:]) for j in plantas), GRB.MINIMIZE)
#Funcion objetivo

model.update()
model.optimize()
print()
print("Optimal value=", model.ObjVal)

for i in plantas:
    print('Planta_%s'%(i))
    for j in meses[1:]: 
        print('Mes_%s'%(j))
        print('Produccion_:%s'%(y[i,j].X))
        print('Stock_:%s'%(z[i,j]).X)
        for k in importadoras:
            print('Envio importadora_%s: %s'%(k,x[i,k,j].X))
    