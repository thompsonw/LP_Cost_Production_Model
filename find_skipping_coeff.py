from cost_model import cost_model
import random
import math
from BaseLoop_optimizer_Input_Reader import *


def random_simulation(L, J, I0, h, a, trigger_point, D, t, Tau, T, num_simulation, optimal_lambda, neighbourhood):
    feasible_results = {}
    for i in range(num_simulation):
        Lambda = get_random_lambdas(optimal_lambda, neighbourhood)
        avg_baseloop = get_average_baseloop_time(L, J, I0, h, a, trigger_point, D, Lambda, t, Tau, T, False)

        if avg_baseloop != -1:
            feasible_results[avg_baseloop] = Lambda

    return feasible_results


def get_average_baseloop_time(L, J, I0, h, a, trigger_point, D, Lambda, t, Tau, T, print_optimal_info):
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

    if print_optimal_info:
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


def display_simulation_results(optimal_result):
    '''
    Displays the optimal lamdbas and average base loop found in the Simulation
    or indicate that no feasible solutions were found

    PARAMETERS:
    optimal_result := a tuple of the average base loop and its corresponding
                      lambdas

    RETURN:
    None
    '''
    print("***************************")
    print("Simulation Output:")
    if optimal_result != -1:
        print("Optimal Choice of Lambdas: {}".format(optimal_result[1]))
        print("Optimal average baseloop: {}".format(optimal_result[0]))
        print("***************************")

    else:
        print("No feasible solution found")
        print("***************************")


def main():
    random.seed(0)

    csv_input = BaseLoopInputdata('Input_Data.csv')
    demand_schedule = csv_input.entire_Demand_Schedule
    unit_production_time = csv_input.all_Production_Times
    holding_cost = csv_input.inventory_Cost
    num_items = len(holding_cost)
    num_periods = len(demand_schedule)
    demand_schedule_init = demand_schedule.copy()
    demand_schedule_init.insert([0]*num_items, 0)
    changeover_cost = csv_input.changeover_Cost
    initial_inventory = csv_input.initial_inventories
    total_time = csv_input.total_time
    cost_tolerance = csv_input.cost_tolerance

    '''
    num_items = 3 # total number of items
    num_periods = 11 # total number of time periods
    unit_production_time = [3, 4, 5] # vector of item production time per unit
    total_time = 1400
    initial_inventory = [100, 150, 50]

    # demand
    demand_schedule = [[140, 100, 120], [140, 110, 110], [140, 90, 100], \
                       [120, 110, 110], [130, 110, 90], [120, 110, 90], \
                       [140, 100, 80], [150, 100, 90], [140, 80, 120], \
                       [140, 90, 110], [130, 110, 100]]

    cost_tolerance = 10000 # cost tolerance
    changeover_cost = [10, 10, 20] # changeover cost
    holding_cost = [1, 2, 2] # inventory cost

    # demand with a dummy initial demand
    demand_schedule_init = [[0, 0, 0], [140, 100, 120], [140, 110, 110], \
                            [140, 90, 100], [120, 110, 110], [130, 110, 90], \
                            [120, 110, 90], [140, 100, 80], [150, 100, 90], \
                            [140, 80, 120], [140, 90, 110], [130, 110, 100]]
    '''

    kwargs = {'num_items': num_items, 'num_periods': num_periods, \
              'unit_production_time': unit_production_time, \
              'total_time': total_time, 'initial_inventory': initial_inventory, \
              'demand_schedule': demand_schedule, 'cost_tolerance': cost_tolerance, \
              'changeover_cost': changeover_cost, 'holding_cost': holding_cost, \
              'demand_schedule_init': demand_schedule_init}
    optimal_lambdas = cost_model(**kwargs)

    # output of skipping model after 1M simulations: [18, 8, 11]
    #optimal_lambda = [18, 8, 11]

    num_simulation = 1000
    neighbourhood = 30
    trigger_point = 100

    '''
    avg_baseloop = get_average_baseloop_time(num_items, num_periods, \
    initial_inventory, holding_cost, changeover_cost, trigger_point, \
    demand_schedule, optimal_lambda, unit_production_time, cost_tolerance, \
    total_time, print_optimal_info)
    '''

    # Run simulations
    feasible_results = random_simulation(num_items, num_periods, \
                                         initial_inventory, holding_cost,\
                                         changeover_cost, trigger_point, \
                                         demand_schedule, unit_production_time,\
                                         cost_tolerance, total_time, \
                                         num_simulation, optimal_lambdas, \
                                         neighbourhood)
    optimal_result = get_optimal_siumulation_results(feasible_results)
    display_simulation_results(optimal_result)

if __name__ == "__main__":
    main()
