class Cladding:
    def __init__(self, length, width, thickness, direction):
        self.materialType = "cladding"
        self.length = length
        self.width = width
        self.thickness = thickness
        self.direction = direction


claddingObj = Cladding(length, width, thickness, direction)



class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.claddingData= claddingObj

cladding_obj = allData