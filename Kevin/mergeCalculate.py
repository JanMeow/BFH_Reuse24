import Rhino.Geometry as rg
from ghpythonlib.components import BrepClosestPoint
import scriptcontext as rs
import time
import math
from ghpythonlib.components import Shatter, BoundarySurfaces, BrepXBrep
from copy import deepcopy

brickLength, brickHeight = tempPattern

start = time.time()
wallData = iWallData.data
windowData = iWindowData.data


if init:
    initial_point_data = {}
    initial_curve_data = {}
    initial_value_data = {}
    wallCalculateData = {}

# check if object is moved
try:
    for wallKey in wallData:
        wallData[wallKey].update_movement(initial_curve_data)

    for windowKey in windowData:
        windowData[windowKey].update_movement(initial_point_data)

    for wallKey in wallData:
        wallData[wallKey].check_isMoved(initial_curve_data)

    for windowKey in windowData:
        windowData[windowKey].check_isMoved(initial_point_data)

except:
    initial_point_data = {}
    initial_curve_data = {}

    # check if object is moved
    for wallKey in wallData:
        wallData[wallKey].update_movement(initial_curve_data)

    for windowKey in windowData:
        windowData[windowKey].update_movement(initial_point_data)

    for wallKey in wallData:
        wallData[wallKey].check_isMoved(initial_curve_data)

    for windowKey in windowData:
        windowData[windowKey].check_isMoved(initial_point_data)


# Calculate the closest wall of windows
for key in windowData:
    windowData[key].wall = []
for key in wallData:
    wallData[key].windowList = []

wallList = [(wallData[key].nickname, wallData[key].surface) for key in wallData]
window_List = [(windowData[key].nickname, windowData[key].pt) for key in windowData]

for winNickname, winPt in window_List:
    allDist = []
    allPt = []
    allWallNickname = []
    for wallNickname, wallSrf in wallList:
        wallSrf = wallSrf.ToBrep()
        closestPt = wallSrf.ClosestPoint(winPt)
        dist = winPt.DistanceTo(closestPt)
        allDist.append(dist)
        allPt.append(closestPt)
        allWallNickname.append(wallNickname)

    minDist = min(allDist)
    closestId = allDist.index(minDist)
    ptOnWall = allPt[closestId]

    xAxis = ptOnWall - winPt
    yAxis = rg.Vector3d(0,0,1)
    worldZAxis = rg.Vector3d(0,0,1)
    winPlane = rg.Plane(ptOnWall, xAxis, yAxis)
    winPlane.Rotate(math.pi/2, worldZAxis, ptOnWall)
    winPlane.Translate(worldZAxis*windowData[winNickname].locHeight)
    windowData[winNickname].winPlane = winPlane
    
    closestWallNickname = allWallNickname[closestId]
    wallData[closestWallNickname].windowList.append(winNickname)
    windowData[winNickname].wall = closestWallNickname


# check if value is change
try:
    for wallKey in wallData:
        wallData[wallKey].update_value(initial_value_data)

    for wallKey in wallData:
        wallData[wallKey].check_value(initial_value_data)

except:
    initial_value_data = {}

    for wallKey in wallData:
        #print(initial_value_data)
        wallData[wallKey].update_value(initial_value_data)
    
    for wallKey in wallData:
        wallData[wallKey].check_value(initial_value_data)


