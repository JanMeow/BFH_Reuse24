import Rhino.Geometry as rg
from ghpythonlib.components import Area, SurfaceClosestPoint, EvaluateSurface, Contour, SurfaceSplit, Extrude, OffsetCurve, BoundarySurfaces
import ghpythonlib.treehelpers as th
import math
from copy import copy
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree
import System.Array as array


def create_contours(surface, base_plane, interval):
    base_plane = copy(base_plane)
    base_plane.Rotate(math.pi/2, base_plane.XAxis, base_plane.Origin)
    base_plane.Rotate(math.pi/10, base_plane.ZAxis, base_plane.Origin)
    contours = []
    trimmed_contours = []

    # Get the bounding box of the surface in the plane's coordinate system
    bbox = surface.GetBoundingBox(base_plane)

    # Start and end values for contouring in the direction of the plane's normal
    start = bbox.Min.Z
    end = bbox.Max.Z

    # Generate contours
    z = start
    while z <= end:
        # Create a plane parallel to the base plane at height z
        contour_plane = rg.Plane(base_plane)
        contour_plane.Translate(base_plane.Normal * z)

        # Generate the contour
        contour_curves = rg.Brep.CreateContourCurves(surface, contour_plane)
        contours.extend(contour_curves)

        z += interval

    # Get the edge curves of the surface
    edge_curves = surface.DuplicateEdgeCurves()
    boundary = rg.Curve.JoinCurves(edge_curves)[0]  # Join edge curves to form a single boundary curve
    
    # Trim contours
    for contour in contours:
        intersection_events = rg.Intersect.Intersection.CurveCurve(contour, boundary, 0.01, 0.01)
        if intersection_events:
            intersection_params = [event.ParameterA for event in intersection_events]
            segments = contour.Split(intersection_params)
            for segment in segments:
                trimmed_contours.append(segment)

    return trimmed_contours


def create_beam(curve, base_plane, width, height):
    start_point = curve.PointAtStart

    # Create a plane at the start point with the same orientation as the provided plane
    section_plane = rg.Plane(start_point, base_plane.YAxis, base_plane.ZAxis)
    matrix = rg.Transform.Translation(-base_plane.YAxis*width/2)
    section_plane.Transform(matrix)

    # Create a rectangle in this plane
    rectangle = rg.Rectangle3d(section_plane, width, height)

    # Create a sweep
    sweep = rg.SweepOneRail()
    sweep.AngleToleranceRadians = 0.01
    sweep.ClosedSweep = True
    sweep.SweepTolerance = 0.01

    # Perform the sweep
    swept_breps = sweep.PerformSweep(curve, rectangle.ToNurbsCurve())

    # Assuming we want the first Brep if there are multiple
    return swept_breps[0]
    


def create_board(surface, base_plane, length, width, thickness, direction):
    if direction:
        firDirPlane = copy(base_plane)
        secDirPlane = copy(base_plane)
        secDirPlane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
    else:
        base_plane = copy(base_plane)
        base_plane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
        firDirPlane = copy(base_plane)
        secDirPlane = copy(base_plane)
        secDirPlane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)

    crvLength = create_contours(surface, firDirPlane, length)
    crvWidth = create_contours(surface, secDirPlane, width)

    crvCombine = []
    crvCombine.extend(crvLength)
    crvCombine.extend(crvWidth)

    panelGeoList = SurfaceSplit(surface, crvCombine)

        # create panel geometry
    panelOffsetList = []
    boardSeam = 2
    for panel in panelGeoList:
        # neg = OffsetCurve(panel, -boardSeam, base_plane, 1)
        # pos = OffsetCurve(panel, boardSeam, base_plane, 1)
        # if pos.GetLength() > neg.GetLength():
        #     offsetResult = neg
        # else:
        #     offsetResult = pos
        
        # panelOffsetSrf = BoundarySurfaces(offsetResult)
        panelOffsetList.append(Extrude(panel, base_plane.ZAxis*thickness))
    
    return panelOffsetList



