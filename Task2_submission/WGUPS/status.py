from enum import Enum


# Create ENUM for the driver class
class Available(Enum):
    UNAVAILABLE = 'UNAVAILABLE'
    AVAILABLE = 'AVAILABLE'

    def __str__(self):
        return self.value


# Create ENUM for package status
class Status(Enum):
    AT_HUB = 'AT_HUB'
    OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY'
    DELIVERED = 'DELIVERED'
    DELAYED = 'DELAYED'

    def __str__(self):
        return self.value