class WallCalculate:
    def __init__(self, wallObj, brickLength, brickHeight):
        self.wallObj = wallObj
        self.brickLength = brickLength
        self.brickHeight = brickHeight
        self.windowList = [windowData.get(key) for key in self.wallObj.windowList]
        self.surface = wallObj.surface
        self.curve = wallObj.curve
        self.wallHeight = wallObj.height
        self.generatePattern()
        self.buildWindow()
        self.wallWithOpen()
    
    def generatePattern(self):
        evenSegment = Shatter(self.curve, self.curve.DivideByLength(self.brickLength, True))
        see = self.curve
        oddCrv = see.Trim(rg.CurveEnd.Start, self.brickLength/2)
        arr = oddCrv.DivideByLength(self.brickLength, True)
        oddSegment = Shatter(oddCrv, arr)
        self.headCrv = rg.LineCurve(rg.Line(self.curve.PointAt(0), oddCrv.PointAt(arr[0])))
        #oddSegment.insert(0, self.headCrv)
        matrix = rg.Transform.Translation(rg.Vector3d(0, 0, self.brickHeight))
        _ = [c.Transform(matrix) for c in oddSegment]

        #rg.Extrusion.Create(curve,height,False)
        evenExtrusion = [rg.Extrusion.Create(crv,self.brickHeight,False) for crv in evenSegment]
        oddExtrusion = [rg.Extrusion.Create(crv,self.brickHeight,False) for crv in oddSegment]

        layerNum = self.wallHeight / self.brickHeight
        if layerNum%2 == 0:
            evenLayerNum = layerNum/2
            oddLayerNum = layerNum/2
        else:
            evenLayerNum = math.floor(layerNum/2)
            oddLayerNum = layerNum - evenLayerNum

        self.extrusionStore = []
        
        for evenNum in range(int(evenLayerNum)):
            matrix = rg.Transform.Translation(rg.Vector3d(0, 0, self.brickHeight*2*evenNum))
            for brick in evenExtrusion:
                brickMove = deepcopy(brick)
                brickMove.Transform(matrix)
                self.extrusionStore.append(brickMove)

        for oddNum in range(int(oddLayerNum)):
            matrix = rg.Transform.Translation(rg.Vector3d(0, 0, self.brickHeight*2*oddNum))
            for brick in oddExtrusion:
                brickMove = deepcopy(brick)
                brickMove.Transform(matrix)
                self.extrusionStore.append(brickMove)
    
    def buildWindow(self):
        self.windowRectangle = []
        for windowObj in self.windowList:
            rect = rg.Rectangle3d(windowObj.winPlane, windowObj.width, windowObj.height)
            negXAxis = rg.Transform.Translation(-windowObj.winPlane.XAxis*(windowObj.width/2))
            rect.Transform(negXAxis)
            self.windowRectangle.append(rect)
    
    def wallWithOpen(self):
        if len(self.windowList)!=0 and len(self.windowList)>1:
            windowRect = BoundarySurfaces(self.windowRectangle)
            windowRect.append(self.surface)
            wallFrame = BoundarySurfaces(windowRect)
            self.facade = [BrepXBrep(wallFrame, block)[0] for block in self.extrusionStore]
        elif len(self.windowList)==1:
            li = []
            windowRect = BoundarySurfaces(self.windowRectangle)
            li.append(windowRect)
            li.append(self.surface)
            wallFrame = BoundarySurfaces(li)
            self.facade = [BrepXBrep(wallFrame, block)[0] for block in self.extrusionStore]
        else:
            self.facade = self.extrusionStore



# Detect which wall need to be rebuild.
for wallKey in wallData:
    boolList = [windowData.get(windowNickname).isMoved for windowNickname in wallData[wallKey].windowList]
    boolList.append(wallData[wallKey].isMoved)
    boolList.append(wallData[wallKey].isValueChanged)
    isTrueInside = any(boolList)
    wallData[wallKey].rebuild = isTrueInside


try:
    for wallKey in wallData:
        if wallData[wallKey].rebuild or wallCalculateData.get(wallData[wallKey].nickname) == None:
            wallFacadeObj = WallCalculate(wallData[wallKey], brickLength, brickHeight)
            wallCalculateData[wallData[wallKey].nickname] = wallFacadeObj
except:
    wallCalculateData = {}
    for wallKey in wallData:
        if wallData[wallKey].rebuild or wallCalculateData.get(wallData[wallKey].nickname) == None:
            wallFacadeObj = WallCalculate(wallData[wallKey], brickLength, brickHeight)
            wallCalculateData[wallData[wallKey].nickname] = wallFacadeObj


# buildWall = WallCalculate(wallData["wall_0"], brickLength, brickHeight)
# a = buildWall.windowRectangle
# b = buildWall.extrusionStore
# c = buildWall.surface
# d = buildWall.facade


class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.wallData= wallData
allData.windowData = windowData
allData.facadeData = wallCalculateData
oAllData = allData

#for key in wallData:
#    print(wallData[key].windowList)

end = time.time()
print(end - start)