import datetime

from address import Address
from status import Status


class Package:
    def __init__(self, ID, weight, note, is_priority=False) -> None:
        self.ID = ID
        self.deadline: int or str = None
        self.weight = weight
        self.note = note
        self.is_priority = is_priority

        self.address: Address or None = None
        self.leave_time = None  # added when truck leaves hub
        self.truck = None  # added when truck leaves hub
        self.delivery_time = None  # added when route is calculated

    def __str__(self) -> str:
        return f'Package ID: {self.ID} - Weight: {self.weight} lbs - Deadline: {self.deadline}'

    def get_address(self) -> str:
        return self.address.__str__()

    def handle_deadline(self):
        if self.deadline > datetime.timedelta(hours=10, minutes=30):
            return 'EOD'
        else:
            return self.deadline

    def package_print_out(self, time):
        prtout = ''
        prtout += f'Package ID: {self.ID} - Weight: {self.weight} lbs - Leave Time: {self.leave_time} On Truck: {self.truck} - Deadline: {self.handle_deadline()} - '
        if self.ID == 9 and time < datetime.timedelta(hours=10, minutes=20):
            prtout += f'Council Hall - 300 State St Salt Lake City, UT 84103'
        else:
            prtout += f'{self.get_address()}'

        return prtout