class Address:
    def __init__(self, ID, name, street):
        self.ID = int(ID)
        self.name = name
        self.street = street
        self.city = None
        self.state = None
        self.zip = None

    def __str__(self):
        string_builder = ""

        string_builder += str(self.name) + ' - '
        string_builder += str(self.street) + ' '
        if self.city is not None:
            string_builder += str(self.city)
            string_builder += ', ' + str(self.state)
            string_builder += ' ' + str(self.zip)

        return string_builder