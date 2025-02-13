class Warehouse:
    def __init__(self, name, coords, distance):
        self.name = name
        self.coords = coords
        self.inventory = {}
        self.distance = distance
