from mip import Model, xsum, maximize, minimize, BINARY, INTEGER

def demand_upto(D, j, item):
    # D size: J x L
    result = 0
    for period in range(j):
        result += D[period][item]
    return result

def dot_product(a, b):
    # a and b are lists of the same length
    result = 0
    for i in range(len(a)):
        result += a[i]*b[i]
    return result

# number of items
L = 2

# number of time periods
J = 3

# vector of item times
t  = [2, 4]

# answers lambda = [2; 1]

T = 300
I0 = [10, 100]
D = [[40, 30], [60, 60], [100, 100]]

model = Model('loop minimization')

Lambda = [model.add_var(var_type=INTEGER) for i in range(L)]
#Lambda[0] = 1
#Lambda[1] = 1

model.objective = minimize(xsum(Lambda[i] * t[i] for i in range(L)))

# add constraints
for i in range(1, L+1):
    for j in range(1, J+1):
        tmp = D[j-1][i-1] - I0[i-1] + demand_upto(D, j, i-1)
        model += xsum(t[i] * Lambda[i] for i in range(L)) * (D[j-1][i-1] - I0[i-1] + demand_upto(D, j, i-1)) <= j*T*3

model += xsum(t[i] * Lambda[i] for i in range(L)) >= 1

model.optimize()

print([Lambda[i].x for i in range(L)])
