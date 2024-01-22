class Paint:
    def __init__(self, thickness):
        self.materialType = "paint"
        self.thickness = thickness


paintObj = Paint(thickness)



class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.paintData= paintObj

paint_obj = allData