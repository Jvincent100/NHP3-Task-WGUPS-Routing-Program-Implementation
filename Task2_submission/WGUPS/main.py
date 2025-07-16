# Joshua Vincent
# Student ID: 011253318
# C950

import datetime
import random

import csv
from address import Address
from hash_table import HashTableWithChaining as HashTable
from package import Package
from status import Status
from truck import Truck

#
# Global state
#
ADDRESSES = []
PACKAGES = HashTable(10)
DISTANCES = {}


# Convert time string to minutes
# "10:30 AM" -> 10:30 , "10:30 PM"-> 22:30
def convert_time(time_str) -> datetime.timedelta:
    if time_str == 'EOD':
        return datetime.timedelta(hours=22, minutes=0)
    time = time_str.split(':')
    hour = int(time[0])
    minute = int(time[1].split(' ')[0])
    if len(time[1]) > 2 and time[1].split(' ')[1] == 'PM':
        hour += 12
    return datetime.timedelta(hours=hour, minutes=minute)


print('Loading addresses...')
with open('csv/addresses.csv', 'r') as address_file:
    address_data = csv.reader(address_file)
    address_data = list(address_data)

# Create a list of Address objects
for address in address_data:
    addr = Address(int(address[0]), address[1], address[2])
    ADDRESSES.insert(addr.ID, addr)

print('Loading packages...')
with open('csv/packages.csv', 'r') as package_file:
    package_data = csv.reader(package_file)
    package_data = list(package_data)

# Create a list of Package objects and extend the Address with the address data
for package in package_data:
    # 1,195 W Oakland Ave,Salt Lake City,UT,84115,10:30 AM,21,
    parcel = Package(int(package[0]), package[6], package[7])

    for address in ADDRESSES:
        if address.street == package[1]:
            address.street = package[1]
            address.city = package[2]
            address.state = package[3]
            address.zip = package[4]
            parcel.address = address
            break

    parcel.deadline = convert_time(package[5])

    if parcel.deadline <= datetime.timedelta(hours=10, minutes=30):
        parcel.is_priority = True

    if parcel.ID == 9:
        parcel.address = ADDRESSES[19]

    # Insert package into hash table with package ID as key and package data as value
    PACKAGES.insert(parcel.ID, parcel)

print('Populating distance dictionary...')
with open('csv/distances.csv', 'r') as distance_file:
    distance_data = csv.reader(distance_file)
    distance_data = list(distance_data)

for i in range(len(distance_data)):
    for j in range(len(distance_data[i])):
        if distance_data[i][j]:
            DISTANCES[i, j] = float(distance_data[i][j])
        else:
            DISTANCES[j, i] = 0.0


#
# Helper functions
#
def get_address_by_street(address_list, street: str) -> Address or None:
    for addr in address_list:
        if addr.street == street:
            return addr
    return None


# find all packages at a given address to avoid route loops
def get_packages_by_address(package_list, address: int) -> list:
    packages = []
    for package in package_list:
        if package.address.ID == address:
            packages.append(package)
    return packages


# get_distance returns the distance between two addresses
def get_distance(i: int, j: int) -> float:
    i = int(i)
    j = int(j)
    if i == j:  # same address, no distance
        return 0.0

    if (i, j) in DISTANCES:
        return DISTANCES[i, j]
    else:
        return DISTANCES[j, i]


# truck_assigner assigns packages to a truck based on restrictions given in the notes column of the packages.csv file
def truck_assigner(package) -> int | None:
    id: int = int(package.ID)

    # handle packages with restrictions
    # must be on truck 2
    if id in [3, 18, 36, 38]:
        return 2

    # delayed packages
    if id in [6, 25, 28, 32]:
        return 1

    # packages that must be delivered together
    if id in [13, 14, 15, 16, 19, 20]:
        return 2

    # packages that must be on truck 3
    if id == 9:
        return 3

    return None


