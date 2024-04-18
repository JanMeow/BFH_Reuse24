class MakeTile:
    def __init__(self, width, height, quantity):
        self.width = width
        self.height = height
        self.quantity = quantity


tileObj = MakeTile(width, height, quantity)

class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.tileData= tileObj

tile_obj = allData