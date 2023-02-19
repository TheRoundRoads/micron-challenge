    
# class for each building
class Building:
    def __init__(self):
        self.stations = []
        self.lots = [0] * 7
    
    # add station to building
    def add_station(self, station):
        self.stations.append(station)
        
    def add_lot(self, lot):
        self.lots[lot] += 1
    
# class for workstations
class Workstation:
    def __init__(self, name, stages):
        self.finish_time = 0
        self.process = -1
        self.name = name
        self.stages = stages  # e.g. {3: 10, 1: 5} for workstation A (Note: Descending order of stages - greedy)
        
    # prints status of workstation to show if it is free
    def status(self):
        if self.process == None:
            print(f"Station {self.name} is currently free.")
        else:
            print(f"Station {self.name} is doing process {self.process}, to finish at {self.finish_time}.")
        
        return        
    
    # return new process of lot if finished, else return -1
    def finished(self, time):
        if time >= self.finish_time:
            return self.process + 1  # lot can go to next process
        else:
            return -1
    
    # work on new lot, only runs when finished with previous lot
    def execute(self, time, lot):
        self.process = lot
        self.finish_time = time + self.stages[lot]
        
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
    
# initialise buildings, stations and truck
buildingX = Building()
buildingY = Building()

buildingX.add_station(Workstation("A", {3: 10, 1: 5}))
buildingX.add_station(Workstation("B", {6: 10, 2: 15}))
buildingX.add_station(Workstation("C", {5: 10, 2: 15}))
buildingY.add_station(Workstation("F", {6: 10, 4: 10}))
buildingY.add_station(Workstation("D", {4: 15, 1: 5}))
buildingY.add_station(Workstation("E", {5: 15, 3: 5}))

truck = Truck()
buildingX.lots[1] = 10000  # set it to virtually infinity

TOTAL_TIME = 10080  # total no. of minutes in a week
# TOTAL_TIME = 60
TIME = 0
OUTPUT = 0

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
            for lot in reversed(range(1, 7)):
                if len(toLoad) == 5:
                    break
                if lot == 2:  # don't want to load lot of process 2, because Y doesn't have stns
                    continue                
                
                # determine number of lots that can be added
                canAdd = min(buildingX.lots[lot], 5 - len(toLoad))
                for _ in range(canAdd):
                    toLoad.append(lot)  
                
            # unload lots
            for lot in truck.lots:
                print(f"Unload lot {lot} into building {dst}")
                buildingX.add_lot(lot)
            
            # load lots
            truck.unload()
            for lot in toLoad:
                print(f"Load lot {lot} onto truck.")
                truck.add_lot(lot)
            
            truck.update("Y")  # update to new destination
                            
        else:
            # load then unload to prevent same lots being loaded
            toLoad = []
            
            # load up to 5 lots
            for lot in reversed(range(1, 7)):
                if len(toLoad) == 5:
                    break
                if lot == 4:  # don't want to load lot of process 4, because X doesn't have stns
                    continue                
                
                # determine number of lots that can be added
                canAdd = min(buildingY.lots[lot], 5 - len(toLoad))
                for _ in range(canAdd):
                    toLoad.append(lot)  
                
            # unload lots
            for lot in truck.lots:
                print(f"Unload lot {lot} into building {dst}")
                buildingY.add_lot(lot)
            
            # load lots
            truck.unload()
            for lot in toLoad:
                print(f"Load lot {lot} onto truck.")
                truck.add_lot(lot)

            truck.update("X")  # update to new destination
    else:
        print(f"Truck will reach at {truck.dst} at time {truck.arrival_time}.")
        
    print()
    
    ## building X
    print("Building X:")
    for station in buildingX.stations:
        # check if station is free
        station.status()
        newLot = station.finished(TIME)
        if newLot != -1:  # add new lot to station
            if newLot == 7:  # add to output since lot is completed
                OUTPUT += 1
                print(f"Lot completed! Current Output: {OUTPUT}")
            else:
                buildingX.lots[newLot] += 1  # add lot to count
            for stage in station.stages:
                if buildingX.lots[stage] > 0:  # check if particular lot at that stage exists
                    print(f"Station {station.name} will now work on lot {stage}")
                    station.execute(TIME, stage)  # work on lot
                    buildingX.lots[stage] -= 1  # remove lot from count
                    break
    print()
    
    ## building Y
    print("Building Y:")
    for station in buildingY.stations:
        # check if station is free
        station.status()
        newLot = station.finished(TIME)
        if newLot != -1:  # add new lot to station
            if newLot == 7:  # add to output since lot is completed
                OUTPUT += 1
                print(f"Lot completed! Current Output: {OUTPUT}")
            else:
                buildingY.lots[newLot] += 1  # add lot to count
            for stage in station.stages:
                if buildingY.lots[stage] > 0:  # check if particular lot at that stage exists
                    print(f"Station {station.name} will now work on lot {stage}")
                    station.execute(TIME, stage)  # work on lot
                    buildingY.lots[stage] -= 1  # remove lot from count
                    break
    print()
    print(30*"-")
    TIME += 5
    
print("Final output:", OUTPUT)
print("Building X counts:")
for i in range(1, 7):
    print(i, buildingX.lots[i])
    
print("Building Y counts:")
for i in range(1, 7):
    print(i, buildingY.lots[i])