class Paint:
    def __init__(self, thickness, attrList):
        self.materialType = "paint"
        self.thickness = thickness
        self.attrList = attrList

class ObjFromRH:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Check inputs of component is none.
if objAttr == None:
    attr_dict = {
    'bauteil_obergruppe': 'unknown',
    'bauteil_gruner': 'unknown',
    'uuid': 'unknown',
    'kosten': 'unknown',
    'zustand': 'unknown',
    'material': 'unknown',
    'ref_gebauede_geschoss': 'unknown',
    'breite': 'unknown',
    'hoehe': 'unknown',
    'tiefe': 'unknown',
    'flaeche': 'unknown',
    'masse': 'unknown',
    'anzahl': 'unknown',
    'foto1': 'unknown',
    'foto2': 'unknown',
    'co2': 'unknown',
    'url': 'unknown'}
    newObj = ObjFromRH(**attr_dict)
    attrList = newObj
else:
    attrList = objAttr

paintObj = Paint(thickness, attrList)



class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.paintData= paintObj
allData.identity = "innerMaterial"

paint_obj = allData