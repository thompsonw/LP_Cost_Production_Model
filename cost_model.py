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

def get_cost_coeff(index, T, J, h, D_init, t, I0, Tau):
    term1 = T * J * (J-1) * h[index] / 2
    J_vector = [i for i in range(J, -1, -1)]
    J_np = np.array(J_vector)
    D_np = np.asarray(D_init)
    h_np = np.array(h)
    JD_np = np.dot(J_np, D_np)
    tmp = J * dot_product(h, I0) - np.dot(JD_np, h_np) - Tau
    #print('term1: ', term1)
    term2 = t[index] * (J * dot_product(h, I0) - np.dot(JD_np, h_np) - Tau)
    return term1 + term2

def cost_model(L, J, t, T, I0, D, Tau, a, h, D_init):
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
            kwargs = {'J': J, 't': t, 'T': T, 'I0':I0, 'Tau': Tau,\
                      'h': h, 'D_init': D_init, 'index': i-1}
            cost_coeff[i-1] = get_cost_coeff(**kwargs)

    # cost constraint
    #print('********************')
    print('cost coeff: ', cost_coeff)
    model += xsum(cost_coeff[i] * Lambda[i] for i in range(L)) <= -J * T * sum(a)

    # looptime >= 1
    model += xsum(t[i] * Lambda[i] for i in range(L)) >= 1

    model.optimize()

    print('result of cost model (non-skipping): ')
    print([Lambda[i].x for i in range(L)])
    return [Lambda[i].x for i in range(L)]

def main():
    L = 3 # number of items
    J = 11 # number of time periods
    t  = [3, 4, 5] # vector of item times
    T = 1400 # total time
    I0 = [100, 150, 50] # initial inventory

    # demand
    D = [[140, 100, 120], [140, 110, 110], [140, 90, 100], [120, 110, 110], \
          [130, 110, 90], [120, 110, 90], [140, 100, 80], [150, 100, 90], \
          [140, 80, 120], [140, 90, 110], [130, 110, 100]]

    Tau = 10000 # cost tolerance
    a = [10, 10, 20] # changeover cost
    h = [1, 2, 2] # inventory cost

    # demand with a dummy initial demand
    D_init = [[0, 0, 0], [140, 100, 120], [140, 110, 110], [140, 90, 100], [120, 110, 110], \
              [130, 110, 90], [120, 110, 90], [140, 100, 80], [150, 100, 90], \
              [140, 80, 120], [140, 90, 110], [130, 110, 100]]

    kwargs = {'L': L, 'J': J, 't': t, 'T': T, 'I0':I0, 'D': D, 'Tau': Tau,\
              'a': a, 'h': h, 'D_init': D_init}
    cost_model(**kwargs)

if __name__=='__main__':
    main()
