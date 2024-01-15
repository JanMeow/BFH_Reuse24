import Rhino.Geometry as rg
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree
import System.Array as array
import Rhino
import ghpythonlib.treehelpers as th
import inspect
import scriptcontext as sc

# Ensure we're using the Rhino document, not Grasshopper's
sc.doc = Rhino.RhinoDoc.ActiveDoc

class DetectObjectIsMoved:
    def __init__(self, geometryInput, nickname):

        self.geometryInput = geometryInput
        self.nickname = nickname
        self.detectObjType(self.geometryInput)
        self.isMoved = False
    
    def initializeMovement(self, storeDict):
        # self.store_initial_point_data(self.points, storeDict)
        self.store_initial_curve_data(self.curves, storeDict)
    
    def detectObjType(self, objInput):
        self.points = []
        self.curves = []
        self.surfaces = []

        # Check if the object is a point
        #print(obj)
        if isinstance(objInput, rg.Point3d):
            self.points.append(objInput)
            self.geometryType = "point"
        # Check if the object is a curve
        elif isinstance(objInput, rg.Curve):
            self.curves.append(objInput)
            self.geometryType = "curve"
        # Check if the object is a surface
        elif isinstance(objInput, rg.Surface):
            self.surfaces.append(objInput)
            self.geometryType = "surface"
                
    # Function to store initial curve data
    def store_initial_curve_data(self, curves, storeDict):
        for curve in curves:
            if curve:
                # Extract and store the curve's control points or vertices
                control_points = [pt.Location for pt in curve.ToNurbsCurve().Points]
                storeDict[self.nickname] = (control_points, False, curve)

    # Function to determine if curves have moved
    def have_curves_moved(self, detectCurves, storeDict):
        if detectCurves and isinstance(detectCurves, rg.Curve):
            current_curve = detectCurves
            current_control_points = [pt.Location for pt in current_curve.ToNurbsCurve().Points]
            initial_control_points = storeDict.get(self.nickname)[0]

            # Check if the set of control points has changed
            if any(pt1 != pt2 for pt1, pt2 in zip(current_control_points, initial_control_points)):
                storeDict[self.nickname] = (current_control_points, True, current_curve)
            else:
                storeDict[self.nickname] = (initial_control_points, False, current_curve)



class DetectObjectValue:
    """
    Now this DetectObjectValue only execute for list. However, I need to detect if the number, such as height, material and also the parameters of window, are changed, so I need to modify here.
    """
    def __init__(self, nickname):
        self.nickname = nickname
    
    def initializeValue(self, attrName, attrData, storeDict):
        self.store_initial_Value(attrName, attrData, storeDict)
    
    def store_initial_Value(self, attrName, attrData, storeDict):
        storeDict[self.nickname][attrName] = (len(attrData), False)

    def have_Value_changed(self, attrName, attrData, storeDict):
        if storeDict[self.nickname][attrName][0] != len(attrData):
            storeDict[self.nickname][attrName] = (len(attrData), True)
        else:
            storeDict[self.nickname][attrName] = (len(attrData), False)
    


class Wall:
    def __init__(self, guid, id, geometryInput, checkValueList):
        """
        Can input guid of "Curve"
        It should add guid allowed for inputing "surface"
        Consider when I should add geometryInput. Since init? Because in wall, I cannot find curve by using guid to find the geometry like the way I use in window's point.
        """
        self.guid = guid
        self.guidStr = str(guid)
        self.nickname = "wall_" + str(id)
        self.geometryInput = geometryInput
        self.checkValueList = checkValueList
        self.windowList = []
        self.doorList = []
        self.isMoved = False
        self.rebuild = False
        self.isValueChanged = False

        self.checkMoveObj = DetectObjectIsMoved(self.geometryInput, self.nickname) 
        self.checkValueObj = DetectObjectValue(self.nickname)
        
    def addElement(self, element):
        self.element = element
        
    def addWallType(self, type):
        self.type = type
        
    def addGeometry(self, curve, height):
        self.curve = curve
        self.height = height
        self.surface = rg.Extrusion.Create(curve,height,False)
        
    def addWindow(self, window):
        self.windowList.append(window)
        
    def addDoor(self, door):
        self.doorList.append(door)


    # Method to check if the wall has moved
    def update_movement(self, inputDict):
        try:
            self.checkMoveObj.have_curves_moved(self.curve, inputDict)

        except:
            self.checkMoveObj.initializeMovement(inputDict)
            self.checkMoveObj.have_curves_moved(self.curve, inputDict)

    def check_isMoved(self, searchDict):
        self.isMoved = searchDict[self.nickname][1]
        return self.isMoved
    

    def update_value(self, inputDict):
        for attrName in self.checkValueList:
            attrData = getattr(self, attrName, None)
            if inputDict.get(self.nickname) == None:
                inputDict[self.nickname]={}

            try:
                self.checkValueObj.have_Value_changed(attrName, attrData, inputDict)

            except:
                self.checkValueObj.initializeValue(attrName, attrData, inputDict)
                self.checkValueObj.have_Value_changed(attrName, attrData, inputDict)

    
    def check_value(self, inputDict):
        boolList = [inputDict[self.nickname][attrName][1] for attrName in self.checkValueList]
        
        self.isValueChanged = any(boolList)
        return any(boolList)


    def showAttribute(self):
        self.attributes = []
        for item in dir(self):
            if item.startswith('__') and item.endswith('__'):
                continue
            attr = getattr(self, item)
            if inspect.ismethod(attr):
                continue
            else:
                if item not in ['attributes', 'methods']:  # Avoid including the lists themselves
                    self.attributes.append(item)  # Append the attribute name
        
        print("attr: "+ str(self.attributes))    
    
    def showMethod(self):
        self.methods = []
        for item in dir(self):
            if item.startswith('__') and item.endswith('__'):
                continue
            attr = getattr(self, item)
            if inspect.ismethod(attr):
                self.methods.append(item)  # Append the method name
        
        print("method: "+ str(self.methods))


show = ""
wall_dict = {}
checkValueList = ["windowList", "doorList"]
id = 0
for wallSeries in iWalls:
    obj = sc.doc.Objects.Find(wallSeries).Geometry
    wallSeg = obj.DuplicateSegments()
    for wall in wallSeg:
        wallObj = Wall(wallSeries, id, wall, checkValueList)
        wallObj.addElement("wall")
        wallObj.addWallType(iType)
        wallObj.addGeometry(wall, iHeight)
        #wallObj.check_isMoved(initial_curve_data)
        
        wall_dict[wallObj.nickname] = wallObj
        id += 1
        
        if id == 1:
            show = wallObj.nickname
        




class classForOutput:
    def __init__(self):
        pass

wallData = classForOutput()
wallData.data = wall_dict
oWallData = wallData


wall_dict[show].showAttribute()
wall_dict[show].showMethod()
