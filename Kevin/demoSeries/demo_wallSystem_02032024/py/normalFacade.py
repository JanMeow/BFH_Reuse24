import Rhino.Geometry as rg
from ghpythonlib.components import Area, SurfaceClosestPoint, EvaluateSurface, SurfaceSplit, Extrude, OffsetCurve, BoundarySurfaces, TrimwithRegions, JoinCurves, RegionDifference, AlignPlane, EvaluateLength, LineSDL, Project, RegionUnion, ProjectPoint, PullPoint, BrepEdges, Explode, CurveXCurve
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


path = os.path.abspath(__file__)
parentdir = os.path.dirname(path)
grandparentdir = os.path.dirname(parentdir)
dire = os.path.join(grandparentdir, 'py')
if dire not in sys.path:
    sys.path.append(dire)

import innerMaterialGenerate
import compoundMaterial
reload(innerMaterialGenerate)
reload(compoundMaterial)
from innerMaterialGenerate import InnerMaterialGenerate
from compoundMaterial import CompoundMaterial


dbList = ["bauteil_obergruppe", "bauteil_gruner", "uuid", "kosten", "zustand", "material", "ref_gebauede_geschoss", "breite", "hoehe", "tiefe", "flaeche", "masse", "anzahl", "foto1", "foto2", "co2", "url"]

class NormalFacade:
    """
    A class to generate cladding layouts based on various parameters such as window and wall geometries,
    cladding dimensions, and overlap specifications.

    Attributes:
        windowDB: Database of window.
        claddingDB: Database of cladding.
        wallGeo: Geometry of the wall to be clad.
        windowGeo: Geometry of the windows in the wall.
        claddingWidth: The width of the cladding material that users input.
        claddingLength: The length of the cladding material that users input.
        kindNum: How many cldding type users want.
        wWeight: Weight parameter for width consideration.
        lWeight: Weight parameter for length consideration.
        horizontalOverlap: Overlap between claddings horizontally.
        verticalOverlap: Overlap between claddings vertically.
        horizontalAngle: The angle of the cladding orientation horizontally.
        verticalAngle: The angle of the cladding orientation vertically.
    """

    def __init__(self, DB, wallGeo, windowGeo, doorGeo, claddingDirection=True, offsetDist=0, claddingMaterial = None):
        """
        Initializes the GenerateCladding class with all the necessary attributes for cladding generation.
        """
        print("class of generateCladding is running")
        global initial_data
        self.DB = DB
        self.windowDB = DB["windowDB"]
        self.doorDB = DB["doorDB"]
        self.claddingDB = DB["tileDB"]
        self.wallGeo = wallGeo
        self.windowGeo = windowGeo
        self.doorGeo = doorGeo
        self.offsetDist = offsetDist
        self.claddingDirection = claddingDirection
        self.claddingMaterial = claddingMaterial

        # NormalFacade don't need tile grid system, thus I set width and length as 1
        width = [1]
        length = [1]

        # build mapping for width and length
        self.number_mapping = {}
        for w, l in zip(width, length):
            self.number_mapping[l] = w

        # Decide grid distance based on the minimum width of the tile
        paired_list = zip(length, width)
        sorted_list = sorted(paired_list, key=lambda x: x[1])
        self.minTileWidth = sorted_list[0][1]
        self.minTileLength = sorted_list[0][0]
        self.gridDist = self.minTileWidth
        #print(self.minTileWidth)
        #print(self.minTileLength)

        self.claddingGeo = self.offset_brep(self.wallGeo, [self.offsetDist], self.wallGeo.Faces[0].FrameAt(0.5, 0.5)[1])[0]

        # Generate the column line, wall frame, and cut direction for the cladding
        self.columnLine, self.wallFrame, self.cutDirect = self.generateTileColumn(self.claddingGeo, self.gridDist)


##################################################################################
        compoundMaterialObj = CompoundMaterial(self.claddingMaterial, self.DB)
        materialList = compoundMaterialObj.new_materialList
        material_thickness = compoundMaterialObj.thicknessList

        offsetList = []
        total = 0
        for num in material_thickness:
            total += num
            offsetList.append(total)

        self.normalOffsetDist = sum(material_thickness)
        offsetList = offsetList[:-1]
        offsetList.insert(0,0)

        outterMaterial = materialList[len(materialList)-1]

        self.ruler = self.createRuler(self.claddingGeo, self.wallFrame, outterMaterial.length, outterMaterial.width, outterMaterial.direction, outterMaterial.pt)
    
