import numpy as np
from mip import Model, xsum, maximize, minimize, BINARY, INTEGER


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


def get_cost_coeff(index, total_time, num_periods, h, D_init, unit_production_time, initial_inventory, Tau):
    term1 = total_time * num_periods * (num_periods-1) * h[index] / 2
    num_periods_vector = [i for i in range(num_periods, -1, -1)]
    num_periods_np = np.array(num_periods_vector)
    D_np = np.asarray(D_init)
    h_np = np.array(h)
    initial_inventory_np = np.asarray(initial_inventory)
    term2 = unit_production_time[index] * (num_periods * np.dot(h_np, initial_inventory_np) - \
                        np.dot(np.dot(num_periods_np, D_np), h_np) - Tau)
    return term1 + term2


def cost_model(num_items, num_periods, unit_production_time, total_time, \
               initial_inventory, demand_schedule, Tau, a, h, D_init):
    model = Model('loop minimization')
    Lambda = [model.add_var(var_type=INTEGER) for i in range(num_items)]
    model.objective = minimize(xsum(Lambda[i] * unit_production_time[i] for i in range(num_items)))
    cost_coeff = [0] * num_items

    # add constraints
    for i in range(1, num_items+1):
        for j in range(1, num_periods+1):
            # baseloop constraints
            coeff = [0] * num_items
            for k in range(num_items):
                coeff[k] = unit_production_time[k]*(initial_inventory[i-1]-demand_upto(demand_schedule, j, i-1))
            coeff[i-1] += j*total_time
            model += xsum(coeff[i] * Lambda[i] for i in range(num_items)) >= 0
            # add coeffs in for cost constraint
            kwargs = {'num_periods': num_periods, 'unit_production_time': \
                      unit_production_time, 'total_time': total_time, \
                      'initial_inventory':initial_inventory, 'Tau': Tau,\
                      'h': h, 'D_init': D_init, 'index': i-1}
            cost_coeff[i-1] = get_cost_coeff(**kwargs)

    # cost constraint
    print('cost coeff: ', cost_coeff)
    model += xsum(cost_coeff[i] * Lambda[i] for i in range(num_items)) <=\
             - num_periods * total_time * sum(a)

    # positive looptime
    model += xsum(unit_production_time[i] * Lambda[i] for i in range(num_items)) >= 1

    model.optimize()

    print('result of cost model (non-skipping): ')
    print([Lambda[i].x for i in range(num_items)])
    return [Lambda[i].x for i in range(num_items)]


def main():
    '''
    Pass input to model and get results
    '''
    num_items = 3 # total number of items
    num_periods = 11 # total number of time periods
    unit_production_time = [3, 4, 5] # vector of item production time per unit
    total_time = 1400 # total time
    initial_inventory = [100, 150, 50] # initial inventory

    # demand
    demand_schedule = [[140, 100, 120], [140, 110, 110], [140, 90, 100], \
                       [120, 110, 110], [130, 110, 90], [120, 110, 90], \
                       [140, 100, 80], [150, 100, 90], [140, 80, 120], \
                       [140, 90, 110], [130, 110, 100]]

    Tau = 10000 # cost tolerance
    a = [10, 10, 20] # changeover cost
    h = [1, 2, 2] # inventory cost

    # demand with a dummy initial demand
    D_init = [[0, 0, 0], [140, 100, 120], [140, 110, 110], [140, 90, 100], [120, 110, 110], \
              [130, 110, 90], [120, 110, 90], [140, 100, 80], [150, 100, 90], \
              [140, 80, 120], [140, 90, 110], [130, 110, 100]]

    kwargs = {'num_items': num_items, 'num_periods': num_periods, \
              'unit_production_time': unit_production_time, \
              'total_time': total_time, 'initial_inventory': initial_inventory,\
              'demand_schedule': demand_schedule, 'Tau': Tau,\
              'a': a, 'h': h, 'D_init': D_init}
    cost_model(**kwargs)

if __name__=='__main__':
    main()
