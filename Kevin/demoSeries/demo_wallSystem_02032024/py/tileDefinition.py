import uuid

class MakeTile:
    def __init__(self, width, height, quantity, attrList):
        self.width = width
        self.height = height
        self.quantity = quantity
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
    'uuid': 'tile_uuid_' + str(uuid.uuid4()),
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

    if width != None:
        attr_dict['breite'] = width
    if height != None:
        attr_dict['hoehe'] = height
    if quantity != None:
        attr_dict['anzahl'] = int(quantity)

    newObj = ObjFromRH(**attr_dict)
    newObj.attrDict = attr_dict
    attrList = newObj
else:
    attrList = objAttr

tileObj = MakeTile(width, height, quantity, attrList)


class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.tileData= tileObj
allData.identity = "customizedTile"

tile_obj = allData