##################################################################################

  
        if len(self.windowGeo)!=0 and isinstance(self.windowGeo[0], rg.Brep):
            # Get window indices and geometries from DB that match users' dimension of geometry for window.
            chosenWindowId, self.chosenWindowGeo, self.chosenWindowAttr = self.findWindow(self.windowDB, self.windowGeo, self.gridDist)
            # Orient window and door onto grid system
            self.orientedWindowGeoList, self.finalWindowPlaneList, self.windowForFinalList = self.orientWindow(self.columnLine, self.windowGeo, self.chosenWindowGeo, self.claddingGeo)
        else:
            self.chosenWindowGeo, self.chosenWindowAttr = self.buildWindow(self.windowGeo)
            # Orient window and door onto grid system
            self.orientedWindowGeoList, self.finalWindowPlaneList, self.windowForFinalList = self.orientWindow(self.columnLine, self.windowGeo, self.chosenWindowGeo, self.claddingGeo)

        if len(self.doorGeo)!=0 and isinstance(self.doorGeo[0], rg.Brep):
            # Get window indices and geometries from DB that match users' dimension of geometry for window.
            chosenDoorId, self.chosenDoorGeo, self.chosenDoorAttr = self.findDoor(self.doorDB, self.doorGeo, self.gridDist)
            # Orient window and door onto grid system
            self.orientedDoorGeoList, self.finalDoorPlaneList, self.doorForFinalList = self.orientDoor(self.columnLine, self.doorGeo, self.chosenDoorGeo, self.claddingGeo)
        else:
            self.chosenDoorGeo, self.chosenDoorAttr = self.buildDoor(self.doorGeo)
            # Orient window and door onto grid system
            self.orientedDoorGeoList, self.finalDoorPlaneList, self.doorForFinalList = self.orientDoor(self.columnLine, self.doorGeo, self.chosenDoorGeo, self.claddingGeo)


        



        # Generate basic wall geometry for inner material
        self.wallForInnerGeo = self.calculateInnerGeo(self.windowForFinalList, self.doorForFinalList)

        self.wallForFacadeGeo = self.calculateFacadeGeo(self.windowForFinalList, self.doorForFinalList)

        # Calculate innerMaterial Part
        offsetted_surface = self.offset_brep(self.wallForFacadeGeo, offsetList, self.wallFrame)

        moduleDistance = 200
        moduleCurve = []
        facadeObj = InnerMaterialGenerate(DB, offsetted_surface, materialList, material_thickness, moduleDistance, self.wallFrame, claddingDirection, moduleCurve, 10, False)
        self.facadeMaterial = facadeObj.allTypeMaterial
        self.claddingInfo = facadeObj.materialInfoDict
        # checkGeo = wallObj.checkGeo
        # allTypeMaterialModule = facadeObj.allTypeMaterialModule


    def createRuler(self, surface, base_plane, length, width, direction, oriPt):
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
        
        crvLength, _ = InnerMaterialGenerate.create_contours(surface, firDirPlane, length, oriPt)
        crvWidth, _ = InnerMaterialGenerate.create_contours(surface, secDirPlane, width, oriPt)
        crvLength = [crv.ToNurbsCurve() for crv in crvLength]
        crvWidth = [crv.ToNurbsCurve() for crv in crvWidth]

        crvList = BrepEdges(surface)[0]
        crvList = [crv.ToNurbsCurve() for crv in crvList]

        crvCombine = []
        crvCombine.extend(crvLength)
        crvCombine.extend(crvWidth)
        crvCombine.extend(crvList)

        return crvCombine


    def alignSystem(self, windowGeo, grid, toler, basePlane):
        def findMoveDist(points, checkLinesDict, basePlane, direction):
            dir = {"verti":True, "hori":False}
            moveDir = dir[direction]
            checkLines = checkLinesDict[direction]

            xform = rg.Transform.ChangeBasis(rg.Plane.WorldXY, basePlane)
            newPts = []
            for pt in points:
                newPt = deepcopy(pt)
                newPt.Transform(xform)
                newPts.append(newPt)
            
            if moveDir:
                newPts = sorted(newPts, key=lambda pt: pt.Y)
            else:
                newPts = sorted(newPts, key=lambda pt: pt.X)

            xform_back = rg.Transform.ChangeBasis(basePlane, rg.Plane.WorldXY)
            for pt in newPts:
                pt.Transform(xform_back)

            # firPts: upper & right
            # secPt: button & left
            firPts, secPts = newPts[2:], newPts[:2]

            crvDir = basePlane.YAxis if moveDir else basePlane.XAxis
            see = []
            wholePair_facade = []
            for pt in newPts:
                firMoveTrace = LineSDL(pt, crvDir, toler).ToNurbsCurve()
                secMoveTrace = LineSDL(pt, -crvDir, toler).ToNurbsCurve()
                see.append(firMoveTrace)

                for crv in checkLines['facade']:
                    firCutPt = CurveXCurve(crv.ToNurbsCurve(), firMoveTrace)[0]
                    secCutPt = CurveXCurve(crv.ToNurbsCurve(), secMoveTrace)[0]
                    if firCutPt:
                        wholePair_facade.append((pt,firCutPt))
                    if secCutPt:
                        wholePair_facade.append((pt,secCutPt))
            
            if len(wholePair_facade)!=0:
                wholePair_facade = sorted(wholePair_facade, key=lambda pair: pair[0].DistanceTo(pair[1]))
                closestPair = wholePair_facade[0]
                
                return (rg.Vector3d(closestPair[1]-closestPair[0]), True)

            else:
                return (rg.Vector3d(0,0,0), True)

        # Whole lines involved in this system, having opening lines and grid lines
        checkLinesFacade = grid
        checkLinesOpening = []

        pt_rect = []
        for geo in windowGeo:
            if isinstance(geo, rg.Rectangle3d):
                lines, vertics = Explode(geo, True)
                pt_rect.append((vertics[:-1], geo))
                checkLinesOpening.extend(lines)
            elif isinstance(geo, rg.Brep):
                lines = BrepEdges(geo)[0]
                checkLinesOpening.extend(lines)
                pt_rect.append(([vertex.Location for vertex in geo.Vertices], geo))

        horiVec, vertiVec = basePlane.XAxis, basePlane.YAxis
        # print("horiVec", horiVec)
        horiLinesFacade = []
        vertiLinesFacade = []
        for crv in checkLinesFacade:
            vecCrv = crv.PointAtEnd - crv.PointAtStart
            if sum(rg.Vector3d.CrossProduct(horiVec,vecCrv))<1:
                horiLinesFacade.append(crv)
            else:
                vertiLinesFacade.append(crv)

        horiLinesOpening = {}
        vertiLinesOpening = {}
        for openId, crv in enumerate(checkLinesOpening):
            vecCrv = crv.PointAtEnd - crv.PointAtStart
            if rg.Vector3d.CrossProduct(horiVec,vecCrv).IsZero:
                horiLinesOpening[openId] = crv
            else:
                vertiLinesOpening[openId] = crv

        wholeLinesDict = {"hori":{"facade":vertiLinesFacade, "opening":vertiLinesOpening}, "verti":{"facade":horiLinesFacade, "opening":horiLinesOpening}}
        
        finalVec = []
        for pts, _ in pt_rect:
            horiVec, fixedBool = findMoveDist(pts, wholeLinesDict, basePlane, 'hori')
            vertiVec, fixedBool = findMoveDist(pts, wholeLinesDict, basePlane, 'verti')
            crossVec = rg.Vector3d.Add(horiVec, vertiVec)

            finalVec.append(crossVec)

        return finalVec


        
    def compare(self, name, data):
        if not isinstance(data, list):
            data = [data]

        if name not in initial_data:
            initial_data[name] = data
            return True
        else:
            if Counter(initial_data[name]) == Counter(data):
                return False
            else:
                initial_data[name] = data
                return True


    def alignToZ(self, targetPlane):
        finalPlane = copy(targetPlane)
        finalPlane = AlignPlane(finalPlane, rg.Vector3d.ZAxis)[0]
        finalPlane.Rotate(-math.pi/2, finalPlane.ZAxis, finalPlane.Origin)

        return finalPlane


    def offset_brep(self, brep, distances, plane, tolerance=0.01):
        if isinstance(brep, list):
            brep = brep[0]

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


    def replace_with_zeros(self, nested_list):
        # Check if the current element is a list
        if isinstance(nested_list, list):
            # If it is, recursively apply the function to each element of the list
            return [self.replace_with_zeros(item) for item in nested_list]
        else:
            # If the current element is not a list, replace it with zero
            return []


    def customizedCladding(self, tile_list):
        width = []
        length = []
        longList = []
        for tileClass in tile_list:
            w, l, q = tileClass.tileData.width, tileClass.tileData.height, int(tileClass.tileData.quantity)
            width.append(w)
            length.append(l)
            longList.extend([l]*q)
        
        return (width, length, longList)


    def findWindow(self, windowDB, userWindowGeoList, gridWidth):
        """
        Identifies the best matching window dimensions from a database based on user-specified geometries,
        considering a given tolerance and grid width.

        Parameters:
            windowDB: A database or list of window objects with width and height attributes.
            userWindowGeoList: A list of user-specified window geometries to match against the database.
            gridWidth: The width of the grid to consider for matching.
            tolerance: The tolerance within which a match is considered acceptable.

        Returns:
            A list of indices corresponding to the chosen windows from the database.
            A list of geometries of window.
        """

        def _sortPoints(points, surf):
            """
            Sorts points based on their spatial relation to a reference surface, categorizing them into quadrants
            relative to the surface's frame and returning them in a specific order along with the surface frame.

            Parameters:
                points: A list of points to sort.
                surf: The reference surface or brep for sorting points.

            Returns:
                A tuple containing the sorted points in specific quadrants and the updated surface frame.
            """

            if isinstance(surf, rg.Surface) or isinstance(surf, rg.Brep):
                # Ensure surf is a Surface for the operations (if Brep, use its faces)
                if isinstance(surf, rg.Brep):
                    surf = surf.Faces[0]

                # 1. Calculate the Area Centroid of the Surface
                area_properties = rg.AreaMassProperties.Compute(surf)
                if area_properties is not None:
                    centroid = area_properties.Centroid

                    # 2. Find the Closest Point on the Surface to the Centroid
                    success, uvPU, uvPV = surf.ClosestPoint(centroid)
                    if success:
                        # 3. Evaluate the Surface at the UV Parameters
                        success, surf_Frame = surf.FrameAt(uvPU, uvPV)
                        surf_Frame = self.alignToZ(surf_Frame)
                        # if success:
                            # surf_Frame now contains the frame (plane) at the closest point
                            # Do something with surf_Frame, e.g., access its origin or its normal
                            # frame_origin = surf_Frame.Origin
                            # frame_normal = surf_Frame.Normal
                            # You can now use frame_origin and frame_normal as needed
                        # else:
                        #     print("Failed to evaluate the surface frame.")
                    else:
                        print("Failed to find the closest point on the surface.")
                else:
                    print("Failed to compute area properties.")
            else:
                print("The input 'surf' is not a valid surface or brep.")


            rTo = rg.Transform.ChangeBasis(rg.Plane.WorldXY, surf_Frame)
            rFro = rg.Transform.ChangeBasis(surf_Frame, rg.Plane.WorldXY)
            
            for pt in points:
                pt.Transform(rTo)
                if pt.X>0 and pt.Y>0:
                    pt.Transform(rFro)
                    pointHighFirst = pt
                elif pt.X<0 and pt.Y>0:
                    pt.Transform(rFro)
                    pointHighSecond = pt
                elif pt.X>0 and pt.Y<0:
                    pt.Transform(rFro)
                    pointLowFirst = pt
                elif pt.X<0 and pt.Y<0:
                    pt.Transform(rFro)
                    pointLowSecond = pt
            surf_Frame.Rotate(math.pi/2, surf_Frame.ZAxis)
            return (pointLowSecond, pointHighSecond, pointLowFirst, pointHighFirst, surf_Frame)
        
        DBwidthList = [win.geometry.Width for win in windowDB]
        DBheightList = [win.geometry.Height for win in windowDB]
        uList = []
        vList = []
        for windowGeo in userWindowGeoList:
            ptList = [vertex.Location for vertex in windowGeo.Vertices]
            ptList = _sortPoints(ptList, windowGeo)
            width = ptList[0].DistanceTo(ptList[1])
            height = ptList[0].DistanceTo(ptList[2])
            u, v = height, width
            uList.append(u)
            vList.append(v)

        chosenId = []
        chosenWindowGeo = []
        chosenWindowAttr = []
        for u,v in zip(uList, vList):
            minId = None
            minDist = float('inf')
            for id, (width, height) in enumerate(zip(DBwidthList, DBheightList)):
                if self.claddingDirection:
                    euclideanDist = (width-u)**2 + (height-v)**2 + ((width)%gridWidth)**3
                else:
                    euclideanDist = (width-u)**2 + (height-v)**2 + ((height)%gridWidth)**3
                if euclideanDist < minDist:
                    minId = id
                    minDist = euclideanDist
            chosenId.append(minId)
            chosenWindowGeo.append(windowDB[minId].geometry)
            chosenWindowAttr.append(windowDB[minId].attr)
        
        return (chosenId, chosenWindowGeo, chosenWindowAttr)


    def buildWindow(self, geoList):
        windowGeoList = []
        windowAttrList = []
        for geo in geoList:
            windowGeoList.append(rg.Rectangle3d(rg.Plane.WorldXY, float(geo.breite), float(geo.hoehe)))

            windowAttrList.append(geo.attr)
        
        return (windowGeoList, windowAttrList)


    def buildDoor(self, geoList):
        doorGeoList = []
        doorAttrList = []
        for geo in geoList:
            doorGeoList.append(rg.Rectangle3d(rg.Plane.WorldXY, float(geo.breite), float(geo.hoehe)))

            doorAttrList.append(geo.attr)

        return (doorGeoList, doorAttrList)
    

    def findDoor(self, doorDB, userDoorGeoList, gridWidth):
        """
        Identifies the best matching window dimensions from a database based on user-specified geometries,
        considering a given tolerance and grid width.

        Parameters:
            windowDB: A database or list of window objects with width and height attributes.
            userWindowGeoList: A list of user-specified window geometries to match against the database.
            gridWidth: The width of the grid to consider for matching.
            tolerance: The tolerance within which a match is considered acceptable.

        Returns:
            A list of indices corresponding to the chosen windows from the database.
            A list of geometries of window.
        """

        def _sortPoints(points, surf):
            """
            Sorts points based on their spatial relation to a reference surface, categorizing them into quadrants
            relative to the surface's frame and returning them in a specific order along with the surface frame.

            Parameters:
                points: A list of points to sort.
                surf: The reference surface or brep for sorting points.

            Returns:
                A tuple containing the sorted points in specific quadrants and the updated surface frame.
            """

            if isinstance(surf, rg.Surface) or isinstance(surf, rg.Brep):
                # Ensure surf is a Surface for the operations (if Brep, use its faces)
                if isinstance(surf, rg.Brep):
                    surf = surf.Faces[0]

                # 1. Calculate the Area Centroid of the Surface
                area_properties = rg.AreaMassProperties.Compute(surf)
                if area_properties is not None:
                    centroid = area_properties.Centroid

                    # 2. Find the Closest Point on the Surface to the Centroid
                    success, uvPU, uvPV = surf.ClosestPoint(centroid)
                    if success:
                        # 3. Evaluate the Surface at the UV Parameters
                        success, surf_Frame = surf.FrameAt(uvPU, uvPV)
                        surf_Frame = self.alignToZ(surf_Frame)
                        # if success:
                            # surf_Frame now contains the frame (plane) at the closest point
                            # Do something with surf_Frame, e.g., access its origin or its normal
                            # frame_origin = surf_Frame.Origin
                            # frame_normal = surf_Frame.Normal
                            # You can now use frame_origin and frame_normal as needed
                        # else:
                        #     print("Failed to evaluate the surface frame.")
                    else:
                        print("Failed to find the closest point on the surface.")
                else:
                    print("Failed to compute area properties.")
            else:
                print("The input 'surf' is not a valid surface or brep.")


            rTo = rg.Transform.ChangeBasis(rg.Plane.WorldXY, surf_Frame)
            rFro = rg.Transform.ChangeBasis(surf_Frame, rg.Plane.WorldXY)
            
            for pt in points:
                pt.Transform(rTo)
                if pt.X>0 and pt.Y>0:
                    pt.Transform(rFro)
                    pointHighFirst = pt
                elif pt.X<0 and pt.Y>0:
                    pt.Transform(rFro)
                    pointHighSecond = pt
                elif pt.X>0 and pt.Y<0:
                    pt.Transform(rFro)
                    pointLowFirst = pt
                elif pt.X<0 and pt.Y<0:
                    pt.Transform(rFro)
                    pointLowSecond = pt
            surf_Frame.Rotate(math.pi/2, surf_Frame.ZAxis)
            return (pointLowSecond, pointHighSecond, pointLowFirst, pointHighFirst, surf_Frame)
        
        DBwidthList = [door.geometry.Width for door in doorDB]
        DBheightList = [door.geometry.Height for door in doorDB]
        uList = []
        vList = []
        for doorGeo in userDoorGeoList:
            ptList = [vertex.Location for vertex in doorGeo.Vertices]
            ptList = _sortPoints(ptList, doorGeo)
            width = ptList[0].DistanceTo(ptList[1])
            height = ptList[0].DistanceTo(ptList[2])
            u, v = height, width
            uList.append(u)
            vList.append(v)

        chosenId = []
        chosenDoorGeo = []
        chosenDoorAttr = []
        for u,v in zip(uList, vList):
            minId = None
            minDist = float('inf')
            for id, (width, height) in enumerate(zip(DBwidthList, DBheightList)):
                if self.claddingDirection:
                    euclideanDist = (width-u)**2 + (height-v)**2 + ((width)%gridWidth)**3
                else:
                    euclideanDist = (width-u)**2 + (height-v)**2 + ((height)%gridWidth)**3
                if euclideanDist < minDist:
                    minId = id
                    minDist = euclideanDist
            chosenId.append(minId)
            chosenDoorGeo.append(doorDB[minId].geometry)
            chosenDoorAttr.append(doorDB[minId].attr)
        
        return (chosenId, chosenDoorGeo, chosenDoorAttr)


    def findCladding(self, claddingDB, searchWidth, searchLength, kindNum, wWeight, lWeight):
        widthDB = []
        lengthDB = []
        quantityDB = []
        for cladding in claddingDB.Branches:
            w, l = cladding[0].Width, cladding[0].Height
            widthDB.append(w)
            lengthDB.append(l)
            quantityDB.append(cladding[1])

        tileList = []
        for id, (w, l, q) in enumerate(zip(widthDB, lengthDB, quantityDB)):
            idName = "tile_" + str(id)
            tileList.append((w,l,q,idName))

        euclideanDistList = []
        for w, l, q, id in tileList:
            euclideanDist = abs((searchWidth-w)**wWeight) + abs((searchLength-l)**lWeight)
            euclideanDistList.append(euclideanDist)

        # Pair each element of first_list with the corresponding element in second_list
        paired_list = zip(tileList, euclideanDistList)

        # Sort the pairs based on the elements of second_list
        sorted_pairs = sorted(paired_list, key=lambda x: x[1])

        # Extract the sorted elements of first_list
        sorted_list = [element for element, _ in sorted_pairs]

        tileData = sorted_list[:kindNum]

        id = []
        width = []
        length = []
        quantity = []
        longList = [] # This one will be input to algorithm ============================

        for w, l, q, i in tileData:
            width.append(w)
            length.append(l)
            quantity.append(q)
            id.append(i)
            longList.extend([l]*q)

        return (id, width, length, quantity, longList)


    def _create_contours(self, surface, base_point, direct, interval):
        if isinstance(surface, rg.BrepFace):
            print("This is surface not brep")
            surface = surface.ToBrep()

        base_plane = rg.Plane(base_point, direct)
        
        contours = []

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
            contour_plane.Translate(base_plane.Normal * z + base_plane.Normal)

            # Generate the contour
            contour_curves = rg.Brep.CreateContourCurves(surface, contour_plane)
            contours.extend(contour_curves)

            z += interval


        return contours


    def generateTileColumn(self, wallGeo, gridDist):
        colBasePt = wallGeo.Vertices[0].Location
        self.seePt = colBasePt
        # if isinstance(wallGeo, rg.Brep):
        #     wallGeo = wallGeo.Faces[0]
        area_properties = rg.AreaMassProperties.Compute(wallGeo)
        if area_properties is not None:
            centroid = area_properties.Centroid
            success, uvPU, uvPV = wallGeo.ClosestPoint(centroid)
            if success:
                # 3. Evaluate the Surface at the UV Parameters
                success, wallGeo_Frame = wallGeo.Faces[0].FrameAt(uvPU, uvPV)
                if success:
                    frame_origin = wallGeo_Frame.Origin
                    frame_normal = wallGeo_Frame.Normal
                else:
                    print("Failed to evaluate the surface frame.")
            else:
                print("Failed to find the closest point on the surface.")
        else:
            print("Failed to compute area properties.")
        
        # # Align wallFrame's YAxis to global ZAxis
        # global_z_axis = rg.Vector3d.ZAxis
        # angle = rg.Vector3d.VectorAngle(wallGeo_Frame.YAxis, global_z_axis)
        
        # # Determine the direction of rotation (clockwise or counter-clockwise)
        # cross_product = rg.Vector3d.CrossProduct(wallGeo_Frame.YAxis, global_z_axis)
        # if cross_product * wallGeo_Frame.ZAxis < 0:  # If cross product is in opposite direction to frame's Z-axis
        #     angle = -angle
        
        # # Rotate the frame around its Z-axis
        # wallGeo_Frame.Rotate(angle, wallGeo_Frame.ZAxis, wallGeo_Frame.Origin)
        
        wallGeo_Frame = self.alignToZ(wallGeo_Frame)
        
        
        if wallGeo_Frame is not None:
            cutDirect = -AlignPlane(wallGeo_Frame, rg.Vector3d.ZAxis)[0].YAxis

            if not self.claddingDirection:
                wallGeo_Frame.Rotate(math.pi/2, wallGeo_Frame.ZAxis, wallGeo_Frame.Origin)
                cutDirect = AlignPlane(wallGeo_Frame, rg.Vector3d.ZAxis)[0].XAxis


            # if self.claddingDirection:
            #     cutDirect = -AlignPlane(wallGeo_Frame, rg.Vector3d.ZAxis)[0].YAxis
            # else:
            #     cutDirect = -AlignPlane(wallGeo_Frame, rg.Vector3d.ZAxis)[0].XAxis

            columnLine = self._create_contours(wallGeo, colBasePt, cutDirect, gridDist)
            return (columnLine, wallGeo_Frame, cutDirect)
        else:
            print("Failed to contour.")


    def orientWindow(self, claddingLine, userWindowGeo, chosenWindowGeo, wallGeo):
        def find_closest_point_on_lines(point, lines):
            closest_point = None
            min_distance = float('inf')  # Initialize with a very large number

            for curve in lines:
                success, t = curve.ClosestPoint(point)
                if success:
                    # Use the parameter 't' to get the actual closest point on the curve
                    temp_closest_point = curve.PointAt(t)
                    
                    # Now calculate the distance from 'point' to 'temp_closest_point'
                    distance = point.DistanceTo(temp_closest_point)

                    # Update the closest point if this curve is closer than previous ones
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = temp_closest_point

            return closest_point


        orientedWindowGeoList = []
        finalWindowPlaneList = []
        windowForFinalList = []
        for windowGeo, chosenGeo in zip(userWindowGeo, chosenWindowGeo):
            if isinstance(windowGeo, rg.Brep):
                windowGeo = windowGeo.Faces[0]
            else:
                windowGeo = windowGeo.geo.Faces[0]
            if isinstance(wallGeo, rg.Brep):
                wallGeo = wallGeo.Faces[0]
            
            if isinstance(chosenGeo, rg.Rectangle3d):
                geo_curve = chosenGeo.ToNurbsCurve()
                planar_surf = rg.Brep.CreatePlanarBreps(geo_curve)
                chosenGeo = planar_surf[0]

            # Get user's geometry's centroid and frame
            area_properties = rg.AreaMassProperties.Compute(windowGeo)
            if area_properties is not None:
                centroid = area_properties.Centroid

            success, uvPU, uvPV = windowGeo.ClosestPoint(centroid)
            if success:
                success, windowFrame = windowGeo.FrameAt(uvPU, uvPV)
                windowFrame = self.alignToZ(windowFrame)
                windowFrameOrigin = windowFrame.Origin
            
            # Get frame that closest to user's geometry's centroid
            success, uvPU, uvPV = wallGeo.ClosestPoint(windowFrameOrigin)
            if success:
                success, windowFrameOnWall = wallGeo.FrameAt(uvPU, uvPV)
                windowFrameOnWall = self.alignToZ(windowFrameOnWall)
            
            area_properties = rg.AreaMassProperties.Compute(chosenGeo)
            if area_properties is not None:
                centroid = area_properties.Centroid
                orientPlane = rg.Plane(centroid, rg.Vector3d.ZAxis)


            # Orient chosenWindow from DB default plane to user's geometry central plane
            trans1 = rg.Transform.PlaneToPlane(orientPlane, windowFrame)
            chosenGeoOnUserGeo = copy(chosenGeo)
            chosenGeoOnUserGeo.Transform(trans1)

            # Orient chosenGeoOnUserGeo from user's geometry central plane to wall
            trans2 = rg.Transform.PlaneToPlane(windowFrame, windowFrameOnWall)
            chosenGeoOnWallGeo = copy(chosenGeoOnUserGeo)
            chosenGeoOnWallGeo.Transform(trans2)  # chosen Opening is placed onto the wall

            #######################
            vec = self.alignSystem([chosenGeoOnWallGeo], self.ruler, 10, self.wallFrame)
            transOnRuler = rg.Transform.Translation(vec[0])
            chosenGeoOnWallGeoOnRuler = copy(chosenGeoOnWallGeo)
            chosenGeoOnWallGeoOnRuler.Transform(transOnRuler)#################################################


            # Orient XYPlane, which is DB default plane, onto the wall and align to grid
            XYPlaneOnUserGeo = copy(rg.Plane.WorldXY)
            XYPlaneOnUserGeo.Transform(trans1)
            XYPlaneOnWallGeo = copy(XYPlaneOnUserGeo)
            XYPlaneOnWallGeo.Transform(trans2)
            closestPoint = find_closest_point_on_lines(XYPlaneOnWallGeo.Origin, claddingLine)
            finalWindowPlane = rg.Plane(closestPoint, XYPlaneOnWallGeo.XAxis, XYPlaneOnWallGeo.YAxis)

            # Orient chosenWindowGeo to final position
            finalWindowGeo = copy(chosenGeoOnWallGeo)
            trans3 = rg.Transform.PlaneToPlane(XYPlaneOnWallGeo, finalWindowPlane)
            finalWindowGeo.Transform(trans3)

            # trans4 = rg.Transform.Translation(self.wallFrame.XAxis*self.horizontalOverlap)
            windowForFinal = copy(finalWindowGeo)
            # windowForFinal.Transform(trans4)

            orientedWindowGeoList.append(finalWindowGeo)
            finalWindowPlaneList.append(finalWindowPlane)
            # windowForFinalList.append(windowForFinal) ################# original
            windowForFinalList.append(chosenGeoOnWallGeoOnRuler) ################# original

        return (orientedWindowGeoList, finalWindowPlaneList, windowForFinalList)


    def orientDoor(self, claddingLine, userDoorGeo, chosenDoorGeo, wallGeo):
        def find_closest_point_on_lines(point, lines):
            closest_point = None
            min_distance = float('inf')  # Initialize with a very large number

            for curve in lines:
                success, t = curve.ClosestPoint(point)
                if success:
                    # Use the parameter 't' to get the actual closest point on the curve
                    temp_closest_point = curve.PointAt(t)
                    
                    # Now calculate the distance from 'point' to 'temp_closest_point'
                    distance = point.DistanceTo(temp_closest_point)

                    # Update the closest point if this curve is closer than previous ones
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = temp_closest_point

            return closest_point
        
        def find_door_point_on_edge(plane, brep_face):
            # Define a small tolerance value for intersection calculations
            tolerance = 0.001  # Example tolerance, adjust based on your precision requirements
            
            # Step 1: Extract the Y-axis from the plane
            yAxisLine = rg.Line(plane.Origin, plane.Origin + plane.YAxis * 1000) # Creating a long line along the Y-axis
            
            # Initialize a list to collect intersection points
            intersection_points = []

            # Step 2: Get the parent Brep of the BrepFace
            brep = brep_face.Brep

            # Get indices of edges adjacent to the BrepFace
            edge_indices = brep_face.AdjacentEdges()

            # Step 3: Extract the edge curves from the Brep using the indices
            edges = [brep.Edges[edge_index].ToNurbsCurve() for edge_index in edge_indices]

            # Step 4: Find the intersection points
            for edge in edges:
                intersection_events = rg.Intersect.Intersection.CurveLine(edge, yAxisLine, tolerance, tolerance)
                for event in intersection_events:
                    point = event.PointA  # Intersection point on the curve
                    intersection_points.append(point)

            # Step 5: Select the appropriate intersection point
            if intersection_points:
                closest_point = min(intersection_points, key=lambda pt: pt.DistanceTo(plane.Origin))
                return closest_point
            else:
                print("No intersection found.")
                return None



        orientedDoorGeoList = []
        finalDoorPlaneList = []
        doorForFinalList = []
        for doorGeo, chosenGeo in zip(userDoorGeo, chosenDoorGeo):
            if isinstance(doorGeo, rg.Brep):
                doorGeo = doorGeo.Faces[0]
            else:
                doorGeo = doorGeo.geo.Faces[0]
            
            if isinstance(wallGeo, rg.Brep):
                wallGeo = wallGeo.Faces[0]
            
            if isinstance(chosenGeo, rg.Rectangle3d):
                geo_curve = chosenGeo.ToNurbsCurve()
                planar_surf = rg.Brep.CreatePlanarBreps(geo_curve)
                chosenGeo = planar_surf[0]

            # Get user's geometry's centroid and frame
            area_properties = rg.AreaMassProperties.Compute(doorGeo)
            if area_properties is not None:
                centroid = area_properties.Centroid

            success, uvPU, uvPV = doorGeo.ClosestPoint(centroid)
            if success:
                success, doorFrame = doorGeo.FrameAt(uvPU, uvPV)
                doorFrame = self.alignToZ(doorFrame)
                doorFrameOrigin = doorFrame.Origin
            
            # Get frame that closest to user's geometry's centroid
            success, uvPU, uvPV = wallGeo.ClosestPoint(doorFrameOrigin)
            if success:
                success, doorFrameOnWall = wallGeo.FrameAt(uvPU, uvPV)
                doorFrameOnWall = self.alignToZ(doorFrameOnWall)
            
            area_properties = rg.AreaMassProperties.Compute(chosenGeo)
            if area_properties is not None:
                centroid = area_properties.Centroid
                orientPlane = rg.Plane(centroid, rg.Vector3d.ZAxis)


            # Orient chosenWindow from DB default plane to user's geometry central plane
            trans1 = rg.Transform.PlaneToPlane(orientPlane, doorFrame)
            chosenGeoOnUserGeo = copy(chosenGeo)
            chosenGeoOnUserGeo.Transform(trans1)

            # Orient chosenGeoOnUserGeo from user's geometry central plane to wall
            trans2 = rg.Transform.PlaneToPlane(doorFrame, doorFrameOnWall)
            chosenGeoOnWallGeo = copy(chosenGeoOnUserGeo)
            chosenGeoOnWallGeo.Transform(trans2)

            vec = self.alignSystem([chosenGeoOnWallGeo], self.ruler, 10, self.wallFrame)
            transOnRuler = rg.Transform.Translation(vec[0])
            chosenGeoOnWallGeoOnRuler = copy(chosenGeoOnWallGeo)
            chosenGeoOnWallGeoOnRuler.Transform(transOnRuler)#################################################


            # Orient XYPlane, which is DB default plane, onto the wall and align to grid
            XYPlaneOnUserGeo = copy(rg.Plane.WorldXY)
            XYPlaneOnUserGeo.Transform(trans1)
            XYPlaneOnWallGeo = copy(XYPlaneOnUserGeo)
            XYPlaneOnWallGeo.Transform(trans2)
            closestPoint = find_closest_point_on_lines(XYPlaneOnWallGeo.Origin, claddingLine)
            # closestPoint = find_door_point_on_edge(self.alignToZ(self.wallFrame), wallGeo) #==========================================================================================
            finalDoorPlane = rg.Plane(closestPoint, XYPlaneOnWallGeo.XAxis, XYPlaneOnWallGeo.YAxis)

            # Orient chosenWindowGeo to final position
            finalDoorGeo = copy(chosenGeoOnWallGeo)
            trans3 = rg.Transform.PlaneToPlane(XYPlaneOnWallGeo, finalDoorPlane)
            finalDoorGeo.Transform(trans3)

            # trans4 = rg.Transform.Translation(self.wallFrame.XAxis*self.horizontalOverlap)
            doorForFinal = copy(finalDoorGeo)
            # doorForFinal.Transform(trans4)


            orientedDoorGeoList.append(finalDoorGeo)
            finalDoorPlaneList.append(finalDoorPlane)
            # doorForFinalList.append(doorForFinal) ############################### original
            doorForFinalList.append(chosenGeoOnWallGeoOnRuler) ##################################

        return (orientedDoorGeoList, finalDoorPlaneList, doorForFinalList)
     

    def getMidCurve(self, claddingLine):
        firstCurves = claddingLine[:-1]
        secondCurves = claddingLine[1:]
        pairedCurves = zip(firstCurves, secondCurves)

        midLine = []
        for pair in pairedCurves:
            fir, sec = pair
            firStartPt = fir.PointAtStart
            firEndPt = fir.PointAtEnd
            secStartPt = sec.PointAtStart
            secEndPt = sec.PointAtEnd
            midStartPt = (firStartPt + secStartPt)/2
            midEndPt = (firEndPt + secEndPt)/2
            midLine.append(rg.Line(midStartPt, midEndPt))

        return midLine


    def calculateInnerGeo(self, windowList, doorList):
        # Generate basic wall geometry for inner material
        allGeo = []
        allGeo.extend(windowList)
        allGeo.extend(doorList)
        reAllGeo = RegionUnion(allGeo, self.wallFrame)
        innerGeo = RegionDifference(self.claddingGeo, reAllGeo, self.wallFrame)
        wallForInnerGeo = self.offset_brep(BoundarySurfaces(innerGeo), [-self.offsetDist], self.wallFrame)[0]

        return wallForInnerGeo
    

    def calculateFacadeGeo(self, windowList, doorList):
        # Generate basic wall geometry for inner material
        allGeo = []
        allGeo.extend(windowList)
        allGeo.extend(doorList)
        reAllGeo = RegionUnion(allGeo, self.wallFrame)
        innerGeo = RegionDifference(self.claddingGeo, reAllGeo, self.wallFrame)
        wallForInnerGeo = self.offset_brep(BoundarySurfaces(innerGeo), [0], self.wallFrame)[0]

        return wallForInnerGeo
