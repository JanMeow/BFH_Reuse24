class Board:
    def __init__(self,length, width, thickness, direction, searchDB, attrList, pt):
        self.materialType = "board"
        self.length = length
        self.width = width
        self.thickness = thickness
        self.direction = direction
        self.searchDB = searchDB
        self.attrList = attrList
        self.pt = pt

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

if searchDB == None:
    searchDB = False
if direction == None:
    direction = True


boardObj = Board(length, width, thickness, direction, searchDB, attrList, pt)



class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.boardData= boardObj
allData.identity = "innerMaterial"

board_obj = allData