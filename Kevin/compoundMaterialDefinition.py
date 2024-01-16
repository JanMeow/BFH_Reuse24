class CompoundMaterial:
    def __init__(self, materialList):
        self.materialList = materialList
        self.new_materialList = self.readMaterial(self.materialList)
        self.thicknessList = self.calculateThickness(self.new_materialList)

    
    def readMaterial(self, materialList):
        new_materialList = []
        for mat in materialList:
            if hasattr(mat, 'boardData'):
                new_materialList.append(mat.boardData)
            elif hasattr(mat, 'substructInfillData'):
                new_materialList.append(mat.substructInfillData)
            elif hasattr(mat, 'substructData'):
                new_materialList.append(mat.substructData)
            elif hasattr(mat, 'paintData'):
                new_materialList.append(mat.paintData)
            elif hasattr(mat, 'claddingData'):
                new_materialList.append(mat.claddingData)
        return new_materialList

    
    def calculateThickness(self, materialList):
        thicknessList = []
        for mat in materialList:
            thicknessList.append(mat.thickness)
        return thicknessList






compoundMaterialObj = CompoundMaterial(material_collection)
materialList = compoundMaterialObj.new_materialList
material_thickness = compoundMaterialObj.thicknessList



print(compoundMaterialObj.thicknessList)
