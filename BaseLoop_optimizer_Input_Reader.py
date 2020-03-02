# This program outputs reads in user input from a CSV file for a Baseloop
# minimization problem
# @author Will Thompson
# @author Rosa Zhou

import csv
import numpy as np

class BaseLoopinputdata:

    def __init__(self, input_filename):

            self.item_directory = self.read_input_filename(input_filename)[0]
            self.entire_demand_schedule = self.read_input_filename(input_filename)[1]
            self.all_production_times = self.read_input_filename(input_filename)[2]
            self.inventory_cost = self.read_input_filename(input_filename)[3]
            self.changeover_Cost = self.read_input_filename(input_filename)[4]
            self.initial_inventories = self.read_input_filename(input_filename)[5]
            self.total_time = self.read_input_filename(input_filename)[6]
            self.cost_tolerance = self.read_input_filename(input_filename)[7]


    def get_item_demand_schedule(self, expected_demand, stdev_demand, num_time_periods):

        item_demand_array = np.random.normal(expected_demand, stdev_demand, num_time_periods)
        item_demand_list = item_demand_array.tolist()

        return item_demand_list


    def get_length_demand_schedule(self, demand_horizon):

        if demand_horizon == "Monthly":
            length_demand_schedule = 12

        elif demand_horizon == "Weekly":
            length_demand_schedule = 52

        else:
            length_demand_schedule = demand_horizon

        return length_demand_schedule

    def update_demand_schedule(self, entire_demand_schedule, some_item_demand_schedule):

        for i in range(len(entire_demand_schedule)):
            entire_demand_schedule[i].append(some_Item_demand_schedule[i])

        return entire_demand_schedule

    def get_item_production_time(self, machine_cycle_time, units_per_machine_cycle):

        item_production_time = (machine_cycle_time/units_per_machine_cycle)
        return item_production_time

    def read_input_filename(self, some_input_filename):

        total_time = 0
        cost_tolerance = 0
        item_directory = {}
        entire_demand_schedule = []
        changeover_cost = []
        inventory_cost = []
        all_production_times = []
        initial_inventories = []
        line_index = 0
        inputdata_csv = open(some_input_filename, 'r', encoding='utf-8')

        for line in inputdata_csv:
            item_data = line.split(",")

            item_demand_Horizon = item_data[7].strip()
            num_time_periods = int(self.get_length_demand_schedule(item_demand_Horizon))
            entire_demand_schedule = [[] for i in range(num_time_periods)]

            total_time = item_data[9].strip()
            cost_tolerance = item_data[10].strip()

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

                line_index += 1

        return item_directory, entire_demand_schedule, all_production_times, inventory_cost, changeover_cost, initial_inventories, total_time, cost_tolerance
