import Rhino.Geometry as rg
import ghpythonlib.treehelpers as th
import Grasshopper.Kernel as ghkernel
import ghpythonlib.components as ghcomp
import Grasshopper as gh
from Grasshopper.Kernel.Data import GH_Path
import System.Array as array
from Grasshopper import DataTree

import sys
import os

path = ghenv.Component.OnPingDocument().FilePath
parentdir = os.path.dirname(path)
grandparentdir = os.path.dirname(parentdir)
dire = os.path.join(grandparentdir, 'py')
if dire not in sys.path:
    sys.path.append(dire)

# Import modules
import compoundMaterial 
import innerMaterialGenerate
import generateCladding
import normalFacade

# Reload the modules
reload(compoundMaterial)
reload(innerMaterialGenerate)
reload(generateCladding)
reload(normalFacade)

from compoundMaterial import CompoundMaterial
from innerMaterialGenerate import InnerMaterialGenerate
from generateCladding import GenerateCladding
from normalFacade import NormalFacade

import uuid


class Empty:
    def __init__(self, thickness, attrList):
        self.materialType = "paint"
        self.thickness = thickness
        self.attrList = attrList
        self.empty = "empty"
class ObjFromRH:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

attr_dict = {
'bauteil_obergruppe': 'other_' + str(uuid.uuid4()),
'bauteil_gruner': 'other_' + str(uuid.uuid4()),
'uuid': 'paint_uuid_' + str(uuid.uuid4()),
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
paintObj = Empty(0.1, newObj)

class classForOutput:
    def __init__(self):
        pass

emptyData = classForOutput()
emptyData.paintData= paintObj
emptyData.identity = "innerMaterial"





def initialize_globals():
    global initial_data
    initial_data = initial_data if 'initial_data' in globals() else {}

def offset_brep(brep, distances, plane, tolerance=0.01):
    all_offset_breps = []
    
    if brep.Faces.Count > 0:
        face_normal = brep.Faces[0].NormalAt(0.5, 0.5)
        dot_product = plane.ZAxis * face_normal
        
        for distance in distances:
            # If the dot product is negative, reverse the distance to align with the plane's Z-axis
            if dot_product >= 0:
                adjusted_distance = distance
            else:
                adjusted_distance = -distance
            
            # adjusted_distance = distance
            
            offset_breps = rg.Brep.CreateOffsetBrep(brep, adjusted_distance, solid=False, extend=False, tolerance=tolerance)
            if offset_breps[0]:  # Check if the offset operation was successful
                all_offset_breps.append(offset_breps[0][0])
            else:
                print("Offset operation failed for distance.")
                all_offset_breps.append(None)
    else:
        print("Brep has no faces to determine normal.")
    
    return all_offset_breps

def changePath(dataModified, dataSource):
    pathList = dataSource.Paths

    layerTree = DataTree[object]()
    dataList = dataModified.Branches

    for data, path in zip(dataList, pathList):
        layerTree.AddRange(data, path)
    return layerTree

def flattenBrep(oBrep):
    # Assume oBrep has only one face, get the first face
    face = oBrep.Faces[0]
    
    # Get the outer boundary of the face as a curve
    outerLoop = face.OuterLoop.To3dCurve()
    
    # Fit a plane through the Brep vertices to find the best fit plane
    vertices = [v.Location for v in oBrep.Vertices]
    plane_success, pl = rg.Plane.FitPlaneToPoints(vertices)
    
    # Get the area and centroid of the Brep
    area_mass_properties = rg.AreaMassProperties.Compute(oBrep)
    centroid = area_mass_properties.Centroid
    
    # Orient the plane to have its origin at the centroid
    orientPl = rg.Plane(pl.Origin, pl.XAxis, pl.YAxis)
    orientPl.Origin = centroid
    
    # Create target plane by rotating the oriented plane around its X-axis by 90 degrees
    targetPlane = rg.Plane(orientPl)
    
    # Project the outer loop curve to the target plane
    projected_outerLoop = rg.Curve.ProjectToPlane(outerLoop, targetPlane)
    
    # Project any inner loops (holes) if they exist
    projected_innerLoops = []
    for loop in face.Loops:
        if loop.LoopType == rg.BrepLoopType.Inner:
            innerLoopCurve = loop.To3dCurve()
            projected_innerLoop = rg.Curve.ProjectToPlane(innerLoopCurve, targetPlane)
            projected_innerLoops.append(projected_innerLoop)
    
    # Create a planar surface from the projected outer loop
    if projected_outerLoop.IsClosed:
        planarFace = rg.Brep.CreatePlanarBreps([projected_outerLoop] + projected_innerLoops, 0.01)
        if planarFace:
            return planarFace[0] # Return the first Brep if creation was successful
    
    return None

def categorize(carrierList, windowList, doorList, crvList):
    tolerDist = 100
    carrierTree = DataTree[object]()
    windowTree = DataTree[object]()
    doorTree = DataTree[object]()
    crvTree = DataTree[object]()

    carrierList = [carrier.Faces[0] for carrier in carrierList]

    windowTreeIndex = []
    windowDist = []
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
                windowDist.append(minDist)


    doorTreeIndex = []
    doorDist = []
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
                doorDist.append(minDist)


    crvTreeIndex = []
    crvDist = []
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
                crvDist.append(minDist)
    
    # path = GH_Path(array[int]([0,0,self.layerId]))

    for cId, carrier in enumerate(carrierList):
        path = GH_Path(array[int]([cId]))
        carrierTree.AddRange([carrier], path)
    
    for wId, window, wDist in zip(windowTreeIndex, windowList, windowDist):
        if wDist < tolerDist:
            path = GH_Path(array[int]([wId]))
            windowTree.AddRange([window], path)
    
    for dId, door, dDist in zip(doorTreeIndex, doorList, doorDist):
        if dDist < tolerDist:
            path = GH_Path(array[int]([dId]))
            doorTree.AddRange([door], path)

    for dId, crv, cDist in zip(crvTreeIndex, crvList, crvDist):
        if cDist < tolerDist:
            path = GH_Path(array[int]([dId]))
            crvTree.AddRange([crv], path)
        
    
    return (carrierTree, windowTree, doorTree, crvTree)

# Check input of this component getting value
goExecute = True
if Database_collection == None:
    ghenv.Component.AddRuntimeMessage(ghkernel.GH_RuntimeMessageLevel.Warning, "Database_collection is empty.")
    goExecute = False
# ==============================================================================
# Check if carrier, window and door is flatten geometry
if len(Carrier_Geometry) != 0:
    if isinstance(Carrier_Geometry[0], rg.Brep):
        carrierGeoFlat = [flattenBrep(carrier) for carrier in Carrier_Geometry]
else:
    ghenv.Component.AddRuntimeMessage(ghkernel.GH_RuntimeMessageLevel.Warning, "Carrier is empty.")
    goExecute = False

# ==============================================================================
if len(setTile) == 0:
    ghenv.Component.AddRuntimeMessage(ghkernel.GH_RuntimeMessageLevel.Warning, "setTile is empty.")
    goExecute = False
# ==============================================================================
input_collection = {"setTile":None, "claddingDirection":True, "horiOverlap":1, "vertiOverlap":0, "horiAngle":0.5, "vertiAngle":0, "substructWidth":4, "substructThickness":2, "moduleDistance":None, "moduleCurve":None, "moduleCrvDist":10, "init":False}

for name in input_collection:
    if name not in globals() or globals()[name]== None:
        globals()[name] = input_collection[name]

visualEmpty = False
if len(material_collection) == 0:
    material_collection = [emptyData]
    visualEmpty = True
    # ghenv.Component.AddRuntimeMessage(ghkernel.GH_RuntimeMessageLevel.Warning, "inner material is empty.")
    # goExecute = False
# ==============================================================================
inputs = ghenv.Component.Params.Input
outputs = ghenv.Component.Params.Output

for input in inputs:
    iName = input.Name
    if iName == "Database_collection":
        input.Description = "Input a database collection (DB_Collection) to access the material database"
    elif iName == "Carrier_Geometry":
        input.Description = "Geometry for carriers. You need to input geometry (Brep) of walls or roofs"
    elif iName == "Window_Geometry":
        input.Description = "Input window geometry (Brep) or Rhino objects (newObj from windowFromRH)"
    elif iName == "Door_Geometry":
        input.Description = "Input door geometry (Brep) or Rhino objects (newObj from doorFromRH)"
    elif iName == "setTile":
        input.Description = "Configure settings for tiles or facades. Input customized tiles (customizeTile), database tiles (searchDBTile) for tile mode, or material collections for facade mode"
    elif iName == "claddingDirection":
        input.Description = "Boolean to determine the direction of cladding"
    elif iName == "horiOverlap":
        input.Description = "Specify the horizontal overlap distance for wall cladding"
    elif iName == "vertiOverlap":
        input.Description = "Specify the vertical overlap distance for wall cladding"
    elif iName == "horiAngle":
        input.Description = "Set the rotation angle of tiles around the horizontal axis"
    elif iName == "vertiAngle":
        input.Description = "Set the rotation angle of tiles around the vertical axis"
    elif iName == "substructWidth":
        input.Description = "Define the width of the cladding's substructure"
    elif iName == "substructThickness":
        input.Description = "Define the thickness of the cladding's substructure"
    elif iName == "material_collection":
        input.Description = "Input the collection of materials for the interior"
    elif iName == "moduleDistance":
        input.Description = "Specify the module width to determine intervals for wall segmentation."
    elif iName == "moduleCurve":
        input.Description = "Input curves to define how walls are segmented into modules"
    elif iName == "moduleCrvDist":
        input.Description = "Specify the seam width for walls segmented into modules"

for output in outputs:
    oName = output.Name
    if oName == "visualObj":
        output.Description = "Visual representation of wall geometries. Connect this output to either tileFacadeViewer or normalFacadeViewer for display"
    elif oName == "allTypeMaterialModule":
        output.Description = "Visual representation of wall modules. Connect this output to the module visualization component"
    elif oName == "matRecordObj":
        output.Description = "Output object containing detailed records of materials used, including quantities and relevant details"
    elif oName == "ruler":
        output.Description = "Curve used as a guide for aligning openings within a 10cm tolerance"
# ==============================================================================


if goExecute:
    carrierTree, windowTree, doorTree, crvTree = categorize(carrierGeoFlat, Window_Geometry, Door_Geometry, moduleCurve)
    if init:
        # initial_data is for tile calculation
        initial_data = {}
    else:
        initialize_globals()
        inputDB = Database_collection.all_DB

        # Start execute main function
        compoundMaterialObj = CompoundMaterial(material_collection, DB = inputDB)
        materialList = compoundMaterialObj.new_materialList
        material_thickness = compoundMaterialObj.thicknessList

        offsetList = []
        total = 0
        for num in material_thickness:
            total += num
            offsetList.append(total)

        offsetCladdingDist = sum(material_thickness)
        offsetList = offsetList[:-1]
        offsetList.insert(0,0)

##################################################################
        rulerTree = DataTree[object]()
        visualObjTree = DataTree[object]()
        allTypeMaterialModuleTree = DataTree[object]()
        matRecordObjTree = DataTree[object]()

        for pathId, path in enumerate(carrierTree.Paths):
            print("Start wall_" + str(pathId))
            carrier = carrierTree.Branch(path)[0].Brep

            windowData = windowTree.Branch(path)
            window = windowData if not windowData==None else []
            # window = [win.ToBrep() for win in window]

            doorData = doorTree.Branch(path)
            door = doorData if not doorData==None else []

            crvData = crvTree.Branch(path)
            moduleCrv = crvData if not crvData==None else []
##################################################################
            


            if setTile[0].identity == "customizedTile":
                print("Go into customizeTile")
                claddingObj = GenerateCladding(DB = inputDB, wallGeo=carrier, windowGeo=window, doorGeo=door, claddingDirection = claddingDirection, horizontalOverlap=horiOverlap, verticalOverlap=vertiOverlap, horizontalAngle=horiAngle, verticalAngle=vertiAngle, substructWidth=substructWidth, substructThickness=substructThickness, offsetDist=offsetCladdingDist, tileDimension = setTile)
                offsetCladdingDistView = offsetCladdingDist
                
            elif setTile[0].identity == "searchTile":
                print("Go into searchTile")
                tileSetting = setTile[0].searchTileData
                claddingWidth = tileSetting["claddingWidth"]
                claddingLength = tileSetting["claddingLength"]
                kindNum = tileSetting["kindNum"]
                wWeight = tileSetting["wWeight"]
                lWeight = tileSetting["lWeight"]

                claddingObj = GenerateCladding(DB=inputDB, wallGeo=carrier, windowGeo=window, doorGeo=door, claddingWidth=claddingWidth, claddingLength=claddingLength, kindNum=kindNum, wWeight=wWeight, lWeight=lWeight, claddingDirection = claddingDirection, horizontalOverlap=horiOverlap, verticalOverlap=vertiOverlap, horizontalAngle=horiAngle, verticalAngle=vertiAngle, substructWidth=substructWidth, substructThickness=substructThickness, offsetDist=offsetCladdingDist)
                offsetCladdingDistView = offsetCladdingDist
            
            else:
                print("Go into Board Facade Process")
                claddingObj = NormalFacade(DB=inputDB, wallGeo=carrier, windowGeo=window, doorGeo=door, claddingDirection = claddingDirection, offsetDist=offsetCladdingDist, claddingMaterial=setTile)
                facadeMaterial = claddingObj.facadeMaterial
                offsetCladdingDistView = offsetCladdingDist + claddingObj.normalOffsetDist

                ruler = claddingObj.ruler
                rulerTree.AddRange(ruler, path)

            # a = claddingObj.check
            # b = claddingObj.check2


            if setTile[0].identity == "customizedTile" or setTile[0].identity == "searchTile":
                facadeType = 'tile'
                # Output claddingObj
                comb = th.list_to_tree(claddingObj.combinationGraph)
                tileGeometry = th.list_to_tree(claddingObj.originalCoTileGeo)
                substructureGeo = claddingObj.substructureGeo #
                claddingInfo = claddingObj.tileAttrDict
            else:
                facadeType = 'normal'
                comb = None
                tileGeometry = facadeMaterial
                substructureGeo = None
                claddingInfo = claddingObj.claddingInfo
            
            # Common Attribute
            wallFrame = claddingObj.wallFrame
            wallForInnerMaterial = claddingObj.wallForInnerGeo
            windowForFinalList = claddingObj.windowForFinalList 
            doorForFinalList = claddingObj.doorForFinalList 
            openingInfo = claddingObj.chosenDoorAttr


            # Calculate innerMaterial Part
            offsetted_surface = offset_brep(wallForInnerMaterial, offsetList, wallFrame)
            wallObj = InnerMaterialGenerate(inputDB, offsetted_surface, materialList, material_thickness, moduleDistance, wallFrame, claddingDirection, moduleCrv, moduleCrvDist, True)
            allTypeMaterial = wallObj.allTypeMaterial
            allTypeMaterialModule = wallObj.allTypeMaterialModule


            class matClass:
                def __init__(self):
                    pass

            
            usedMatDict = {}
            usedMatDict['innerMaterial'] = wallObj.materialInfoDict
            usedMatDict['window'] = claddingObj.chosenWindowAttr
            usedMatDict['door'] = claddingObj.chosenDoorAttr

            usedMatDict['outerMaterial'] = {}
            if facadeType == 'tile':
                usedMatDict['outerMaterial']['type'] = 'tile'
            else:
                usedMatDict['outerMaterial']['type'] = 'normal'
            usedMatDict['outerMaterial']['matInfo'] = claddingInfo


            matRecordObj = matClass()
            matRecordObj.usedMatDict = usedMatDict

            matRecordObjTree.AddRange([matRecordObj], path)

            class visualClass:
                def __init__(self):
                    pass
            
            visualObj = visualClass()
            visualObj.comb = comb
            visualObj.tileGeometry = tileGeometry
            visualObj.allTypeMaterial = allTypeMaterial
            visualObj.substructureGeo = substructureGeo
            visualObj.wallFrame = wallFrame
            visualObj.offsetCladdingDist = offsetCladdingDistView
            # print(offsetCladdingDist)
            visualObj.windowGeo = windowForFinalList
            visualObj.doorGeo = doorForFinalList
            visualObj.usedMatDict = usedMatDict

            visualObj.visualEmpty = True if visualEmpty else False


            visualObjTree.AddRange([visualObj], path)

            
            data = th.list_to_tree(allTypeMaterialModule.Branches)
            allTypeMaterialModule = changePath(data, allTypeMaterialModule)


        oRuler = rulerTree
        oVisualObj = visualObjTree
        oMatRecordObj = matRecordObjTree




else:
    ghenv.Component.AddRuntimeMessage(ghkernel.GH_RuntimeMessageLevel.Warning, "Check necessary input.")

 
