import numpy as np
from mip import Model, xsum, maximize, minimize, BINARY, INTEGER

def demand_upto(D, current_time, item_index):
    # D size: J x L
    result = 0
    for period in range(current_time):
        result += D[period][item_index]
    return result

def dot_product(a, b):
    # a and b are lists of the same length
    result = 0
    for i in range(len(a)):
        result += a[i]*b[i]
    return result

def get_cost_coeff(index):
    term1 = T * J * (J-1) * h[index] / 2
    J_vector = [i for i in range(8, -1, -1)]
    J_np = np.array(J_vector)
    D_np = np.asarray(D_init)
    h_np = np.array(h)
    term2 = t[i-1] * (J * dot_product(h, I0) - np.dot(np.dot(J_np, D_np),h_np) - Tau)
    return term1 + term2

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

model = Model('loop minimization')

Lambda = [model.add_var(var_type=INTEGER) for i in range(L)]

model.objective = minimize(xsum(Lambda[i] * t[i] for i in range(L)))

cost_coeff = [0] * L

# add constraints
for i in range(1, L+1):
    for j in range(1, J+1):
        # baseloop constraints
        coeff = [0] * L
        for k in range(L):
            coeff[k] = t[k]*(I0[i-1]-demand_upto(D, j, i-1))
        coeff[i-1] += j*T
        model += xsum(coeff[i] * Lambda[i] for i in range(L)) >= 0
        # add coeffs in for cost constraint
        cost_coeff[i-1] = get_cost_coeff(i-1)

# cost constraint
#model += xsum(cost_coeff[i] * Lambda[i] for i in range(L)) <= J * T * sum(a)

# looptime >= 1
model += xsum(t[i] * Lambda[i] for i in range(L)) >= 1

model.optimize()

print([Lambda[i].x for i in range(L)])