# distribute packages to trucks based on priority, standard and truck capacity
def sort_packages(packages, trucks):
    standard_packages = []
    for package in packages:
        if package.is_priority:
            choice = truck_assigner(package)
            if choice is None:
                choice = random.randint(1, 2)
            if choice == 1:
                trucks[0].priority_packages.append(package)
                package.truck = trucks[0].ID
            else:
                trucks[1].priority_packages.append(package)
                package.truck = trucks[1].ID
        else:
            choice = truck_assigner(package)
            if choice is None:
                standard_packages.append(package)  # add to standard packages list
            else:
                match choice:
                    case 1:
                        trucks[0].packages.append(package)
                        package.truck = trucks[0].ID
                    case 2:
                        trucks[1].packages.append(package)
                        package.truck = trucks[1].ID
                    case 3:
                        trucks[2].packages.append(package)
                        package.truck = trucks[2].ID
    # fill trucks with standard packages
    for package in standard_packages:
        if trucks[0].package_count() < 14:
            trucks[0].packages.append(package)
            package.truck = trucks[0].ID
        elif trucks[1].package_count() < 14:
            trucks[1].packages.append(package)
            package.truck = trucks[1].ID
        else:
            trucks[2].packages.append(package)
            package.truck = trucks[2].ID


# get_status_at_time returns the status of a package at a given time
def get_status_at_time(package, time):
    if package.ID == 9:
        delay_time = datetime.timedelta(hours=10, minutes=20)
        if time < delay_time:
            return Status.AT_HUB
        elif delay_time < time < package.delivery_time:
            return Status.OUT_FOR_DELIVERY
        elif time >= package.delivery_time:
            return Status.DELIVERED

    if package.leave_time is None:
        return Status.AT_HUB
    elif time < package.leave_time:
        return Status.AT_HUB
    elif time < package.delivery_time:
        return Status.OUT_FOR_DELIVERY
    elif time >= package.delivery_time:
        return str(Status.DELIVERED) + f' at {package.delivery_time}'


# Helper function to print out truck packages and routes for debugging
def print_out_packages(trucks):
    print()
    # print truck packages
    for truck in trucks:
        pri = []
        std = []
        for package in truck.packages:
            std.append(package.ID)
        for package in truck.priority_packages:
            pri.append(package.ID)
        print(f'Truck {truck.ID} packages: {std}')
        print(f'Truck {truck.ID} Route: {truck.route}')
        print()
        pri.clear()
        std.clear()


# Nearest neighbor algorithm
# O(N^2) time complexity
# Consume a list of packages and return a route of addresses
def nearest_neighbor(start, packages_list):
    packages = packages_list.copy()
    route = [start]
    current = start
    while len(packages) > 0:
        nearest = None
        for package in packages:
            if nearest is None:
                nearest = package
            if get_distance(current, package.address.ID) < get_distance(current, nearest.address.ID):
                nearest = package
        route.append(nearest.address.ID)
        current = nearest.address.ID
        packages.remove(nearest)
    return route


# deliver_packages iterates through the truck's route and filters out packages that are to be delivered at each address
# also calculates the total distance traveled by the truck and the time each package is delivered as the truck travels
# O(N^2) time complexity, where N is the number of packages at any given address
def deliver_packages(truck) -> list[Package]:
    current = truck.route[0]  # start at the first address in the route
    delivered = []  # list of packages that have been delivered for reference later
    for i in range(1, len(truck.route)):
        next_local = truck.route[i]

        distance = get_distance(current, next_local)
        truck.total_distance += distance

        # get any packages on the truck at the current address and deliver them together
        curr_packages = get_packages_by_address(truck.packages, next_local)
        for package in curr_packages:
            # convert distance to time in minutes and add to leave time
            delivery_time = truck.leave_time + datetime.timedelta(minutes=truck.total_distance / 18 * 60)

            package.delivery_time = delivery_time  # set delivery time for package
            delivered.append(package)

        # filter out delivered packages to avoid double delivery
        truck.packages = [package for package in truck.packages if package not in curr_packages]
        current = next_local

    return delivered


#
# Main control flow
#


