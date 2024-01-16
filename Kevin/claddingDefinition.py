class Cladding:
    def __init__(self, length, width, thickness):
        self.materialType = "cladding"
        self.length = length
        self.width = width
        self.thickness = thickness


claddingObj = Cladding(length, width, thickness)



class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.claddingData= claddingObj

cladding_obj = allData