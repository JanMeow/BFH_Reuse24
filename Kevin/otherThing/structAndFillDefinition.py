class SubstructInfill:
    def __init__(self, width, thickness, distance, direction):
        self.materialType = "substructInfill"
        self.width = width
        self.thickness = thickness
        self.distance = distance
        self.direction = direction


substructInfillObj = SubstructInfill(width, thickness, distance, direction)



class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.substructInfillData= substructInfillObj
substructInfill_obj = allData