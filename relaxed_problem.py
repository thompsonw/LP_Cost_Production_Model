import numpy as np
from scipy.optimize import minimize

t = None
S = None
L = None 
gamma_l = None

def func(Lambda, sign=1.0):
    """ Objective function """
    obj = gamma_l[0]*t[0]*Lambda[0] 
    for i in range(1, L):
        obj = obj + gamma_l[i]*t[i]*Lambda[i] 
    return sign*(obj)

def func_deriv(Lambda, sign=1.0):
    """ Derivative of objective function """
    deriv_list = []
    for i in range(L):
        deriv_list.append(sign*(t[i]*gamma_l[i]))
    return np.array(deriv_list)

def positive_jac(i, L):
    result = [0] * L
    result[i] = 1
    return result

def if_idle(S):
    production_j = np.sum(S,1)
    for entry in production_j:
        if entry == 0:
            return True
    return False

def main():
    # find optimal lambdas in non-skipping model
    # number of items
    global L
    L = 2

    # number of time periods
    J = 8

    # vector of item times
    global t
    t  = [2, 4]

    T = 1000 # total time
    I0 = [10, 10] # initial inventory
    # demand
    D = [[70, 80], [40, 50], [70, 50], [60, 60], \
         [200, 275], [220, 225], [295, 300], [295, 350]]
    Tau = 10000 # cost tolerance
    a = [2, 1] # changeover cost
    h = [1, 1] # inventory cost
    # demand with a dummy initial demand
    D_init = [[0, 0], [70, 80], [40, 50], [70, 50], \
              [60, 60], [200, 275], [220, 225], [295, 300], [295, 350]]
    
    # initialize random skipping coefficients
    global S
    no_idle_month = False
    while not no_idle_month:
        S = np.random.randint(2, size=(J, L))
        no_idle_month = not if_idle(S)
    global gamma_l
    gamma_l = np.sum(S, 0)
    
    
    cons = []
    # add constraints for all lambda's to be positive
    for i in range(L):
        cons.append({'type': 'ineq',
                     'fun': lambda Lambda: np.array([Lambda[i]]),
                     'jac': lambda Lambda: np.array(positive_jac(i, L))})
    
    #TODO: add positive baseloop constraint
    """
    for j in range(J):
        cons.append({'type': 'ineq',
                     'fun': lambda Lambda: np.array([get_baseloop(j, L, Lambda, ??)]),
                     'jac': lambda Lambda: np.array([??])})
    """
    
    #TODO: add production constraint
    #TODO: add cost constraint
    
    cons = tuple(cons)

    res = minimize(func, [-1.0,1.0], args=(-1.0,), jac=func_deriv,
                   constraints=cons, method='SLSQP', options={'disp': True})

    print(res.x)


if __name__ == "__main__":
    main()