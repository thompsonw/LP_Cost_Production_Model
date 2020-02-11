import numpy as np
from random import *
from mip import Model, xsum, maximize, minimize, BINARY, INTEGER

# number of items
L = 2

# number of time periods
J = 8

# vector of item times
t  = [2, 4]

# answers lambda = [2; 1]

T = 1000 # total time
I0 = [10, 10] # initial inventory
D = [[70, 80], [40, 50], [70, 50], [60, 60], \
     [200, 275], [220, 225], [295, 300], [295, 350]] # demand
Tau = 10000 # cost tolerance
a = [2, 1] # changeover cost
h = [1, 1] # inventory cost
D_init = [[0, 0], [70, 80], [40, 50], [70, 50], \
          [60, 60], [200, 275], [220, 225], [295, 300], [295, 350]] # demand


def demand_upto(demandMatrix, current_time, item_index):
    # D size: J x L
    demand = 0
    for period in range(current_time):
        demand += demandMatrix[period][item_index]
    return demand


def get_cost_coeff(index, storageCost, changeoverCost, initialInventory, productTime, costTolerance, D_init, totalTime, J):

    term1 = totalTime * J * (J-1) * storageCost[index] / 2

    J_vector = [i for i in range(8, -1, -1)]
    J_np = np.array(J_vector)
    demand_np = np.asarray(D_init)
    storageCost_np = np.array(storageCost)

    term2 = productTime[i-1] * (J * dot_product(storageCost, initialInventory) - np.dot(np.dot(J_np, demand_np),storageCost_np) - costTolerance)
    return term1 + term2

def dot_product(vector1, vector2):
    # vector1 and vector2 are lists of the same length
    dotProduct = 0
    for i in range(len(vector1)):
        result += vector1[i]*vector2[i]
    return dotProduct

def optimize_Base_loop(L, J, totalTime, initialInventory, demandMatrix, D_init, storageCost, changeoverCost, costTolerance, skipCoeffMatrix, productTime):

    model = Model('loop minimization')
    Lambda = [model.add_var(var_type=INTEGER) for i in range(L)]
    model.objective = minimize(xsum(Lambda[i] * productTime[i] for i in range(L)))

    cost_coeff = [0] * L

    #Add Constraints:
    for i in range(1, L+1):
        for j in range(1, J+1):

            # baseloop constraints
            coeff = [0] * L
            for k in range(L):
                coeff[k] = productTime[k]*(initialInventory[i-1]-demand_upto(demandMatrix, j, i-1))
            coeff[i-1] += j*totalTime
            model += xsum(coeff[i] * Lambda[i] for i in range(L)) >= 0

            # add coeffs in for cost constraint
            cost_coeff[i-1] = get_cost_coeff(i-1, storageCost, changeoverCost, initialInventory, productTime, costTolerance, D_init, totalTime, J)

    # looptime >= 1
    model += xsum(t[i] * Lambda[i] for i in range(L)) >= 1

    # cost constraint
    #model += xsum(cost_coeff[i] * Lambda[i] for i in range(L)) <= J * T * sum(a)
    model.optimize()
    #print([Lambda[i].x for i in range(L)])
    return [Lambda[i].x for i in range(L)]

def optimizeSkipping(skipCoeffMatrix, Lambda):
    pass #recursive approach?

def modifySkipCoeffMatrix(skipCoeffMatrix):

    #Determine the number of coefficients to change:
    swaps = 10
    for i in range(swaps):
        row = random.randint(0, len(skipCoeffMatrix)-1)
        column = random.randint(0,len(skipCoeffMatrix[0])-1)

        if (skipCoeffMatrix[row][column] == 0):
            skipCoeffMatrix[row][column] = 1
        else:
            skipCoeffMatrix[row][column] = 0
    return skipCoeffMatrix

def displaySkipCoeff(skipCoeffMatrix):

    for i in range(len(skipCoeffMatrix)):
        for j in range(len(skipCoeffMatrix[i])):
           print("Coefficient for item {} in time period {}:".format(i+1,j+1) + "" + str(skipCoeffMatrix[i][j]))
