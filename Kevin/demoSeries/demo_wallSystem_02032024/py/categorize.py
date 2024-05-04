import Rhino.Geometry as rg
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree
import System.Array as array
print("hiiii")
def categorize(carrierList, windowList, doorList, crvList):
    carrierTree = DataTree[object]()
    windowTree = DataTree[object]()
    doorTree = DataTree[object]()
    crvTree = DataTree[object]()

    carrierList = [carrier.Faces[0] for carrier in carrierList]

    
    windowTreeIndex = []
    if len(windowList) != 0:
        for window in windowList:
            if isinstance(window, rg.Brep):
                windowGeo = window.Faces[0]
            else:
                windowGeo = window.geo.Faces[0]
            
            area_properties = rg.AreaMassProperties.Compute(windowGeo)
            if area_properties is not None:
                centroid = area_properties.Centroid

                minDist = None
                minId = None
                for cId, carrier in enumerate(carrierList):
                    success, uvPU, uvPV = carrier.ClosestPoint(centroid)
                    if success:
                        pt = carrier.PointAt(uvPU, uvPV)
                        dist = pt.DistanceTo(centroid)
                        if minDist == None:
                            minDist = dist
                            minId = cId
                        elif dist < minDist:
                            minDist = dist
                            minId = cId
                windowTreeIndex.append(minId)


    doorTreeIndex = []
    if len(doorList) != 0:
        for door in doorList:
            if isinstance(door, rg.Brep):
                doorGeo = door.Faces[0]
            else:
                doorGeo = door.geo.Faces[0]
            
            area_properties = rg.AreaMassProperties.Compute(doorGeo)
            if area_properties is not None:
                centroid = area_properties.Centroid

                minDist = None
                minId = None
                for cId, carrier in enumerate(carrierList):
                    success, uvPU, uvPV = carrier.ClosestPoint(centroid)
                    if success:
                        pt = carrier.PointAt(uvPU, uvPV)
                        dist = pt.DistanceTo(centroid)
                        if minDist == None:
                            minDist = dist
                            minId = cId
                        elif dist < minDist:
                            minDist = dist
                            minId = cId
                doorTreeIndex.append(minId)


    crvTreeIndex = []
    if len(crvList) != 0:
        for crv in crvList:
            if isinstance(crv, rg.Curve):
                centroid = crv.PointAtNormalizedLength(0.5)
                
                minDist = None
                minId = None
                for cId, carrier in enumerate(carrierList):
                    success, uvPU, uvPV = carrier.ClosestPoint(centroid)
                    if success:
                        pt = carrier.PointAt(uvPU, uvPV)
                        dist = pt.DistanceTo(centroid)
                        if minDist == None:
                            minDist = dist
                            minId = cId
                        elif dist < minDist:
                            minDist = dist
                            minId = cId
                crvTreeIndex.append(minId)
    
    # path = GH_Path(array[int]([0,0,self.layerId]))

    for cId, carrier in enumerate(carrierList):
        path = GH_Path(array[int]([cId]))
        carrierTree.AddRange([carrier], path)
    
    for wId, window in zip(windowTreeIndex, windowList):
        path = GH_Path(array[int]([wId]))
        windowTree.AddRange([window], path)
    
    for dId, door in zip(doorTreeIndex, doorList):
        path = GH_Path(array[int]([dId]))
        doorTree.AddRange([door], path)

    for dId, crv in zip(crvTreeIndex, crvList):
        path = GH_Path(array[int]([dId]))
        crvTree.AddRange([crv], path)
        
    
    return (carrierTree, windowTree, doorTree, crvTree)


a, b, c, d = categorize(carrier, window, door, moduleCrv)