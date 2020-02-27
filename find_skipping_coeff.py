from cost_model import cost_model
import random
import math


def random_simulation(L, J, I0, h, a, trigger_point, D, t, Tau, T, num_simulation, optimal_lambda, neighbourhood):

    feasible_results = {}
    infeasible_results = []
    for i in range(num_simulation):
        Lambda = get_random_lambdas(optimal_lambda, neighbourhood)
        avg_baseloop = get_average_baseloop_time(L, J, I0, h, a, trigger_point, D, Lambda, t, Tau, T)

        if avg_baseloop != -1:
            feasible_results[avg_baseloop] = Lambda
        else:
            infeasible_results.append(Lambda)

    return (feasible_results, infeasible_results)


def get_average_baseloop_time(L, J, I0, h, a, trigger_point, D, Lambda, t, Tau, T):
    inventory = []

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
        inventory_j = []
        # determine which items to skip
        for i in range(L):
            item_inventory = cur_inventory[i]
            if item_inventory < max(trigger_point, D[j][i]):
                # produce this month
                S[j][i] = 1
        # compute baseloop at time j
        baseloop = get_baseloop_skipping(Lambda, t, S[j])
        total_baseloop += baseloop
        for i in range(L):
            # feasibility: meet demand at each time period
            if S[j][i] == 1:
                num_baseloop = math.floor(T / baseloop)
                production = Lambda[i] * num_baseloop
                if sum([coeff for coeff in S[j]]) > 1:
                    total_changeover_cost += a[i] * num_baseloop
                if production + cur_inventory[i] < D[j][i]:
                    # does not meet demand
                    return -1
            else:
                production = 0

            inventory_j.append(production+cur_inventory[i])
            # update inventory
            cur_inventory[i] = production + cur_inventory[i] - D[j][i]
            # update holding cost
            total_holding_cost += h[i] * cur_inventory[i]
        inventory.append(inventory_j)

    # feasibility: cost tolerance in a year
    if total_holding_cost + total_changeover_cost > Tau:
        #print('Exceeds cost tolerance')
        return -1

    avg_baseloop = total_baseloop/(J*L)
    print('feasiblility achieved in this simulation')
    print('average baseloop time is: ', avg_baseloop)
    print('skipping coefficients: ', S)
    print('inventory: ', inventory)
    print('total_holding_cost: ', total_holding_cost)
    print('total_changeover_cost: ', total_changeover_cost)
    return avg_baseloop


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


def get_random_lambdas(optimal_lambda, neighborhood):
    '''
    optimal_lambda: a list of L items output by the non-skipping model
    neighbourhood: a number that gives a interval for lambdas we can take in
    the simulation
    '''
    result = optimal_lambda.copy()
    for i in range(len(optimal_lambda)):
        generated_val = -1
        while generated_val <= 0:
            generated_val = int(random.uniform(optimal_lambda[i] - neighborhood, \
                                   optimal_lambda[i] + neighborhood))
        result[i] = generated_val
    return result


def get_optimal_siumulation_results(some_simulation_result):

    if len(some_simulation_result) == 0:
        return -1
    else:
        optimal_avg_baseloop = min(some_simulation_result.keys())
        optimal_lambda = some_simulation_result[optimal_avg_baseloop]

        return (optimal_avg_baseloop, optimal_lambda)


def display_simulation_results(feasible_results, optimal_result, infeasible_results):

    if optimal_result != -1:
        print("***************************")
        print("Simulation Output:")
        print(" ")
        print("Infeasible Choices of Lambda:")
        print(" ")
        #for Lambda in infeasible_results:
            #print("Infeasible: {}".format(Lambda))

        print(" ")
        print("Feasible choices of Lambda:")
        print(" ")
        #for some_avg_baseloop in feasible_results.keys():
            #print(str(some_avg_baseloop) + ": {}".format(feasible_results[some_avg_baseloop]))

        print(" ")
        print("Optimal Choice of Lambdas: {}".format(optimal_result[1]))
        print("Optimal average baseloop: {}".format(optimal_result[0]))
        print("***************************")

    else:
        print(" ")
        print("***************************")
        print("Simulation Output:")
        print(" ")
        print("No feasible solution found")
        print("***************************")


def main():
    '''
    L = 3;
    J = 11;

    t = [3;4;5];
    T = 1400;
    I0 = [100;150;50];
    D = [140 100 120; 140 110 110; 140 90 100; 120 110 110;130 110 90;
    120 110 90; 140 100 80; 150 100 90; 140 80 120; 140 90 110; 130 110 100]';

    h = [1;2;2];
    a = [20;10;15];
    costtol =  10000
    '''
    random.seed(0)
    L = 3 # number of items
    J = 11 # number of time periods
    t  = [3, 4, 5] # vector of item times
    T = 1400 # total time
    I0 = [100, 150, 50] # initial inventory

    # demand
    D = [[140, 100, 120], [140, 110, 100], [140, 90, 100], [120, 110, 110], \
         [130, 110, 90], [120, 110, 90], [140, 100, 80], [150, 100, 90], \
         [140, 80, 120], [140, 90, 110], [130, 110, 100]]

    Tau = 10000 # cost tolerance
    a = [20, 10, 15] # changeover cost
    h = [1, 2, 2] # inventory cost

    # demand with a dummy initial demand
    D_init = [[0, 0, 0], [140, 100, 120], [140, 110, 100], [140, 90, 100], [120, 110, 110], \
              [130, 110, 90], [120, 110, 90], [140, 100, 80], [150, 100, 90], \
              [140, 80, 120], [140, 90, 110], [130, 110, 100]]

    kwargs = {'L': L, 'J': J, 't': t, 'T': T, 'I0':I0, 'D': D, 'Tau': Tau,\
              'a': a, 'h': h, 'D_init': D_init}

    #optimal_lambda = cost_model(**kwargs)
    # output of cost model: [24, 12, 13]
    #optimal_lambda = [21, 11, 12]
    # output of skipping model after 1M simulations: [18, 8, 11]
    optimal_lambda = [18, 8, 11]
    #num_simulation = 1000000
    #neighbourhood = 30
    trigger_point = 100
    #D = D_init
    avg_baseloop = get_average_baseloop_time(L, J, I0, h, a, trigger_point, D, optimal_lambda, t, Tau, T)

    '''
    #Run simulation:
    simulation_results = random_simulation(L, J, I0, h, a, trigger_point, D, t, Tau, T, num_simulation, optimal_lambda, neighbourhood)
    feasible_results = simulation_results[0]
    infeasible_results = simulation_results[1]
    optimal_result = get_optimal_siumulation_results(feasible_results)
    display_simulation_results(feasible_results, optimal_result, infeasible_results)
    '''



if __name__ == "__main__":
    main()
