class Substruct:
    def __init__(self, width, thickness, distance, direction):
        self.materialType = "substruct"
        self.width = width
        self.thickness = thickness
        self.distance = distance
        self.direction = direction


substructObj = Substruct(width, thickness, distance, direction)



class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.substructData= substructObj
substruct_obj = allData