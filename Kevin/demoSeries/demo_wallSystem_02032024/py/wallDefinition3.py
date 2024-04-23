import Rhino.Geometry as rg
import ghpythonlib.treehelpers as th
import Grasshopper.Kernel as ghkernel
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


# Check input of this component getting value
goExecute = True
if DB == None:
    ghenv.Component.AddRuntimeMessage(ghkernel.GH_RuntimeMessageLevel.Warning, "DB is empty.")
    goExecute = False
# ==============================================================================
# Check if carrier, window and door is flatten geometry
if carrierGeo != None:
    carrierGeoFlat = flattenBrep(carrierGeo)
else:
    ghenv.Component.AddRuntimeMessage(ghkernel.GH_RuntimeMessageLevel.Warning, "Carrier is empty.")
    goExecute = False
if len(windowGeo) != 0:
    if isinstance(windowGeo[0], rg.Brep):
        windowGeo = [flattenBrep(win) for win in windowGeo]
if len(doorGeo) != 0:
    if isinstance(doorGeo[0], rg.Brep):
        doorGeo = [flattenBrep(door) for door in doorGeo]
# ==============================================================================
if len(setTile) == 0:
    ghenv.Component.AddRuntimeMessage(ghkernel.GH_RuntimeMessageLevel.Warning, "setTile is empty.")
    goExecute = False
# ==============================================================================
input_collection = {"setTile":None, "claddingDirection":True, "horiOverlap":1, "vertiOverlap":0, "horiAngle":0.5, "vertiAngle":0, "substructWidth":4, "substructThickness":2, "moduleDistance":None, "moduleCurve":None, "moduleCrvDist":10, "init":False}

for name in input_collection:
    if name not in globals() or globals()[name]== None:
        globals()[name] = input_collection[name]

if len(material_collection) == 0:
    ghenv.Component.AddRuntimeMessage(ghkernel.GH_RuntimeMessageLevel.Warning, "inner material is empty.")
    goExecute = False

# if claddingDirection == None:
#     claddingDirection = True
# if horiOverlap == None:
#     horiOverlap = 1
# if vertiOverlap == None:
#     vertiOverlap = 0
# if horiAngle == None:
#     horiAngle = 5
# if vertiAngle == None:
#     vertiAngle = 0
# # ==============================================================================
# if substructWidth == None:
#     substructWidth = 40
# if substructThickness == None:
#     substructThickness = 20
# if len(material_collection) == 0:
#     ghenv.Component.AddRuntimeMessage(ghkernel.GH_RuntimeMessageLevel.Warning, "inner material is empty.")
#     goExecute = False
# if moduleDistance == None:
#     moduleDistance = 1800
# if len(moduleCurve) == 0:
#     moduleCurve = []
# if moduleCrvDist == None:
#     moduleCrvDist = 100
# if init == None:
#     init = False


if goExecute:
    if init:
        # initial_data is for tile calculation
        initial_data = {}
    else:
        initialize_globals()
        inputDB = DB.all_DB

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



        if setTile[0].identity == "customizedTile":
            print("Go into customizeTile")
            claddingObj = GenerateCladding(DB = inputDB, wallGeo=carrierGeoFlat, windowGeo=windowGeo, doorGeo=doorGeo, claddingDirection = claddingDirection, horizontalOverlap=horiOverlap, verticalOverlap=vertiOverlap, horizontalAngle=horiAngle, verticalAngle=vertiAngle, substructWidth=substructWidth, substructThickness=substructThickness, offsetDist=offsetCladdingDist, tileDimension = setTile)
            
        elif setTile[0].identity == "searchTile":
            print("Go into searchTile")
            tileSetting = setTile[0].searchTileData
            claddingWidth = tileSetting["claddingWidth"]
            claddingLength = tileSetting["claddingLength"]
            kindNum = tileSetting["kindNum"]
            wWeight = tileSetting["wWeight"]
            lWeight = tileSetting["lWeight"]

            claddingObj = GenerateCladding(DB=inputDB, wallGeo=carrierGeoFlat, windowGeo=windowGeo, doorGeo=doorGeo, claddingWidth=claddingWidth, claddingLength=claddingLength, kindNum=kindNum, wWeight=wWeight, lWeight=lWeight, claddingDirection = claddingDirection, horizontalOverlap=horiOverlap, verticalOverlap=vertiOverlap, horizontalAngle=horiAngle, verticalAngle=vertiAngle, substructWidth=substructWidth, substructThickness=substructThickness, offsetDist=offsetCladdingDist)
        
        else:
            print("Go into Board Facade Process")
            claddingObj = NormalFacade(DB=inputDB, wallGeo=carrierGeoFlat, windowGeo=windowGeo, doorGeo=doorGeo, claddingDirection = claddingDirection, offsetDist=offsetCladdingDist, claddingMaterial=setTile)
            facadeMaterial = claddingObj.facadeMaterial



        if setTile[0].identity == "customizedTile" or setTile[0].identity == "searchTile":
            facadeType = 'tile'
            # Output claddingObj
            comb = th.list_to_tree(claddingObj.combinationGraph)
            originalCoTileGeo = th.list_to_tree(claddingObj.originalCoTileGeo)
            substructureGeo = claddingObj.substructureGeo #
            claddingInfo = claddingObj.tileAttrDict
        else:
            facadeType = 'normal'
            comb = None
            originalCoTileGeo = facadeMaterial
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
        wallObj = InnerMaterialGenerate(inputDB, offsetted_surface, materialList, material_thickness, moduleDistance, wallFrame, claddingDirection, moduleCurve, moduleCrvDist, True)
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

        class visualClass:
            def __init__(self):
                pass
        
        visualObj = visualClass()
        visualObj.comb = comb
        visualObj.originalCoTileGeo = originalCoTileGeo
        visualObj.allTypeMaterial = allTypeMaterial
        visualObj.substructureGeo = substructureGeo
        visualObj.wallFrame = wallFrame

        
        data = th.list_to_tree(allTypeMaterialModule.Branches)
        allTypeMaterialModule = changePath(data, allTypeMaterialModule)
else:
    ghenv.Component.AddRuntimeMessage(ghkernel.GH_RuntimeMessageLevel.Warning, "Check necessary input.")

 