def create_substructInfill(surface, base_plane, width, thickness, distance, direction):
    if direction:
        workPlane = copy(base_plane)

    else:
        base_plane = copy(base_plane)
        base_plane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
        workPlane = copy(base_plane)
    
    substructCrv = create_contours(surface, workPlane, distance)

    panelGeoList = SurfaceSplit(surface, substructCrv)


    # create panel geometry
    panelOffsetList = []
    for panel in panelGeoList:
        neg = OffsetCurve(panel, -width/2, base_plane, 1)
        pos = OffsetCurve(panel, width/2, base_plane, 1)
        if pos.GetLength() > neg.GetLength():
            offsetResult = neg
        else:
            offsetResult = pos
        
        panelOffsetSrf = BoundarySurfaces(offsetResult)
        panelOffsetList.append(Extrude(panelOffsetSrf, base_plane.ZAxis*thickness*0.8))

    # create beam
    beamGeo = []
    for crv in substructCrv:
        beamGeo.append(create_beam(crv, base_plane, width, thickness))

    return (panelOffsetList, beamGeo)



def create_paint(surface, base_plane, thickness):
    return Extrude(surface, base_plane.ZAxis*thickness)



def create_substruct(surface, base_plane, width, thickness, distance, direction):
    if direction:
        workPlane = copy(base_plane)

    else:
        base_plane = copy(base_plane)
        base_plane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
        workPlane = copy(base_plane)
    
    substructCrv = create_contours(surface, workPlane, distance)

    # create beam
    beamGeo = []
    for crv in substructCrv:
        beamGeo.append(create_beam(crv, base_plane, width, thickness))

    return beamGeo



def create_cladding(surface, base_plane, length, width, thickness, direction):
    if direction:
        firDirPlane = copy(base_plane)
        secDirPlane = copy(base_plane)
        secDirPlane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
    else:
        base_plane = copy(base_plane)
        base_plane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
        firDirPlane = copy(base_plane)
        secDirPlane = copy(base_plane)
        secDirPlane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)

    crvLength = create_contours(surface, firDirPlane, length)
    crvWidth = create_contours(surface, secDirPlane, width)

    crvCombine = []
    crvCombine.extend(crvLength)
    crvCombine.extend(crvWidth)

    panelGeoList = SurfaceSplit(surface, crvCombine)

        # create panel geometry
    panelOffsetList = []
    boardSeam = 2
    for panel in panelGeoList:
        # neg = OffsetCurve(panel, -boardSeam, base_plane, 1)
        # pos = OffsetCurve(panel, boardSeam, base_plane, 1)
        # if pos.GetLength() > neg.GetLength():
        #     offsetResult = neg
        # else:
        #     offsetResult = pos
        
        # panelOffsetSrf = BoundarySurfaces(offsetResult)
        panelOffsetList.append(Extrude(panel, base_plane.ZAxis*thickness))
    
    return panelOffsetList




basePlane = []
boardGeoList = []
substructInfillGeoList = []
paintGeoList = []
substructGeoList = []
claddingGeoList = []
layerTree = DataTree[object]()

for id, (srfList, matList) in enumerate(zip(surfaceList.Branches, materialList.Branches)):
    mat = matList[0]
    if id == 0:
        for srf in srfList:
            uvP = SurfaceClosestPoint(Area(srf)[1], srf)[1]
            frame = EvaluateSurface(srf, uvP)[4]
            basePlane.append(frame)
    
    allTypeGeo = []
    for srf_id, srf in enumerate(srfList):
        workPlane = basePlane[srf_id]
        matType = mat.materialType
        print(matType)
        if matType == "board":
            boardGeo = create_board(srf, workPlane, mat.length, mat.width, mat.thickness, mat.direction)
            boardGeoList.append(boardGeo)
            allTypeGeo.append(boardGeo)
            
        elif matType == "substructInfill":
            panelGeo, beamGeo = create_substructInfill(srf, workPlane, mat.width, mat.thickness, mat.distance, mat.direction)
            substructInfillGeoList.append(beamGeo)
            substructInfillGeoList.append(panelGeo)
            allTypeGeo.append(beamGeo)
            allTypeGeo.append(panelGeo)

        elif matType == "paint":
            paintGeo = create_paint(srf, workPlane, mat.thickness)
            paintGeoList.append([paintGeo])
            allTypeGeo.append([paintGeo])
            
        elif matType == "substruct":
            substructGeo = create_substruct(srf, workPlane, mat.width, mat.thickness, mat.distance, mat.direction)
            substructGeoList.append(substructGeo)
            allTypeGeo.append(substructGeo)

        elif matType == "cladding":
            claddingGeo = create_cladding(srf, workPlane, mat.length, mat.width, mat.thickness, mat.direction)
            claddingGeoList.append(claddingGeo)
            allTypeGeo.append(claddingGeo)
        
    path = GH_Path(array[int]([0,0,id]))
    layerTree.AddRange(allTypeGeo, path)
        


allTypeMaterial = layerTree

