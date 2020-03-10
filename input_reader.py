# This program outputs reads in user input from a CSV file for a Baseloop
# minimization problem
# @author Will Thompson
# @author Rosa Zhou

import csv
import numpy as np

class BaseLoopInputData:

    def __init__(self, input_filename):
        '''
        This class takes in data from a csv file and saves all data into 9 lists

        Instance variables:
        self.item_directory :=  The data for each item data stored in a list
                                will be stored in lists, which are indexed by
                                item.

                                The keys in this dictionary are the indices and
                                the values are the names of the items.
        self.entire_demand_schedule := This object is a list of lists containing
                                       the demand for each item in each time period.
                                       The nth list in this object contains the
                                       demand for each item in the nth time
                                       period.
        self.all_production_times := This is a list containing the production time
                                     for each item. The nth entry in this list
                                     is the production time for the nth items
        self.inventory_cost := This is a list of all item inventory costs
        self.changeover_cost := This is a list of all item changeover costs
        self.initial_inventories := This is a list of all of the initial
                                    inventories for each item
        self.total_time := A fixed amount of time available to produce items
        self.cost_tolerance := A number that represents the maximum cost
                               production can incure
        self.trigger_points := This is a list of all item trigger points
        '''
        self.item_directory = self.read_input_filename(input_filename)[0]
        self.entire_demand_schedule = self.read_input_filename(input_filename)[1]
        self.all_production_times = self.read_input_filename(input_filename)[2]
        self.inventory_cost = self.read_input_filename(input_filename)[3]
        self.changeover_cost = self.read_input_filename(input_filename)[4]
        self.initial_inventories = self.read_input_filename(input_filename)[5]
        self.total_time = self.read_input_filename(input_filename)[6]
        self.cost_tolerance = self.read_input_filename(input_filename)[7]
        self.trigger_points = self.read_input_filename(input_filename)[8]


    def get_item_demand_schedule(self, expected_demand, stdev_demand, num_time_periods):
        '''
        This function estimates an item's demand schedule. With a specified demand
        horizon, we sample from a normal distribution given by the item's expected
        demand and standard deviation.

        PARAMETERS:
        expected_demand := The average demand for an item
        stdev_demand := standard deviation of demand
        num_time_periods := total number of time periods

        RETURN:
        A list containing the item's demand over the given number of time periods
        '''

        np.random.seed(0)
        item_demand_array = np.random.normal(expected_demand, stdev_demand,\
                                             num_time_periods)

        item_demand_list = item_demand_array.tolist()
        item_demand_list = [int(i) for i in item_demand_list]
        negative_samples = self.get_negative_samples(item_demand_list)

        for index in negative_samples:
            item_demand_list[index] = self.make_sample_positive(expected_demand, stdev_demand)

        return item_demand_list

    def get_negative_samples(self, demand_list):
        '''
        This function iterates through a sampled demand schedule and returns the
        indices of negative samples.

        PARAMETERS:
        demand_list := a list of an item's demand in each time period

        RETURN:
        A list containing the indices of samples that were negative
        '''

        indices_of_negative_samples = []

        new_demand_list = demand_list.copy()
        sign_of_entries_array = np.sign(new_demand_list)
        sign_of_entries_list = sign_of_entries_array.tolist()

        for i in range(len(sign_of_entries_list)):
            if sign_of_entries_list[i] == -1.0:
                indices_of_negative_samples.append(i)

        return indices_of_negative_samples

    def make_sample_positive(self, expected_demand, stdev_demand):
        '''
        This function keeps sampling from a normal distribution until it returns
        a sample that is positive. This new positive sample will replace the
        previous negative sample.

        PARAMETERS:
        expected_demand := The average demand for an item
        stdev_demand := standard deviation of demand

        RETURN:
        A positive sample from a normal distribution with the given mean and
        standard deviation
        '''

        sign = -1
        while sign == -1:
            new_demand_sample = int(np.random.normal(expected_demand, stdev_demand))

            if new_demand_sample > 0:
                sign = 1
        return new_demand_sample

    def get_length_demand_schedule(self, demand_horizon):
        '''
        This function converts a spreadsheet's description of the
        deamnd horizon, such as "Weekly" or "Monthly" into an integer value


        PARAMETERS:
        demand_horizon := a qualitative description of how many time periods the
                          loop will run for

        RETURN:
        An integer value for the number of time periods
        '''

        if demand_horizon == "Monthly":
            length_demand_schedule = 12

        elif demand_horizon == "Weekly":
            length_demand_schedule = 52

        else:
            length_demand_schedule = demand_horizon

        return length_demand_schedule

    def update_demand_schedule(self, entire_demand_schedule, some_item_demand_schedule):
        '''
        This function is designed to insert an item's demand schedule into the
        entire_demand_schedule object, which contains all demands index by time
        period.

        PARAMETERS:
        entire_demand_schedule := A list of lists containing all item demand in
                                  each time period

        some_item_demand_schedule := A list of an item's demand for each time period

        RETURN:
        An updated version of entire_demand_schedule containing a new list
        of item demand
        '''
        for i in range(len(entire_demand_schedule)):
            entire_demand_schedule[i].append(some_item_demand_schedule[i])

        return entire_demand_schedule

    def get_item_production_time(self, machine_cycle_time, units_per_machine_cycle):
        '''
        This function calculates item production time by dividing total machine
        cycle time by the number of units produced in that time

        PARAMETERS:
        machine_cycle_time := The total time for a machine to run one cycle

        units_per_machine_cycle := The number of items produced in one cycle

        RETURN:
        item production time
        '''

        item_production_time = (machine_cycle_time/units_per_machine_cycle)
        return item_production_time

    def read_input_filename(self, some_input_filename):
        ''''
        This function reads in the data from a csv file

        PARAMETERS:
        some_input_filename := The csv spreadsheet containing the appropriate data

        RETURN:
        Returns 7 lists of item data, including the complete demand schedule,
        as well as total_time and cost_tolerance.
        '''
        total_time = 0
        cost_tolerance = 0
        item_directory = {}
        entire_demand_schedule = []
        changeover_cost = []
        inventory_cost = []
        all_production_times = []
        initial_inventories = []
        trigger_points = []

        line_index = 0
        inputdata_csv = open(some_input_filename, 'r', encoding='utf-8')

        for line in inputdata_csv:
            item_data = line.split(",")

            item_demand_horizon = item_data[9].strip()
            num_time_periods = int(self.get_length_demand_schedule(item_demand_horizon))
            entire_demand_schedule = [[] for i in range(num_time_periods)]

            total_time = float(item_data[11].strip())
            cost_tolerance = float(item_data[13].strip())

            line_index+=1
            break

        for line in inputdata_csv:

            item_data = line.split(",")

            if line_index >= 1:

                item_Name = item_data[0]
                item_directory[line_index - 1] = item_Name

                item_expected_demand = float(item_data[1])
                item_stdev_demand = float(item_data[2])
                item_demand_schedule = self.get_item_demand_schedule(item_expected_demand, item_stdev_demand, num_time_periods)
                entire_demand_schedule = self.update_demand_schedule(entire_demand_schedule, item_demand_schedule)

                item_changeover_cost = float(item_data[3])
                changeover_cost.append(item_changeover_cost)
                item_Inventory_cost = float(item_data[4])
                inventory_cost.append(item_Inventory_cost)

                machine_cycle_time = float(item_data[5])
                units_per_Machince_cycle = float(item_data[6])
                item_production_time = self.get_item_production_time(machine_cycle_time, units_per_Machince_cycle)
                all_production_times.append(item_production_time)

                item_initial_inventory = float(item_data[7])
                initial_inventories.append(item_initial_inventory)

                item_trigger_point = float(item_data[8])
                trigger_points.append(item_trigger_point)

                line_index += 1

        return item_directory, entire_demand_schedule, all_production_times, inventory_cost, changeover_cost, initial_inventories, total_time, cost_tolerance, trigger_points
