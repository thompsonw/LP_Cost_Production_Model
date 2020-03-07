# The cost model: finds optimal base loop that satisfies cost constraint,
# positive base loop, and have inventory meet demand at each time period.
# @author Rosa Zhou
# @author Will Thompson

import numpy as np
from mip import Model, xsum, maximize, minimize, BINARY, INTEGER
from input_reader import *


def demand_upto(demand_schedule, current_time, item):
    '''
    Computes the total demand from the initial time period to the
    current time period for the given item

    PARAMETERS:
    demand_schedule := a matrix of size (J, L) containing demand for each item
    in each time period
    current_time := index of current time period
    item := index of the item

    RETURN:
    demand_so_far := the total demand from the initial time period to the
    current time period for the given item
    '''
    demand_so_far = 0
    for period in range(current_time):
        demand_so_far += demand_schedule[period][item]
    return demand_so_far


def get_cost_coeff(item_index, total_time, num_periods, holding_cost, \
                   demand_schedule_init, unit_production_time, \
                   initial_inventory, cost_tolerance):
    '''
    Compute the coefficient for a given item in the cost constraint of the
    closed form of linear program

    PARAMETERS:
    item_index := index of the given item
    total_time := total time in one period
    num_periods := total number of time periods
    holding_cost := inventory cost for each item
    demand_schedule_init := demand schedule including the initial time period
    unit_production_time := time needed to produce one unit for each item
    initial_inventory := initial inventory for each item
    cost_tolerance := total cost tolerance for the year

    RETURN:
    The coefficient for the given item's lambda in the cost constraint of the
    closed form of linear program
    '''
    term1 = total_time * num_periods * (num_periods-1) * holding_cost[item_index] / 2

    num_periods_vector = [i for i in range(num_periods, -1, -1)]
    num_periods_np = np.array(num_periods_vector)
    d_np = np.asarray(demand_schedule_init)
    holding_cost_np = np.array(holding_cost)
    initial_inventory_np = np.asarray(initial_inventory)

    term2 = unit_production_time[item_index] * \
            (num_periods * np.dot(holding_cost_np, initial_inventory_np) - \
            np.dot(np.dot(num_periods_np, d_np), holding_cost_np) -\
                   cost_tolerance)
    coefficient = term1 + term2
    return coefficient


def cost_model(num_items, num_periods, unit_production_time, total_time, \
               initial_inventory, demand_schedule, cost_tolerance, \
               changeover_cost, holding_cost, demand_schedule_init):
    '''
    Solves for the cost model. Find lambdas that satisfy the cost constraint and
    have inventory meet demand at each time period

    PARAMETERS:
    num_items := total number of items
    num_periods := total number of time periods
    unit_production_time := time needed to produce one unit for each item
    total_time := total time in one period
    initial_inventory := initial inventory for each item
    demand_schedule := a matrix of size (J, L) containing demand for each item
    cost_tolerance := total cost tolerance for the year
    changeover_cost := changeover cost for each item
    holding_cost := inventory cost for each item
    demand_schedule_init := demand schedule including the initial time period

    RETURN:
    None
    '''
    # initialize model
    model = Model('loop minimization')

    # add model variables
    Lambda = [model.add_var(var_type=INTEGER) for i in range(num_items)]

    # set model objective
    model.objective = minimize(xsum(Lambda[i] * unit_production_time[i] \
                                    for i in range(num_items)))

    # add constraints
    cost_coeff = [0] * num_items
    for i in range(1, num_items+1):
        for j in range(1, num_periods+1):
            # baseloop constraints
            coeff = [0] * num_items
            for k in range(num_items):
                coeff[k] = unit_production_time[k] * \
                           (initial_inventory[i-1] - \
                            demand_upto(demand_schedule, j, i-1))
            coeff[i-1] += j*total_time
            # add constraints for inventory to meet demand at each time period
            model += xsum(coeff[i] * Lambda[i] for i in range(num_items)) >= 0
            # add coeffs in for cost constraint
            kwargs = {'num_periods': num_periods, 'unit_production_time': \
                      unit_production_time, 'total_time': total_time, \
                      'initial_inventory':initial_inventory, 'cost_tolerance': \
                      cost_tolerance, 'holding_cost': holding_cost, \
                      'demand_schedule_init': demand_schedule_init, \
                      'item_index': i-1}
            cost_coeff[i-1] = get_cost_coeff(**kwargs)

    # cost constraint
    model += xsum(cost_coeff[i] * Lambda[i] for i in range(num_items)) <=\
             - num_periods * total_time * sum(changeover_cost)

    # constraint on positive looptime
    model += xsum(unit_production_time[i] * Lambda[i] for i in range(num_items)) >= 1

    # solve for model
    model.optimize()

    try:
        print('result of cost model (non-skipping): ')
        print([Lambda[i].x for i in range(num_items)])
        return [Lambda[i].x for i in range(num_items)]
    except:
        print("no solution for cost model")
        return -1
