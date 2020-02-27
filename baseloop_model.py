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

L = 3 # number of items
J = 11 # number of time periods
t  = [3, 4, 5] # vector of item times
T = 1400 # total time
I0 = [100, 150, 50] # initial inventory

# demand
D = [[140, 100, 120], [140, 110, 100], [140, 90, 100], [120, 110, 110], \
     [130, 110, 90], [120, 110, 90], [140, 100, 80], [150, 100, 90], \
     [140, 80, 120], [140, 90, 110], [130, 110, 100]]

model = Model('loop minimization')

Lambda = [model.add_var(var_type=INTEGER) for i in range(L)]

model.objective = minimize(xsum(Lambda[i] * t[i] for i in range(L)))

# add constraints
for i in range(1, L+1):
    for j in range(1, J+1):
        coeff = [0] * L
        for k in range(L):
            coeff[k] = t[k]*(I0[i-1]-demand_upto(D, j, i-1))
        coeff[i-1] += j*T
        model += xsum(coeff[i] * Lambda[i] for i in range(L)) >= 0

model += xsum(t[i] * Lambda[i] for i in range(L)) >= 1

model.optimize()

print([Lambda[i].x for i in range(L)])
