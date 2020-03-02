
from BaseLoop_optimizer_Input_Reader import *

test()

Baseloop_Data = BaseLoopInputData("Input_Data.csv")

item_Directory = Baseloop_Data.item_Directory
entire_Demand_Schedule = Baseloop_Data.entire_Demand_Schedule
all_Production_Times = Baseloop_Data.all_Production_Times
inventory_Cost = Baseloop_Data.inventory_Cost
changeover_Cost = Baseloop_Data.changeover_Cost
initial_inventories = Baseloop_Data.initial_inventories


def read_list(some_list, name_of_List):
    print(" ")
    print("********************")
    print(name_of_List)
    print(" ")

    for item in some_list:
        print(item)

    print("********************")

def read_dictionary(some_dictionary, name_of_Dict):
    print(" ")
    print("********************")
    print(name_of_Dict)
    print(" ")

    for item in some_dictionary.keys():
        print("{} : {}".format(item, some_dictionary[item]))

    print("********************")

def read_Demand_Schedule(demand_Schedule, name_of_List):
    print(" ")
    print("********************")
    print(name_of_List)
    print(" ")

    for time_period in demand_Schedule:
        print("Time period: {}".format(demand_Schedule.index(time_period)))
        print(" ")
        for demand in time_period:
            print(demand)
        print(" ")

    print("********************")


def main():

    read_list(inventory_Cost, "All Inventory Costs:")
    read_list(all_Production_Times, "All Item Production Times:")
    read_list(changeover_Cost, "changeover_Cost:")
    read_list(initial_inventories, "initial_inventories:")
    read_dictionary(item_Directory, "Items:")
    read_Demand_Schedule(entire_Demand_Schedule, "Demand:")

if __name__ == "__main__":
    main()
