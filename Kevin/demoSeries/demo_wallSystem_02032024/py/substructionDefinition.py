import uuid

class Substruct:
    def __init__(self, width, thickness, distance, direction, searchDB, attrList):
        self.materialType = "substruct"
        self.width = width
        self.thickness = thickness
        self.distance = distance
        self.direction = direction
        self.searchDB = searchDB
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
    'uuid': 'substructure_uuid_' + str(uuid.uuid4()),
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

if searchDB == None:
    searchDB = False
if direction == None:
    direction = True



substructObj = Substruct(width, thickness, distance, direction, searchDB, attrList)



class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.substructData= substructObj
allData.identity = "innerMaterial"

substruct_obj = allData