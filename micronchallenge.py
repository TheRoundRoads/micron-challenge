import csv
from pathlib import Path

p = Path(__file__).with_name('ans.csv')


# create class for lot object
class Lot:
    def __init__(self, id, process=1):
        self.id = id
        self.process = process
    
    def next_process(self):
        self.process += 1
    
# class for each building
class Building:
    def __init__(self):
        self.stations = []
        
        # 2d list of lots, grouped based on process
        self.lots = []
        for _ in range(7):
            self.lots.append([])
    
    # add station to building
    def add_station(self, station):
        self.stations.append(station)
    
    # add lot to correct list
    def add_lot(self, lot):
        self.lots[lot.process].append(lot)
    
# class for workstations
class Workstation:
    def __init__(self, name, stages):
        self.finish_time = 0
        self.lot = None
        self.name = name
        self.stages = stages  # e.g. {3: 10, 1: 5} for workstation A (Note: Descending order of stages - greedy)
        
    # prints status of workstation to show if it is free
    def status(self):
        if self.lot == None:
            print(f"Station {self.name} is currently free.")
        else:
            print(f"Station {self.name} is working on lot {self.lot.id} of process {self.lot.process}, to finish at {self.finish_time}.")
        
        return        
    
    # update station based on time
    def update(self, time):
        if time >= self.finish_time:
            lot = self.lot
            if lot != None:
                lot.next_process()
            self.lot = None
            return lot, True
        return None, False
    
    # work on new lot, only runs when finished with previous lot
    def execute(self, time, lot):
        self.lot = lot
        self.finish_time = time + self.stages[lot.process]
        
        return
        
# truck stores
class Truck:
    def __init__(self):
        self.lots = []
        self.dst = "X"
        self.arrival_time = 0
    
    def add_lot(self, lot):
        self.lots.append(lot)
        
    def reached(self, time):
        return time >= self.arrival_time, self.dst
    
    def update(self, new_dst):
        self.dst = new_dst
        self.arrival_time += 25
        
    def unload(self):
        self.lots = []

def processing(time, buildingX, buildingY, truck):
    X = []
    Y = []
    truck_ = []
    for station in buildingX.stations:
        if station.lot == None:
            X.append("")
        else:
            X.append(station.lot.id)
    
    for station in reversed(buildingY.stations):
        if station.lot == None:
            Y.append("")
        else:
            Y.append(station.lot.id)
            
    for i in range(5):
        if i >= len(truck.lots):
            truck_.append("")
        else:
            truck_.append(truck.lots[i].id)
    
    truck_.append(truck.dst)
    
    return [time] + X + Y + truck_

# initialise buildings, stations and truck
buildingX = Building()
buildingY = Building()

buildingX.add_station(Workstation("A", {3: 10, 1: 5}))
buildingX.add_station(Workstation("B", {6: 10, 2: 15}))
buildingX.add_station(Workstation("C", {5: 10, 2: 15}))
buildingY.add_station(Workstation("F", {6: 10, 4: 10}))
buildingY.add_station(Workstation("E", {5: 15, 3: 5}))
buildingY.add_station(Workstation("D", {4: 15, 1: 5}))


truck = Truck()
# add 10000 lots to building X by default
for i in range(1, 10001):
    buildingX.add_lot(Lot(i))

TOTAL_TIME = 10080  # total no. of minutes in a week
# TOTAL_TIME = 100
TIME = 0
OUTPUT = 0
completed = []
HEADERS = ["Time", "Workstn A", "Workstn B", "Workstn C", "Workstn D", "Workstn E", "Workstn F", "Truck slot 1", "Truck slot 2", "Truck slot 3", "Truck slot 4", "Truck slot 5", "Destination"]

