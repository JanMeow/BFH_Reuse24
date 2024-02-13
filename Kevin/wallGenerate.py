import Rhino.Geometry as rg
from ghpythonlib.components import Area, SurfaceClosestPoint, EvaluateSurface, Contour, SurfaceSplit, Extrude, OffsetCurve, BoundarySurfaces
import ghpythonlib.treehelpers as th
import math
from copy import copy
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree
import System.Array as array


class CompoundMaterial:
    def __init__(self, materialList):
        self.materialList = materialList
        self.new_materialList = self.readMaterial(self.materialList)
        self.thicknessList = self.calculateThickness(self.new_materialList)

    
    def readMaterial(self, materialList):
        new_materialList = []
        for mat in materialList:
            if hasattr(mat, 'boardData'):
                new_materialList.append(mat.boardData)
            elif hasattr(mat, 'substructInfillData'):
                new_materialList.append(mat.substructInfillData)
            elif hasattr(mat, 'substructData'):
                new_materialList.append(mat.substructData)
            elif hasattr(mat, 'paintData'):
                new_materialList.append(mat.paintData)
            elif hasattr(mat, 'claddingData'):
                new_materialList.append(mat.claddingData)
        return new_materialList

    
    def calculateThickness(self, materialList):
        thicknessList = []
        for mat in materialList:
            thicknessList.append(mat.thickness)
        return thicknessList


class wallGenerate:
    def __init__(self, surfaceList, materialList, thicknessList):
        self.surfaceList = surfaceList
        self.materialList = materialList
        self.thicknessList = thicknessList

        basePlane = []
        boardGeoList = []
        substructInfillGeoList = []
        paintGeoList = []
        substructGeoList = []
        claddingGeoList = []
        layerTree = DataTree[object]()

        for id, (srfList, matList) in enumerate(zip(self.surfaceList, self.materialList)):
            mat = matList
            srfList = [srfList]
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
                    boardGeo = self.create_board(srf, workPlane, mat.length, mat.width, mat.thickness, mat.direction)
                    boardGeoList.append(boardGeo)
                    allTypeGeo.append(boardGeo)
                    
                elif matType == "substructInfill":
                    panelGeo, beamGeo = self.create_substructInfill(srf, workPlane, mat.width, mat.thickness, mat.distance, mat.direction)
                    substructInfillGeoList.append(beamGeo)
                    substructInfillGeoList.append(panelGeo)
                    allTypeGeo.append(beamGeo)
                    allTypeGeo.append(panelGeo)

                elif matType == "paint":
                    paintGeo = self.create_paint(srf, workPlane, mat.thickness)
                    paintGeoList.append([paintGeo])
                    allTypeGeo.append([paintGeo])
                    
                elif matType == "substruct":
                    substructGeo = self.create_substruct(srf, workPlane, mat.width, mat.thickness, mat.distance, mat.direction)
                    substructGeoList.append(substructGeo)
                    allTypeGeo.append(substructGeo)

                elif matType == "cladding":
                    claddingGeo = self.create_cladding(srf, workPlane, mat.length, mat.width, mat.thickness, mat.direction)
                    claddingGeoList.append(claddingGeo)
                    allTypeGeo.append(claddingGeo)
                
            path = GH_Path(array[int]([0,0,id]))
            layerTree.AddRange(allTypeGeo, path)
                
        self.allTypeMaterial = layerTree


    def create_contours(self, surface, base_plane, interval):
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
        self.check = contours
        
        # Trim contours
        # for contour in contours:
        #     intersection_events = rg.Intersect.Intersection.CurveCurve(contour, boundary, 0.01, 0.01)
        #     if intersection_events:
        #         intersection_params = [event.ParameterA for event in intersection_events]
        #         segments = contour.Split(intersection_params)
        #         for segment in segments:
        #             trimmed_contours.append(segment)

        return contours


    def create_beam(self, curve, base_plane, width, height):
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
        


    def create_board(self, surface, base_plane, length, width, thickness, direction):
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

        crvLength = self.create_contours(surface, firDirPlane, length)
        crvWidth = self.create_contours(surface, secDirPlane, width)

        crvCombine = []
        crvCombine.extend(crvLength)
        crvCombine.extend(crvWidth)


        panelGeoList = SurfaceSplit(surface, crvCombine)

            # create panel geometry
        panelOffsetList = []
        boardSeam = 2
        for panel in panelGeoList:
            panelOffsetList.append(Extrude(panel, base_plane.ZAxis*thickness))
        
        return panelOffsetList



    def create_substructInfill(self, surface, base_plane, width, thickness, distance, direction):
        if direction:
            workPlane = copy(base_plane)

        else:
            base_plane = copy(base_plane)
            base_plane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
            workPlane = copy(base_plane)
        
        substructCrv = self.create_contours(surface, workPlane, distance)

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
            beamGeo.append(self.create_beam(crv, base_plane, width, thickness))

        return (panelOffsetList, beamGeo)


    def create_paint(self, surface, base_plane, thickness):
        return Extrude(surface, base_plane.ZAxis*thickness)


    def create_substruct(self, surface, base_plane, width, thickness, distance, direction):
        if direction:
            workPlane = copy(base_plane)

        else:
            base_plane = copy(base_plane)
            base_plane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
            workPlane = copy(base_plane)
        
        substructCrv = self.create_contours(surface, workPlane, distance)

        # create beam
        beamGeo = []
        for crv in substructCrv:
            beamGeo.append(self.create_beam(crv, base_plane, width, thickness))

        return beamGeo


    def create_cladding(self, surface, base_plane, length, width, thickness, direction):
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

        crvLength = self.create_contours(surface, firDirPlane, length)
        crvWidth = self.create_contours(surface, secDirPlane, width)

        crvCombine = []
        crvCombine.extend(crvLength)
        crvCombine.extend(crvWidth)

        panelGeoList = SurfaceSplit(surface, crvCombine)

            # create panel geometry
        panelOffsetList = []
        boardSeam = 2
        for panel in panelGeoList:
            panelOffsetList.append(Extrude(panel, base_plane.ZAxis*thickness))
        
        return panelOffsetList



def offset_brep(brep, distances, tolerance=0.01):
    all_offset_breps = []
    for distance in distances:
        offset_breps = rg.Brep.CreateOffsetBrep(brep, distance, solid=False, extend=False, tolerance=tolerance)
        if offset_breps:
            all_offset_breps.append(offset_breps[0][0])
        else:
            print("Offset operation failed for distance .")
            all_offset_breps.append(None)
    return all_offset_breps



compoundMaterialObj = CompoundMaterial(material_collection)
materialList = compoundMaterialObj.new_materialList
material_thickness = compoundMaterialObj.thicknessList

offsetList = []
total = 0
for num in material_thickness:
    total += num
    offsetList.append(total)


offsetList = offsetList[:-1]
offsetList.insert(0,0)

offsetted_surface = offset_brep(wallSurface, offsetList)

wallObj = wallGenerate(offsetted_surface, materialList, material_thickness)
allTypeMaterial = wallObj.allTypeMaterial
check = wallObj.check
