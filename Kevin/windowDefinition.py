import Rhino.Geometry as rg
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree
import System.Array as array
import Rhino
import ghpythonlib.treehelpers as th
import System
import scriptcontext as sc
import inspect

# Ensure we're using the Rhino document, not Grasshopper's
sc.doc = Rhino.RhinoDoc.ActiveDoc

class DetectObjectIsMoved:
    def __init__(self, geometryInput, nickname):

        self.geometryInput = rg.Point3d(geometryInput)
        self.nickname = nickname
        self.detectObjType(self.geometryInput)
        self.isMoved = False
    
    def initializeMovement(self, storeDict):
        self.store_initial_point_data(self.points, storeDict)
        # self.store_initial_curve_data(self.curves, storeDict)

    def detectObjType(self, objInput):
        self.points = []
        self.curves = []
        self.surfaces = []

        # Check if the object is a point
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


        # Function to store initial locations
    def store_initial_point_data(self, points, storeDict):
        for point in points:
            # Get the object's Rhino document object
            if point:
                # Store the initial location (for point objects, use the Location property)
                storeDict[self.nickname] = (point, False)
                

    # Function to check if objects have moved
    def have_points_moved(self, detectPoints, storeDict):
            if detectPoints and isinstance(detectPoints, rg.Point3d):
                current_data = detectPoints
                initial_data = storeDict.get(self.nickname)[0]

                if current_data != initial_data:
                    storeDict[self.nickname] = (current_data, True)
                else:
                    storeDict[self.nickname] = (initial_data, False)



class Window:
    def __init__(self, guid, id):
        """
        Can input guid of "Point"
        It should add guid allowed for inputing "surface"
        """
        self.guid = guid
        self.guidStr = str(guid)
        self.nickname = "window_" + str(id)
        self.wall = None
        # create self.pt for self.checkObj
        self.addPoint()
        self.checkMoveObj = DetectObjectIsMoved(self.pt, self.nickname)
        self.isMoved = False
        
    def addElement(self, element):
        self.element = element
        
    def addHeight(self, height):
        self.height = height
        
    def addWidth(self, width):
        self.width = width
        
    def addLocHeight(self, locHeight):
        self.locHeight = locHeight
        
    def addPoint(self):
        self.pt = rg.Point3d(sc.doc.Objects.Find(self.guid).Geometry.Location)
           
    def setWall(self, wall):
        self.wall = wall
    

    # Method to check if the wall has moved
    def update_movement(self, inputDict):
        try:
            self.checkMoveObj.have_points_moved(self.pt, inputDict)

        except:
            self.checkMoveObj.initializeMovement(inputDict)
            self.checkMoveObj.have_points_moved(self.pt, inputDict)

    def check_isMoved(self, searchDict):
        self.isMoved = searchDict[self.nickname][1]
        return self.isMoved


        
        
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
window_dict = {}
id = 0
for window in iWindows:
    windowObj = Window(window, id)
    windowObj.addElement("window")
    windowObj.addHeight(iHeight)
    windowObj.addWidth(iWidth)
    windowObj.addLocHeight(iLocHeight)
    windowObj.addPoint()
    #windowObj.check_isMoved(initial_point_data)
    
    window_dict[windowObj.nickname] = windowObj
    id += 1
    
    if id == 1:
        show = windowObj.nickname






class classForOutput:
    def __init__(self):
        pass

windowData = classForOutput()
windowData.data = window_dict
oWindowData = windowData

window_dict[show].showAttribute()
window_dict[show].showMethod()

# print(initial_point_data)