with open(p, "w", encoding="UTF-8", newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(HEADERS)
    while TIME <= TOTAL_TIME:
        print(30*"-")
        print(f"Current time: {TIME}")
        ## load / unload truck
        print("Truck:")
        reached, dst = truck.reached(TIME)
        if reached:
            # load then unload to prevent same lots being loaded
            if dst == "X":
                toLoad = []
                
                # load up to 5 lots
                for process in reversed(range(1, 7)):
                    if len(toLoad) == 5:
                        break
                    if process == 2:  # don't want to load lot of process 2, because Y doesn't have stns
                        continue                
                    
                    # determine number of lots that can be added
                    canAdd = min(len(buildingX.lots[process]), 5 - len(toLoad))
                    for i in range(canAdd):
                        toLoad.append(buildingX.lots[process].pop(0))
                        
                    
                # unload lots
                for lot in truck.lots:
                    print(f"Unload lot {lot.id} into building {dst}")
                    buildingX.add_lot(lot)
                
                # load lots
                truck.unload()
                for lot in toLoad:
                    print(f"Load lot {lot.id} onto truck.")
                    truck.add_lot(lot)
                
                truck.update("Y")  # update to new destination
                                
            else:
                # load then unload to prevent same lots being loaded
                toLoad = []
                
                # load up to 5 lots
                for process in reversed(range(1, 7)):
                    if len(toLoad) == 5:
                        break
                    if process == 4:  # don't want to load lot of process 4, because X doesn't have stns
                        continue                
                    
                    # determine number of lots that can be added
                    canAdd = min(len(buildingY.lots[process]), 5 - len(toLoad))
                    for _ in range(canAdd):
                        toLoad.append(buildingY.lots[process].pop(0))
                    
                # unload lots
                for lot in truck.lots:
                    print(f"Unload lot {lot.id} into building {dst}")
                    buildingY.add_lot(lot)
                
                # load lots
                truck.unload()
                for lot in toLoad:
                    print(f"Load lot {lot.id} onto truck.")
                    truck.add_lot(lot)

                truck.update("X")  # update to new destination
        else:
            print(f"Truck will reach Building {truck.dst} at time {truck.arrival_time}.")
            
        print()
        
        ## building X
        print("Building X:")
        for station in buildingX.stations:
            # check if station is free
            station.status()
            newLot, isFree = station.update(TIME)
            if isFree:  # add new lot to station
                if newLot != None:
                    if newLot.process == 7:  # add to output since lot is completed
                        completed.append(newLot.id)
                        OUTPUT += 1
                        print(f"Lot {newLot.id} completed! Current Output: {OUTPUT}")
                    else:
                        buildingX.lots[newLot.process].append(newLot)  # add lot to count
        for station in buildingX.stations:
            if TIME >= station.finish_time:
                for stage in station.stages:
                    if len(buildingX.lots[stage]) > 0:  # check if particular lot at that stage exists
                        toAdd = buildingX.lots[stage].pop(0)
                        print(f"Station {station.name} will now work on lot {toAdd.id} on process {stage}")
                        station.execute(TIME, toAdd)  # work on lot
                        break
        print()
        
        ## building Y
        print("Building Y:")
        for station in buildingY.stations:
            # check if station is free
            station.status()
            newLot, isFree = station.update(TIME)
            if isFree:  # add new lot to station
                if newLot != None:
                    if newLot.process == 7:  # add to output since lot is completed
                        completed.append(newLot.id)
                        OUTPUT += 1
                        print(f"Lot {newLot.id} completed! Current Output: {OUTPUT}")
                    else:
                        buildingY.lots[newLot.process].append(newLot)  # add lot to count
        for station in buildingY.stations:
            if TIME >= station.finish_time:
                for stage in station.stages:
                    if len(buildingY.lots[stage]) > 0:  # check if particular lot at that stage exists
                        toAdd = buildingY.lots[stage].pop(0)
                        print(f"Station {station.name} will now work on lot {toAdd.id} on process {stage}")
                        station.execute(TIME, toAdd)  # work on lot
                        break
        print()
        print(30*"-")
        writer.writerow(processing(TIME, buildingX, buildingY, truck))
        TIME += 5
    
print("Final output:", OUTPUT)
# print("Completed:", *completed)
print("Building X counts:")
for i in range(1, 7):
    print(i, len(buildingX.lots[i]))
    
print("Building Y counts:")
for i in range(1, 7):
    print(i, len(buildingY.lots[i]))