def run_simulation() -> list[Truck]:
    # create trucks
    truck1 = Truck(1, ADDRESSES[0])
    truck2 = Truck(2, ADDRESSES[0])
    truck3 = Truck(3, ADDRESSES[0])

    trucks = [truck1, truck2, truck3]

    # load priority packages
    packages = [PACKAGES.search(i) for i in range(1, 41)]

    # sort packages to priority and standard lists
    sort_packages(packages, trucks)

    # Nearest neighbor optimization
    for truck in trucks:
        # starting at hub, find nearest neighbor path for priority packages
        temp_list = nearest_neighbor(0, truck.priority_packages)

        # add the optimized route to the truck's route
        truck.route.extend(temp_list)

        # remove all but the last element
        temp_list = temp_list[-1:]

        # starting at last element of temp list, find nearest neighbor path for standard packages
        temp_list = nearest_neighbor(temp_list[0], truck.packages)
        temp_list = temp_list[1:]

        truck.route.extend(temp_list)
        truck.route.append(0)

        truck.packages.extend(truck.priority_packages)
        truck.priority_packages.clear()

    # iterate through the route and calculate the total distance
    trucks[0].leave_time = datetime.timedelta(hours=8, minutes=0)
    trucks[0].set_package_leave_times()
    trucks[0].delivered = deliver_packages(trucks[0])

    trucks[1].leave_time = datetime.timedelta(hours=9, minutes=5)
    trucks[1].set_package_leave_times()
    trucks[1].delivered = deliver_packages(trucks[1])

    truck3_leave_time = max(
        datetime.timedelta(hours=10, minutes=20),
        truck1.leave_time + datetime.timedelta(minutes=truck1.total_distance / 18))
    trucks[2].leave_time = truck3_leave_time
    trucks[2].set_package_leave_times()
    trucks[2].delivered = deliver_packages(trucks[2])

    # print_out_packages(trucks)
    return trucks


def intro():
    print('<- Press Ctrl+C to quit at any time ->')
    print("""
            _____________________________________________
           /  __          _______ _    _ _____   _____   \\
           |  \ \        / / ____| |  | |  __ \ / ____|  |\\\\\\\\\\\\
           |   \ \  /\  / / |  __| |  | | |__) | (___    |------
           |    \ \/  \/ /| | |_ | |  | |  ___/ \___ \\   |\\\\\\\\\\\\\\\\
           |     \  /\  / | |__| | |__| | |     ____) |  |--------
           |      \/  \/   \_____|\____/|_|    |_____/   |\\\\\\\\\\\\\\\\\\\\
            \\___________________________________________/
            Welcome to the WGUPS package tracking system!
            """)
    print('Starting Service...')


def user_interface(trucks: list[Truck]):
    menu = """
            Please select an option:
            1. Lookup package at exact time
            2. Lookup all packages
            3. Get status of all packages at a specific time
            4. Exit
            
            """

    while True:
        user_input = input(menu + '\nEnter choice: ')

        match user_input:
            case '1':
                package_id = input('\nEnter package ID: ')
                package: Package | None = PACKAGES.search(int(package_id))
                if package is None:
                    print('Package not found or does not exist.')
                    input('Press Enter to continue...')
                    break
                search_time = input('Enter time to search for package: (HH:MM) ')
                search_time = convert_time(search_time)
                print(package.package_print_out(search_time) + ' -- ' + str(get_status_at_time(package, search_time)))
                input('Press Enter to continue...')
            case '2':
                package_list = [PACKAGES.search(i) for i in range(1, 41)]
                for package in package_list:
                    print(package.package_print_out(datetime.timedelta(hours=22, minutes=0)))
                input('Press Enter to continue...')
            case '3':
                search_time = input('\nEnter time to view status of all packages: (HH:MM) ')
                search_time = convert_time(search_time)
                package_list = [PACKAGES.search(i) for i in range(1, 41)]
                for package in package_list:
                    status = get_status_at_time(package, search_time)
                    print(package.package_print_out(search_time) + ' -- ' + str(status))
                input('Press Enter to continue...')
            case '4':
                print('Exiting...')
                break
            case _:
                print('\nInvalid input. Please select and option by its #.')


def main():
    intro()  # Display intro message
    # Run simulation until total distance is calculated < 140 miles
    while True:
        print('Running simulation...')
        trucks = run_simulation()
        distance = trucks[0].total_distance + trucks[1].total_distance + trucks[2].total_distance
        if distance < 140:
            print('Simulation complete.')
            print(f'Total distance traveled: {distance} miles')
            break
        print('Total distance exceeded 140 miles.')
        print('Rerunning simulation...')

    user_interface(trucks)  # User Input Loop
    exit()  # Graceful exit


if __name__ == '__main__':
    main()