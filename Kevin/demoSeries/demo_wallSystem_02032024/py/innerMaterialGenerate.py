import Rhino.Geometry as rg
from ghpythonlib.components import Area, SurfaceClosestPoint, EvaluateSurface, SurfaceSplit, Extrude, OffsetCurve, BoundarySurfaces, TrimwithRegions, JoinCurves, RegionDifference, AlignPlane, EvaluateLength, LineSDL, Project, RegionUnion, ProjectPoint, PullPoint
import ghpythonlib.treehelpers as th
import math
from copy import copy, deepcopy
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree
import System.Array as array
from itertools import chain
import random
from collections import Counter

import sys
import os

class InnerMaterialGenerate:
    def __init__(self, DB, surfaceList, materialList, thicknessList, moduleDistance=180, wallFrame=None, claddingDirection=None, moduleCurve=[], moduleCrvDist=10, ifModule=False):
        print("class of innerMaterialGenerate is running")
        self.boardDB = DB["boardDB"]
        self.surfaceList = surfaceList
        self.materialList = materialList
        self.thicknessList = thicknessList
        self.moduleDistance = moduleDistance
        self.wallFrame = wallFrame
        self.claddingDirection = claddingDirection
        self.moduleCurve = moduleCurve
        self.moduleCrvDist = moduleCrvDist
        self.ifModule = ifModule


        basePlane = [self.wallFrame]
        boardGeoList = []
        substructInfillGeoList = []
        paintGeoList = []
        substructGeoList = []
        claddingGeoList = []
        self.materialInfoDict = {}
        layerTree = DataTree[object]()
        layerTreeModule = DataTree[object]()

        self.checkGeo = []

        for self.layerId, (srfList, matList) in enumerate(zip(self.surfaceList, self.materialList)):
            mat = matList
            srfList = [srfList]
            
            allTypeGeo = []
            for entireSrf_id, entireSrf in enumerate(srfList):
                workPlane = basePlane[entireSrf_id]
                matType = mat.materialType
                

                # Splite surface into several module
                if ifModule == True:
                    if len(self.moduleCurve) != 0:
                        srf_List = self.create_module_byCurve(entireSrf, workPlane, self.moduleCurve, self.moduleCrvDist)
                    else:
                        srf_List = self.create_module_withDistance(entireSrf, workPlane, self.moduleDistance)
                else:
                    srf_List = [entireSrf]


                if self.layerId not in self.materialInfoDict:
                    self.materialInfoDict[self.layerId] = {}

                for self.module_id, srf in enumerate(srf_List):
                    if self.module_id not in self.materialInfoDict[self.layerId]:
                        self.materialInfoDict[self.layerId][self.module_id] = {}

                    allTypeGeoModule = []
                    if matType == "board":
                        # if mat.searchDB:
                        #     useWidth, useLength, useDepth, useQuantity, useId, useMatAttr = self.find_board(self.boardDB, mat.length, mat.width, mat.thickness)
                        #     print("==============")
                        #     print(useDepth)
                        # else:
                        useWidth, useLength, useDepth, useMatAttr, useDirect, usePt = mat.width, mat.length, mat.thickness, mat.attrList, mat.direction, mat.pt

                        # print(useMatAttr.uuid)
                        boardGeo = self.create_board(srf, workPlane, useLength, useWidth, useDepth, useDirect, useMatAttr, usePt)
                        boardGeoList.append(boardGeo)
                        allTypeGeo.append(boardGeo)
                        allTypeGeoModule.append(boardGeo)
                        
                    elif matType == "substructInfill":
                        useWidth, useDepth, useMatAttr, useDirect, useDist = mat.width, mat.thickness, mat.attrList, mat.direction, mat.distance

                        panelGeo, beamGeo = self.create_substructInfill(srf, workPlane, useWidth, useDepth, useDist, useDirect, useMatAttr)
                        substructInfillGeoList.append(beamGeo)
                        substructInfillGeoList.append(panelGeo)
                        allTypeGeo.append(beamGeo)
                        allTypeGeo.append(panelGeo)
                        li = []
                        li.extend(beamGeo)
                        li.extend(panelGeo)
                        allTypeGeoModule.append(li)

                    elif matType == "paint":
                        paintGeo = self.create_paint(srf, workPlane, mat.thickness, mat.attrList)
                        paintGeoList.append([paintGeo])
                        allTypeGeo.append([paintGeo])
                        allTypeGeoModule.append([paintGeo])
                        
                    elif matType == "substruct":
                        useWidth, useDepth, useMatAttr, useDirect, useDist = mat.width, mat.thickness, mat.attrList, mat.direction, mat.distance

                        substructGeo = self.create_substruct(srf, workPlane, useWidth, useDepth, useDist, useDirect, useMatAttr)
                        substructGeoList.append(substructGeo)
                        allTypeGeo.append(substructGeo)
                        allTypeGeoModule.append(substructGeo)
                    
                    path_module = GH_Path(array[int]([self.layerId, self.module_id]))
                    layerTreeModule.AddRange(allTypeGeoModule, path_module)
                    
                
            path = GH_Path(array[int]([0,0,self.layerId]))
            layerTree.AddRange(allTypeGeo, path)
                
        self.allTypeMaterial = layerTree
        self.allTypeMaterialModule = layerTreeModule
        

    def create_module_byCurve(self, surface, base_plane, curves, crvDist):
        newCurve = []
        midPtList = []
        for crv in curves:
            midPtList.append(crv.PointAtNormalizedLength(0.5))
            crv = crv.Extend(rg.CurveEnd.Start, 10000, 0)
            crv = crv.Extend(rg.CurveEnd.End, 10000, 0)
            crv1 = crv.Offset(base_plane, crvDist/2, 0.1, 0)[0]
            crv2 = crv.Offset(base_plane, -crvDist/2, 0.1, 0)[0]
            newCurve.append(crv1)
            newCurve.append(crv2)

        projectMidPt = ProjectPoint(midPtList, base_plane.ZAxis, surface)[0]
        projectCurves = Project(newCurve, surface, base_plane.ZAxis)
        surfaceList = SurfaceSplit(surface, projectCurves)
        # print(surfaceList)
        surfaceList = self.sortSurface(surfaceList, base_plane)

        chosenSrf = []
        for srf in surfaceList:
            delete = False
            for midPt in projectMidPt:
                closPt, closDist = PullPoint(midPt, srf)
                if closDist < 0.1: ################################################################################
                    delete = True
            
            if not delete:
                chosenSrf.append(srf)

        return chosenSrf


    def create_module_withDistance(self, surface, base_plane, distance):
        base_plane = copy(base_plane)
        
        if self.claddingDirection:
            base_plane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
        curves, _ = self.create_contours(surface, base_plane, distance)
        surfaceList = SurfaceSplit(surface, curves)
        surfaceList = self.sortSurface(surfaceList, base_plane)

        return surfaceList


    def sortSurface(self, srfList, sortPlane):
            # Calculate the center point of each surface's bounding box
            centers = [srf.GetBoundingBox(True).Center for srf in srfList]
            
            # Project these center points onto the sortPlane's Y-axis and calculate distance from the plane's origin
            distances = [sortPlane.YAxis * (center - sortPlane.Origin) for center in centers]
            
            # Sort the surfaces based on these distances
            sortedSurfaces = [srf for _, srf in sorted(zip(distances, srfList))]
            
            return sortedSurfaces


    def create_contours(self, surface, base_plane, interval, pt=None):
        base_plane = copy(base_plane)
        base_plane.Rotate(math.pi/2, base_plane.XAxis, base_plane.Origin)
        base_plane.Rotate(math.pi/10, base_plane.ZAxis, base_plane.Origin) # Maybe this line can be removed

        contours = []
        # trimmed_contours = []

        # Get the bounding box of the surface in the plane's coordinate system
        bbox = surface.GetBoundingBox(base_plane)

        # Start and end values for contouring in the direction of the plane's normal
        start = bbox.Min.Z
        end = bbox.Max.Z
        
        originPlane = rg.Plane(base_plane)
        originPlane.Translate(base_plane.Normal * start)

        if pt == None:
            offsetDist = 0
        else:
            offsetDist = originPlane.DistanceTo(pt)%interval
        

        z = start + offsetDist
        while z <= end:
            # Create a plane parallel to the base plane at height z
            contour_plane = rg.Plane(base_plane)
            contour_plane.Translate(base_plane.Normal * z)


            # Generate the contour
            contour_curves = rg.Brep.CreateContourCurves(surface, contour_plane)
            contours.extend(contour_curves)
            
            z += interval

        total_length = 0
        for crv in contours:
            total_length += crv.GetLength()
            # print(crv.GetLength())

        return (contours, int(total_length))


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
        

    def create_board(self, surface, base_plane, length, width, thickness, direction, matAttr, oriPt):
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

        crvLength, _ = self.create_contours(surface, firDirPlane, length, oriPt)
        crvWidth, _ = self.create_contours(surface, secDirPlane, width, oriPt)

        crvCombine = []
        crvCombine.extend(crvLength)
        crvCombine.extend(crvWidth)

        panelGeoList = SurfaceSplit(surface, crvCombine)

        # create panel geometry
        panelOffsetList = []
        boardSeam = 2
        # print("=====================")
        # print(panelGeoList)
        for panel in panelGeoList:
            panelOffsetList.append(Extrude(panel, base_plane.ZAxis*thickness))

        # Record Material using information.
        boardArea = length*width
        cuttedPiece = 0
        for panel in panelGeoList:
            area_properties = rg.AreaMassProperties.Compute(panel)
            if area_properties is not None:
                panelArea = area_properties.Area
                if (boardArea - panelArea) > 10: #############################
                    cuttedPiece += 1

        usedPiece = len(panelGeoList)
        self.materialInfoDict[self.layerId][self.module_id]["availableQuantity"] = matAttr.anzahl
        self.materialInfoDict[self.layerId][self.module_id]["materialType"] = "board"
        self.materialInfoDict[self.layerId][self.module_id]["usedPiece"] = usedPiece
        self.materialInfoDict[self.layerId][self.module_id]["cuttedPiece"] = cuttedPiece
        self.materialInfoDict[self.layerId][self.module_id]["completedPiece"] = usedPiece - cuttedPiece
        self.materialInfoDict[self.layerId][self.module_id]["info"] = matAttr
        
        return panelOffsetList

    """
    def find_board(self, searchDB, searchLength, searchWidth, searchDepth):
        widthDB = []
        lengthDB = []
        depthDB = []
        quantityDB = []
        for board in searchDB:
            w, l, d = board.breite, board.hoehe, board.tiefe
            widthDB.append(w)
            lengthDB.append(l)
            depthDB.append(d)
            quantityDB.append(board.anzahl)

        boardList = []
        for id, (w, l, d, q, obj) in enumerate(zip(widthDB, lengthDB, depthDB, quantityDB, searchDB)):
            idName = "board_" + str(id)
            boardList.append((w,l,d,q,idName,obj))

        euclideanDistList = []
        for w, l, d, q, id, obj in boardList:
            euclideanDist = abs(searchWidth-w)**2 + abs(searchLength-l)**2 + abs(searchDepth-d)**2
            euclideanDistList.append(euclideanDist)

        # Pair each element of first_list with the corresponding element in second_list
        paired_list = zip(boardList, euclideanDistList)

        # Sort the pairs based on the elements of second_list
        sorted_pairs = sorted(paired_list, key=lambda x: x[1])

        # Extract the sorted elements of first_list
        sorted_list = [element for element, _ in sorted_pairs]
        tileData = sorted_list[0]

        useWidth, useLength, useDepth, useQuantity, useId, useObjAttr = tileData

        return (useWidth, useLength, useDepth, useQuantity, useId, useObjAttr)
    """


    def create_substructInfill(self, surface, base_plane, width, thickness, distance, direction, matAttr):
        def offset_surface_inner(surface, plane, distance, tolerance=0.01):
            inner_distance = -abs(distance)
            
            # Offset the surface
            # print(type(surface))
            offset_surface = surface.Offset(100, tolerance)
            
            if offset_surface:
                # Convert the offset surface to Brep
                return offset_surface
            else:
                print("Offset operation failed.")
                return None

        if direction:
            workPlane = copy(base_plane)

        else:
            base_plane = copy(base_plane)
            base_plane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
            workPlane = copy(base_plane)
        
        substructCrv, substructureLength = self.create_contours(surface, workPlane, distance)

        panelGeoList = SurfaceSplit(surface, substructCrv)

        if isinstance(panelGeoList, list):
            pass
        else:
            panelGeoList = [panelGeoList]

        # create panel geometry
        panelOffsetList = []
        totalArea = 0
        for panel in panelGeoList:
            # Assuming 'brep' is your Brep object and it's essentially a single surface
            if panel.Faces.Count == 1:
                surface = panel.Faces[0]
            else:
                print("The Brep contains multiple faces. Please specify which face to offset.")
                # For this example, let's proceed with the first face
                surface = panel.Faces[0]
            
            # panelOffsetSrf = offset_surface_inner(surface, base_plane, width/2)
            panelOffsetSrf = panel

            panelOffsetList.append(Extrude(panelOffsetSrf, base_plane.ZAxis*thickness*0.8))

            area_properties = rg.AreaMassProperties.Compute(panelOffsetSrf)
            if area_properties is not None:
                panelArea = area_properties.Area
                totalArea += panelArea

        # create beam
        beamGeo = []
        for crv in substructCrv:
            beamGeo.append(self.create_beam(crv, base_plane, width, thickness))
        
        self.materialInfoDict[self.layerId][self.module_id]["availableQuantity"] = matAttr.anzahl
        self.materialInfoDict[self.layerId][self.module_id]["materialType"] = "substructInfill"
        self.materialInfoDict[self.layerId][self.module_id]["usedLength"] = substructureLength
        self.materialInfoDict[self.layerId][self.module_id]["usedArea"] = int(totalArea)
        self.materialInfoDict[self.layerId][self.module_id]["info"] = matAttr

        return (panelOffsetList, beamGeo)


    def create_paint(self, surface, base_plane, thickness, matAttr):
        area_properties = rg.AreaMassProperties.Compute(surface)
        if area_properties is not None:
            panelArea = area_properties.Area

        self.materialInfoDict[self.layerId][self.module_id]["availableQuantity"] = matAttr.anzahl
        self.materialInfoDict[self.layerId][self.module_id]["materialType"] = "paint"
        self.materialInfoDict[self.layerId][self.module_id]["usedArea"] = None
        self.materialInfoDict[self.layerId][self.module_id]["usedArea"] = int(panelArea)
        self.materialInfoDict[self.layerId][self.module_id]["info"] = matAttr

        return Extrude(surface, base_plane.ZAxis*thickness)


    def create_substruct(self, surface, base_plane, width, thickness, distance, direction, matAttr):
        if direction:
            workPlane = copy(base_plane)

        else:
            base_plane = copy(base_plane)
            base_plane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
            workPlane = copy(base_plane)
        
        substructCrv, substructureLength = self.create_contours(surface, workPlane, distance)

        # create beam
        beamGeo = []
        for crv in substructCrv:
            beamGeo.append(self.create_beam(crv, base_plane, width, thickness))
        
        # self.materialInfoList.append((self.module_id, "substruct", substructureLength))
        self.materialInfoDict[self.layerId][self.module_id]["availableQuantity"] = matAttr.anzahl
        self.materialInfoDict[self.layerId][self.module_id]["materialType"] = "substruct"
        self.materialInfoDict[self.layerId][self.module_id]["usedLength"] = substructureLength
        self.materialInfoDict[self.layerId][self.module_id]["info"] = matAttr

        return beamGeo

