
from BaseLoop_optimizer_Input_Reader import *

Baseloop_Data = BaseLoopInputData("Input_Data.csv")

item_Directory = Baseloop_Data.item_Directory
entire_Demand_Schedule = Baseloop_Data.entire_Demand_Schedule
all_Production_Times = Baseloop_Data.all_Production_Times
inventory_Cost = Baseloop_Data.inventory_Cost

def read_list(some_list):
    print(" ")
    print("********************")
    print("Items in {}: ".format(some_list))
    print(" ")

    for item in some_list:
        print(item)

    print("********************")

def read_dictionary(some_dictionary):
    print(" ")
    print("********************")
    print("Stuff in {}: ".format(some_dictionary))
    print(" ")

    for item in some_dictionary.keys():
        print(item + ":" + some_dictionary[item])

    print("********************")


def main():

    read_list(inventory_Cost)
    read_list(all_Production_Times)
    read_dictionary(item_Directory)

if __name__ == "__main__":
    main()
