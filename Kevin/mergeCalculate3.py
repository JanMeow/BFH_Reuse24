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


from copy import copy
import threading


class WallCalculate:
    def __init__(self, wallObj, brickLength, brickHeight):
        self.wallObj = wallObj
        self.brickLength = brickLength
        self.brickHeight = brickHeight
        self.windowList = [windowData.get(key) for key in self.wallObj.windowList]
        self.surface = wallObj.surface
        self.curve = wallObj.curve
        self.wallHeight = wallObj.height
        self.extrusionStore = self.generatePattern()
        self.windowRectangle = self.buildWindow()
        self.facade = self.wallWithOpen()

    def generatePattern(self):
        evenSegment = Shatter(self.curve, self.curve.DivideByLength(self.brickLength, True))
        oddCrv = self.curve.Trim(rg.CurveEnd.Start, self.brickLength / 2)
        arr = oddCrv.DivideByLength(self.brickLength, True)
        oddSegment = Shatter(oddCrv, arr)

        evenExtrusion = [rg.Extrusion.Create(crv, self.brickHeight, False) for crv in evenSegment if crv]
        oddExtrusion = [rg.Extrusion.Create(crv, self.brickHeight, False) for crv in oddSegment if crv]

        layerNum = int(math.ceil(self.wallHeight / self.brickHeight))
        extrusionStore = []
        for layer in range(layerNum):
            isEvenLayer = layer % 2 == 0
            extrusions = evenExtrusion if isEvenLayer else oddExtrusion
            translation = rg.Vector3d(0, 0, self.brickHeight * layer)
            matrix = rg.Transform.Translation(translation)
            for brick in extrusions:
                brickCopy = copy(brick)
                brickCopy.Transform(matrix)
                extrusionStore.append(brickCopy)
        
        return extrusionStore or []

    def buildWindow(self):
        windowRectangle = []
        for windowObj in self.windowList:
            rect = rg.Rectangle3d(windowObj.winPlane, windowObj.width, windowObj.height)
            negXAxis = rg.Transform.Translation(-windowObj.winPlane.XAxis * (windowObj.width / 2))
            rect.Transform(negXAxis)
            windowRectangle.append(rect)
        return windowRectangle

    def wallWithOpen(self):
        if not self.windowList:
            return self.extrusionStore

        combinedGeometries = self.windowRectangle + [self.surface]
        windowRect = BoundarySurfaces(combinedGeometries)
        return self.processFacade(windowRect)

    def processFacade(self, windowRect):
        if not self.extrusionStore:
            return []

        facade = []
        threads = []
        facade_lock = threading.Lock()

        for block in self.extrusionStore:
            thread = threading.Thread(target=self._process_block, args=(block, windowRect, facade, facade_lock))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return facade

    # def _process_block(self, block, windowRect, facade, facade_lock):
    #     result = BrepXBrep(windowRect, block)
    #     if result:
    #         with facade_lock:
    #             facade.append(result[0])

    def _process_block(self, block, windowRect, facade, facade_lock):
        # 如果 block 是 Extrusion 类型，则转换为 Brep
        if isinstance(block, rg.Extrusion):
            block = block.ToBrep()

        # 同样，确保 windowRect 也是 Brep 类型
        if isinstance(windowRect, rg.Extrusion):
            windowRect = windowRect.ToBrep()

        intersection = rg.Intersect.Intersection.BrepBrep(windowRect, block, 0.01)  # 0.01 是容差值
        if intersection[0]:  # 检查是否有交集
            with facade_lock:
                facade.extend(intersection[1])  # intersection[1] 包含了交集的结果




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