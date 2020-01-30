from cost_model import cost_model
import random
import math

def get_baseloop_skipping(Lambda, t, s):
    '''
    compute baseloop at a time period

    PARAM:
    Lambda: a list of L items, each correspond to number of one item
    produced in a loop
    t: a list of time takes to produce one unit of item
    s: a list of L skipping coeffs for this time period
    '''
    baseloop = 0
    for i in range(len(Lambda)):
        baseloop += Lambda[i]*t[i]*s[i]
    return baseloop

def get_random_lambdas(optimal_lambda, neighbourhood):
    '''
    optimal_lambda: a list of L items output by the non-skipping model
    neighbourhood: a number that gives a interval for lambdas we can take in
    the simulation
    '''
    result = optimal_lambda.copy()
    for i in range(len(optimal_lambda)):
        #result[i] = random.uniform(optimal_lambda[i] - neighbourhood, \
                                   #optimal_lambda[i] + neighbourhood)
        result[i] = random.uniform(optimal_lambda[i], optimal_lambda[i] + neighbourhood)
    return result

def simulation(L, J, I0, h, a, trigger_point, D, Lambda, t, Tau, T):
    # initialize placeholders (all zeros) for skipping coefficients
    S = []
    for time_index in range(J):
        S.append([0] * L)

    # initialization
    cur_inventory = I0.copy()
    total_baseloop = 0
    total_holding_cost = 0
    total_changeover_cost = 0

    for j in range(J):
        print('cur_inventory: ', cur_inventory)
        print('Demand this time: ', D[j])
        # determine which items to skip
        for i in range(L):
            item_inventory = cur_inventory[i]
            if item_inventory < max(trigger_point, D[j][i]):
                # produce this month
                S[j][i] = 1
            else:
                #print('item', i, ' inventory: ', item_inventory)
                #print('demand: ', D[j][i])
                print('skip item ', i, ' in time period ', j)
        # compute baseloop at time j
        baseloop = get_baseloop_skipping(Lambda, t, S[j])
        total_baseloop += baseloop
        for i in range(L):
            # feasibility: meet demand at each time period
            if S[j][i] == 1:
                num_baseloop = math.floor(T / baseloop)
                production = Lambda[i] * num_baseloop
                total_changeover_cost += a[i] * num_baseloop
                if production + cur_inventory[i] < D[j][i]:
                    # does not meet demand
                    print('Does not meet demand in time period ', j, \
                          ' for item ', i)
                    return -1
                else:
                    print('production of item ', i, ' is ', production)
            else:
                production = 0

            # update inventory
            cur_inventory[i] = production + cur_inventory[i] - D[j][i]
            # update holding cost
            total_holding_cost += h[i] * cur_inventory[i]

    # feasibility: cost tolerance in a year
    if total_holding_cost + total_changeover_cost > Tau:
        print('Exceeds cost tolerance')
        return -1

    avg_baseloop = total_baseloop/J
    print('feasiblility achieved in this simulation')
    print('average baseloop time is: ', avg_baseloop)
    print('skipping coefficients: ', S)
    return 0

def main():
    # find optimal lambdas in non-skipping model
    # number of items
    L = 2

    # number of time periods
    J = 8

    # vector of item times
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

    kwargs = {'L': L, 'J': J, 't': t, 'T': T, 'I0':I0, 'D': D, 'Tau': Tau,\
              'a': a, 'h': h, 'D_init': D_init}
    optimal_lambda = cost_model(**kwargs)

    # simulation
    num_simulation = 1
    neighbourhood = 0
    trigger_point = 300
    D = D_init
    for i in range(num_simulation):
        print('simulation #', i)
        # randomly generate lambdas within neighbourhood of
        # the optimal non-skipping lambdas
        Lambda = get_random_lambdas(optimal_lambda, neighbourhood)
        print('lambdas: ', Lambda)
        simulation(L, J, I0, h, a, trigger_point, D, Lambda, t, Tau, T)

if __name__ == "__main__":
    main()
