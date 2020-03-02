# This program outputs reads in user input from a CSV file for a Baseloop
# minimization problem
# @author Will Thompson
# @author Rosa Zhou

import csv
import numpy as np

class BaseLoopInputData:

    def __init__(self, Input_filename):

            self.item_Directory = self.read_Input_filename(Input_filename)[0]
            self.entire_Demand_Schedule = self.read_Input_filename(Input_filename)[1]
            self.all_Production_Times = self.read_Input_filename(Input_filename)[2]
            self.inventory_Cost = self.read_Input_filename(Input_filename)[3]

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

    def update_demand_schedule(self, entire_Demand_Schedule, some_Item_Demand_Schedule):

        for i in range(len(entire_Demand_Schedule)):
            entire_Demand_Schedule[i].append(some_Item_Demand_Schedule[i])

        return entire_Demand_Schedule

    def get_item_production_time(self, machine_Cycle_Time, units_per_Machince_Cycle):

        item_Production_Time = (machine_Cycle_Time/units_per_Machince_Cycle)
        return item_Production_Time

    def read_Input_filename(self, some_Input_filename):

        all_Production_Times = []
        entire_Demand_Schedule = []
        changeover_Cost = []
        inventory_Cost = []
        item_Directory = {}
        line_index = 0
        inputData_csv = open(some_Input_filename, 'r', encoding='utf-8')

        for line in inputData_csv:
            item_Data = line.split(",")
            item_Demand_Horizon = item_Data[7].strip()
            num_time_periods = int(self.get_length_demand_schedule(item_Demand_Horizon))
            entire_Demand_Schedule = [[] for i in range(num_time_periods)]
            line_index+=1
            break

        for line in inputData_csv:

            item_Data = line.split(",")

            if line_index >= 1:

                item_Name = item_Data[0]
                item_Directory[line_index - 1] = item_Name

                item_Expected_Demand = float(item_Data[1])
                item_Stdev_Demand = float(item_Data[2])

                item_Demand_Schedule = self.get_item_demand_schedule(item_Expected_Demand, item_Stdev_Demand, num_time_periods)
                entire_Demand_Schedule = self.update_demand_schedule(entire_Demand_Schedule, item_Demand_Schedule)

                machine_Cycle_Time = float(item_Data[5])
                units_per_Machince_Cycle = float(item_Data[6])
                item_Production_Time = self.get_item_production_time(machine_Cycle_Time, units_per_Machince_Cycle)
                all_Production_Times.append(item_Production_Time)

                item_Inventory_Cost = float(item_Data[4])
                inventory_Cost.append(item_Inventory_Cost)

                line_index += 1

        return item_Directory, entire_Demand_Schedule, all_Production_Times,inventory_Cost
