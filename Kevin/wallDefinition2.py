import Rhino.Geometry as rg
from ghpythonlib.components import Area, SurfaceClosestPoint, EvaluateSurface, SurfaceSplit, Extrude, OffsetCurve, BoundarySurfaces, TrimwithRegions, JoinCurves, RegionDifference, AlignPlane, EvaluateLength, LineSDL, Project, RegionUnion
import ghpythonlib.treehelpers as th
import math
from copy import copy, deepcopy
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree
import System.Array as array
from itertools import chain
import random
from collections import Counter


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


class innerMaterialGenerate:
    def __init__(self, surfaceList, materialList, thicknessList, moduleDistance, wallFrame):
        self.surfaceList = surfaceList
        self.materialList = materialList
        self.thicknessList = thicknessList
        self.moduleDistance = moduleDistance
        self.wallFrame = wallFrame

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

        for self.id, (srfList, matList) in enumerate(zip(self.surfaceList, self.materialList)):
            mat = matList
            srfList = [srfList]
            
            allTypeGeo = []
            for entireSrf_id, entireSrf in enumerate(srfList):
                workPlane = basePlane[entireSrf_id]
                matType = mat.materialType
                srfList = self.create_module(entireSrf, workPlane, self.moduleDistance)
                self.checkGeo.append(srfList)

                if self.id not in self.materialInfoDict:
                    self.materialInfoDict[self.id] = {}


                for self.module_id, srf in enumerate(srfList):
                    if self.module_id not in self.materialInfoDict[self.id]:
                        self.materialInfoDict[self.id][self.module_id] = {}

                    allTypeGeoModule = []
                    if matType == "board":
                        boardGeo = self.create_board(srf, workPlane, mat.length, mat.width, mat.thickness, mat.direction)
                        boardGeoList.append(boardGeo)
                        allTypeGeo.append(boardGeo)
                        allTypeGeoModule.append(boardGeo)
                        
                    elif matType == "substructInfill":
                        panelGeo, beamGeo = self.create_substructInfill(srf, workPlane, mat.width, mat.thickness, mat.distance, mat.direction)
                        substructInfillGeoList.append(beamGeo)
                        substructInfillGeoList.append(panelGeo)
                        allTypeGeo.append(beamGeo)
                        allTypeGeo.append(panelGeo)
                        li = []
                        li.extend(beamGeo)
                        li.extend(panelGeo)
                        allTypeGeoModule.append(li)

                    elif matType == "paint":
                        paintGeo = self.create_paint(srf, workPlane, mat.thickness)
                        paintGeoList.append([paintGeo])
                        allTypeGeo.append([paintGeo])
                        allTypeGeoModule.append([paintGeo])
                        
                    elif matType == "substruct":
                        substructGeo = self.create_substruct(srf, workPlane, mat.width, mat.thickness, mat.distance, mat.direction)
                        substructGeoList.append(substructGeo)
                        allTypeGeo.append(substructGeo)
                        allTypeGeoModule.append(substructGeo)

                    elif matType == "cladding":
                        claddingGeo = self.create_cladding(srf, workPlane, mat.length, mat.width, mat.thickness, mat.direction)
                        claddingGeoList.append(claddingGeo)
                        allTypeGeo.append(claddingGeo)
                        allTypeGeoModule.append(claddingGeo)
                    
                    path_module = GH_Path(array[int]([self.id, self.module_id]))
                    layerTreeModule.AddRange(allTypeGeoModule, path_module)
                    
                
            path = GH_Path(array[int]([0,0,self.id]))
            layerTree.AddRange(allTypeGeo, path)
                
        self.allTypeMaterial = layerTree
        self.allTypeMaterialModule = layerTreeModule
        


    def create_module(self, surface, base_plane, distance):
        def sortSurface(srfList, sortPlane):
            # Calculate the center point of each surface's bounding box
            centers = [srf.GetBoundingBox(True).Center for srf in srfList]
            
            # Project these center points onto the sortPlane's Y-axis and calculate distance from the plane's origin
            distances = [sortPlane.YAxis * (center - sortPlane.Origin) for center in centers]
            
            # Sort the surfaces based on these distances
            sortedSurfaces = [srf for _, srf in sorted(zip(distances, srfList))]
            
            return sortedSurfaces

        base_plane = copy(base_plane)
        base_plane.Rotate(math.pi/2, base_plane.ZAxis, base_plane.Origin)
        curves, _ = self.create_contours(surface, base_plane, distance)
        surfaceList = SurfaceSplit(surface, curves)
        surfaceList = sortSurface(surfaceList, base_plane)

        return surfaceList


    def create_contours(self, surface, base_plane, interval):
        base_plane = copy(base_plane)
        base_plane.Rotate(math.pi/2, base_plane.XAxis, base_plane.Origin)
        base_plane.Rotate(math.pi/10, base_plane.ZAxis, base_plane.Origin)
        contours = []
        # trimmed_contours = []

        # Get the bounding box of the surface in the plane's coordinate system
        bbox = surface.GetBoundingBox(base_plane)

        # Start and end values for contouring in the direction of the plane's normal
        start = bbox.Min.Z
        end = bbox.Max.Z
        
        # Generate contours
        # z = start
        # while z <= end:
        #     # Create a plane parallel to the base plane at height z
        #     contour_plane = rg.Plane(base_plane)
        #     contour_plane.Translate(base_plane.Normal * z)

        #     # Generate the contour
        #     contour_curves = rg.Brep.CreateContourCurves(surface, contour_plane)
        #     contours.extend(contour_curves)
            
        #     z += interval
        
        # =====================
        z = end
        while z >= start:
            # Create a plane parallel to the base plane at height z
            contour_plane = rg.Plane(base_plane)
            contour_plane.Translate(base_plane.Normal * z)

            # Generate the contour
            contour_curves = rg.Brep.CreateContourCurves(surface, contour_plane)
            contours.extend(contour_curves)
            
            z -= interval



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

        crvLength, _ = self.create_contours(surface, firDirPlane, length)
        crvWidth, _ = self.create_contours(surface, secDirPlane, width)

        crvCombine = []
        crvCombine.extend(crvLength)
        crvCombine.extend(crvWidth)


        panelGeoList = SurfaceSplit(surface, crvCombine)

        # create panel geometry
        panelOffsetList = []
        boardSeam = 2
        for panel in panelGeoList:
            panelOffsetList.append(Extrude(panel, base_plane.ZAxis*thickness))

        # Record Material using information.
        boardArea = length*width
        cuttedPiece = 0
        for panel in panelGeoList:
            area_properties = rg.AreaMassProperties.Compute(panel)
            if area_properties is not None:
                panelArea = area_properties.Area
                if (boardArea - panelArea) > 100:
                    cuttedPiece += 1

        usedPiece = len(panelGeoList)
        self.materialInfoDict[self.id][self.module_id]["typeName"] = "board"
        self.materialInfoDict[self.id][self.module_id]["usedPiece"] = usedPiece
        self.materialInfoDict[self.id][self.module_id]["cuttedPiece"] = cuttedPiece
        self.materialInfoDict[self.id][self.module_id]["completedPiece"] = usedPiece - cuttedPiece
        
        return panelOffsetList


    def create_substructInfill(self, surface, base_plane, width, thickness, distance, direction):
        def offset_surface_inner(surface, plane, distance, tolerance=0.01):
            inner_distance = -abs(distance)
            
            # Offset the surface
            print(type(surface))
            offset_surface = surface.Offset(1000, tolerance)
            
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
        
        # self.materialInfoList.append((self.module_id, "substructInfill", substructureLength))
        self.materialInfoDict[self.id][self.module_id]["typeName"] = "substructInfill"
        self.materialInfoDict[self.id][self.module_id]["usedLength"] = substructureLength
        self.materialInfoDict[self.id][self.module_id]["usedArea"] = int(totalArea)

        return (panelOffsetList, beamGeo)


    def create_paint(self, surface, base_plane, thickness):
        area_properties = rg.AreaMassProperties.Compute(surface)
        if area_properties is not None:
            panelArea = area_properties.Area

        self.materialInfoDict[self.id][self.module_id]["typeName"] = "paint"
        self.materialInfoDict[self.id][self.module_id]["usedArea"] = None
        self.materialInfoDict[self.id][self.module_id]["usedArea"] = int(panelArea)


        return Extrude(surface, base_plane.ZAxis*thickness)


    def create_substruct(self, surface, base_plane, width, thickness, distance, direction):
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
        self.materialInfoDict[self.id][self.module_id]["typeName"] = "substruct"
        self.materialInfoDict[self.id][self.module_id]["usedLength"] = substructureLength

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


class generateCladding:
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

    def __init__(self, windowDB, doorDB, claddingDB, wallGeo, windowGeo, doorGeo, claddingWidth=299, claddingLength=399, kindNum=4, wWeight=5, lWeight=4, claddingDirection=False, horizontalOverlap=0, verticalOverlap=0, horizontalAngle=0, verticalAngle=0, substructWidth=40, substructThickness=20, offsetDist=0,**kwargs):
        """
        Initializes the GenerateCladding class with all the necessary attributes for cladding generation.
        """
        global initial_data
        self.windowDB = windowDB
        self.doorDB = doorDB
        self.claddingDB = claddingDB
        self.wallGeo = wallGeo
        self.windowGeo = windowGeo
        self.doorGeo = doorGeo
        self.claddingWidth = claddingWidth
        self.claddingLength = claddingLength
        self.kindNum = kindNum
        self.wWeight = wWeight
        self.lWeight = lWeight
        self.claddingDirection = claddingDirection
        self.horizontalOverlap = horizontalOverlap
        self.verticalOverlap = verticalOverlap
        self.horizontalAngle = horizontalAngle
        self.verticalAngle = verticalAngle
        self.substructWidth = substructWidth
        self.substructThickness = substructThickness
        self.offsetDist = offsetDist + self.substructThickness
        self.tileDimension = kwargs.get('tileDimension', None)
        
        # Find user's tile based on input criteria
        if self.tileDimension == None:
            b1 = self.compare("claddingWidth", self.claddingWidth)
            b2 = self.compare("claddingLength", self.claddingLength)
            b3 = self.compare("kindNum", self.kindNum)
            b4 = self.compare("wWeight", self.wWeight)
            b5 = self.compare("lWeight", self.lWeight)
            if  b1 or b2 or b3 or b4 or b5:
                print("find tile!!")
                id, width, length, quantity, self.longList = self.findCladding(self.claddingDB, self.claddingWidth, self.claddingLength, self.kindNum, self.wWeight, self.lWeight)
                initial_data["longList"] = self.longList
                initial_data["width"] = width
                initial_data["length"] = length
            else:
                print("don't find again")
                width = initial_data["width"]
                length = initial_data["length"]
                self.longList = initial_data["longList"]

        else:
            print("start customize tile process")
            width, length, self.longList = self.customizedCladding(self.tileDimension)


        # build mapping for width and length
        self.number_mapping = {}
        for w, l in zip(width, length):
            self.number_mapping[l] = w

        # Decide grid distance based on the minimum width of the tile
        paired_list = zip(length, width)
        sorted_list = sorted(paired_list, key=lambda x: x[1])
        self.minTileWidth = sorted_list[0][1]
        self.minTileLength = sorted_list[0][0]
        self.gridDist = self.minTileWidth - self.horizontalOverlap
        #print(self.minTileWidth)
        #print(self.minTileLength)

        self.claddingGeo = self.offset_brep(self.wallGeo, [self.offsetDist])[0]

        # Generate the column line, wall frame, and cut direction for the cladding
        self.columnLine, self.wallFrame, self.cutDirect = self.generateTileColumn(self.claddingGeo, self.gridDist)

        # Get window indices and geometries from DB that match users' dimension of geometry for window.
        chosenWindowId, self.chosenWindowGeo = self.findWindow(self.windowDB, self.windowGeo, self.gridDist, self.horizontalOverlap)
        chosenDoorId, self.chosenDoorGeo = self.findDoor(self.doorDB, self.doorGeo, self.gridDist, self.horizontalOverlap)

        # Orient window and door onto grid system
        self.orientedWindowGeoList, self.finalWindowPlaneList, self.windowForFinalList = self.orientWindow(self.columnLine, self.windowGeo, self.chosenWindowGeo, self.claddingGeo)
        self.orientedDoorGeoList, self.finalDoorPlaneList, self.doorForFinalList = self.orientDoor(self.columnLine, self.doorGeo, self.chosenDoorGeo, self.claddingGeo)

        self.midCurve = self.getMidCurve(self.columnLine)


        # Generate basic wall geometry for inner material
        self.wallForInnerGeo = self.calculateInnerGeo(self.windowForFinalList, self.doorForFinalList)

        # Find the target lines for cladding searching algorithm.
        self.targetLines, self.targetLinesLength = self.trimWithRegion(self.midCurve, self.orientedWindowGeoList, self.orientedDoorGeoList, self.wallFrame)

        # compare if target lines are changed, if yes, calculate it again.
        targetsLengthflatten = [int(t) for t in list(chain.from_iterable(self.targetLinesLength))]
        sourceLength = [int(s) for s in self.longList]

        # Sometimes, when I moved opening, it happens error due to the crack of evaluate length in self.generateCladdingByTarget. Thus, I use "try" here to initialize everything again.
        toler = (self.minTileLength+self.verticalOverlap)*0.4
        try:
            if self.compare("targetsLengthflatten", targetsLengthflatten) or self.compare("sourceLength", sourceLength) or "combinationGraph" not in initial_data:
                # Use cladding sarching algorithm.
                self.combinationGraph = self.calculateTarget(self.longList, self.targetLinesLength, toler)
                initial_data["combinationGraph"] = self.combinationGraph
            else:
                self.combinationGraph = initial_data["combinationGraph"]

            # put tile onto the line according to result of calculation.
            self.tileLocation = self.generateCladdingByTarget(self.targetLines, self.originalCoGraft, self.combinationGraph)

            self.substructureGeo = self.addSubstructure(self.substructureList, self.substructWidth, self.substructThickness)
        except:
            print("happpen errrorrrr!!!!")
            initial_data = {}
            if self.compare("targetsLengthflatten", targetsLengthflatten) or self.compare("sourceLength", sourceLength) or "combinationGraph" not in initial_data:
                # Use cladding sarching algorithm.
                self.combinationGraph = self.calculateTarget(self.longList, self.targetLinesLength, toler)
                initial_data["combinationGraph"] = self.combinationGraph
            else:
                self.combinationGraph = initial_data["combinationGraph"]

            # put tile onto the line according to result of calculation.
            self.tileLocation = self.generateCladdingByTarget(self.targetLines, self.originalCoGraft, self.combinationGraph)

            self.substructureGeo = self.addSubstructure(self.substructureList, self.substructWidth, self.substructThickness)

        
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


    def offset_brep(self, brep, distances, tolerance=0.01):
        if isinstance(brep, list):
            brep = brep[0]
        all_offset_breps = []
        for distance in distances:
            offset_breps = rg.Brep.CreateOffsetBrep(brep, distance, solid=False, extend=False, tolerance=tolerance)
            if offset_breps:
                all_offset_breps.append(offset_breps[0][0])
            else:
                print("Offset operation failed for distance .")
                all_offset_breps.append(None)
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


    def findWindow(self, windowDB, userWindowGeoList, gridWidth, tolerance):
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
        
        DBwidthList = [win.Width for win in windowDB]
        DBheightList = [win.Height for win in windowDB]
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
        for u,v in zip(uList, vList):
            minId = None
            minDist = float('inf')
            for id, (width, height) in enumerate(zip(DBwidthList, DBheightList)):
                euclideanDist = (width-u)**2 + (height-v)**2 + ((width+tolerance)%gridWidth)**3
                if euclideanDist < minDist:
                    minId = id
                    minDist = euclideanDist
            chosenId.append(minId)
            chosenWindowGeo.append(windowDB[minId])
        
        return (chosenId, chosenWindowGeo)


    def findDoor(self, doorDB, userDoorGeoList, gridWidth, tolerance):
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
        
        DBwidthList = [door.Width for door in doorDB]
        DBheightList = [door.Height for door in doorDB]
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
        for u,v in zip(uList, vList):
            minId = None
            minDist = float('inf')
            for id, (width, height) in enumerate(zip(DBwidthList, DBheightList)):
                euclideanDist = (width-u)**2 + (height-v)**2 + ((width+tolerance)%gridWidth)**3
                if euclideanDist < minDist:
                    minId = id
                    minDist = euclideanDist
            chosenId.append(minId)
            chosenDoorGeo.append(doorDB[minId])
        
        return (chosenId, chosenDoorGeo)


    def findCladding(self, claddingDB, searchWidth, searchLength, kindNum, wWeight, lWeight):
        print("searching cladding now...")
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
            contour_plane.Translate(base_plane.Normal * z)

            # Generate the contour
            contour_curves = rg.Brep.CreateContourCurves(surface, contour_plane)
            contours.extend(contour_curves)

            z += interval


        return contours


    def generateTileColumn(self, wallGeo, gridDist):
        colBasePt = wallGeo.Vertices[0].Location
        if isinstance(wallGeo, rg.Brep):
            wallGeo = wallGeo.Faces[0]
        area_properties = rg.AreaMassProperties.Compute(wallGeo)
        if area_properties is not None:
            centroid = area_properties.Centroid
            success, uvPU, uvPV = wallGeo.ClosestPoint(centroid)
            if success:
                # 3. Evaluate the Surface at the UV Parameters
                success, wallGeo_Frame = wallGeo.FrameAt(uvPU, uvPV)
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
            chosenGeoOnWallGeo.Transform(trans2)

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

            trans4 = rg.Transform.Translation(self.wallFrame.XAxis*self.horizontalOverlap)
            windowForFinal = copy(finalWindowGeo)
            windowForFinal.Transform(trans4)


            orientedWindowGeoList.append(finalWindowGeo)
            finalWindowPlaneList.append(finalWindowPlane)
            windowForFinalList.append(windowForFinal)

        return (orientedWindowGeoList, finalWindowPlaneList, windowForFinalList)


    def orientDoor(self, claddingLine, userDoorGeo, chosenDoorGeo, wallGeo):
        def find_closest_point_on_lines(point, lines):
            closest_point = None
            closest_st_point = None
            closest_end_point = None
            min_distance = float('inf')  # Initialize with a very large number

            for curve in lines:
                success, t = curve.ClosestPoint(point)
                if success:
                    # Use the parameter 't' to get the actual closest point on the curve
                    temp_closest_point = curve.PointAt(t)
                    temp_closest_st_point, temp_closest_end_point = curve.PointAtStart, curve.PointAtEnd
                    
                    # Now calculate the distance from 'point' to 'temp_closest_point'
                    distance = point.DistanceTo(temp_closest_point)

                    # Update the closest point if this curve is closer than previous ones
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = temp_closest_point
                        closest_st_point = temp_closest_st_point
                        closest_end_point = temp_closest_end_point
            
            if closest_st_point.Z < closest_end_point:
                closest_point = closest_st_point
            else:
                closest_point = closest_end_point
            
            # Make door position slightly lower
            trans = rg.Transform.Translation(-self.wallFrame.YAxis)
            closest_point.Transform(trans)

            return closest_point


        orientedDoorGeoList = []
        finalDoorPlaneList = []
        doorForFinalList = []
        for doorGeo, chosenGeo in zip(userDoorGeo, chosenDoorGeo):
            if isinstance(doorGeo, rg.Brep):
                doorGeo = doorGeo.Faces[0]
            
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

            # Orient XYPlane, which is DB default plane, onto the wall and align to grid
            XYPlaneOnUserGeo = copy(rg.Plane.WorldXY)
            XYPlaneOnUserGeo.Transform(trans1)
            XYPlaneOnWallGeo = copy(XYPlaneOnUserGeo)
            XYPlaneOnWallGeo.Transform(trans2)
            closestPoint = find_closest_point_on_lines(XYPlaneOnWallGeo.Origin, claddingLine)
            finalDoorPlane = rg.Plane(closestPoint, XYPlaneOnWallGeo.XAxis, XYPlaneOnWallGeo.YAxis)

            # Orient chosenWindowGeo to final position
            finalDoorGeo = copy(chosenGeoOnWallGeo)
            trans3 = rg.Transform.PlaneToPlane(XYPlaneOnWallGeo, finalDoorPlane)
            finalDoorGeo.Transform(trans3)

            trans4 = rg.Transform.Translation(self.wallFrame.XAxis*self.horizontalOverlap)
            doorForFinal = copy(finalDoorGeo)
            doorForFinal.Transform(trans4)


            orientedDoorGeoList.append(finalDoorGeo)
            finalDoorPlaneList.append(finalDoorPlane)
            doorForFinalList.append(doorForFinal)

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
        wallForInnerGeo = self.offset_brep(BoundarySurfaces(innerGeo), [-self.offsetDist])[0]

        return wallForInnerGeo


    def trimWithRegion(self, midCurves, windowGeo, doorGeo, basePlane):
        def move_largest_x_points(points, plane, distance):
            # Transform points to the plane's coordinate system
            transformed_points = [plane.RemapToPlaneSpace(point)[1] for point in points]
            
            # Find indices of the two points with the largest x-coordinates
            largest_x_indices = sorted(range(len(transformed_points)), key=lambda i: transformed_points[i].X)[-2:]
            
            # Initialize a list to hold the final positions of all points
            final_points = points[:]
            
            # Move the identified points along the plane's x-axis
            for index in largest_x_indices:
                # Calculate the new position in the plane's coordinate system
                moved_point_plane_space = rg.Point3d(transformed_points[index].X + distance, transformed_points[index].Y, transformed_points[index].Z)
                
                # Transform the moved point back to the world coordinate system
                moved_point_world_space = plane.PointAt(moved_point_plane_space.X, moved_point_plane_space.Y, moved_point_plane_space.Z)
                
                # Update the point in the final list
                final_points[index] = moved_point_world_space
            
            return final_points
        
        # def split_curve_by_points(curve, points):
        #     print(type(curve))
        #     curve = curve.ToNurbsCurve()
        #     # List to store parameters on the curve corresponding to the points
        #     parameters = []

        #     # Convert each point to a parameter on the curve
        #     for point in points:
        #         rc, t = curve.ClosestPoint(point, 20)
        #         if rc:  # If the closest point was successfully found
        #             parameters.append(t)

        #     # Split the curve at the collected parameters
        #     split_curves = curve.Split(parameters)

        #     return split_curves

        def split_curve_by_points(curves, points, height):
            ptNum = len(points)
            tileTotalHeigth = self.minTileLength * (ptNum-1)

            # check if cutting point overlap with the below window
            changeBool = False
            for curve in curves:
                firPt = points[0]
                rc, t = curve.ClosestPoint(firPt, 1)
                if abs(curve.GetLength()-self.minTileLength)<10 and rc:
                    changeBool = True
                    print("overlap, ver 1")
                    temp_pt = curve.PointAt(t)
                    ptAtStart = curve.PointAtStart
                    dist = temp_pt.DistanceTo(ptAtStart)
                    trans = rg.Transform.Translation(self.wallFrame.YAxis*dist)
            if changeBool:
                newPoints = []
                for pt in points:
                    n_pt = deepcopy(pt)
                    n_pt.Transform(trans)
                    newPoints.append(n_pt)
                if tileTotalHeigth + dist - height > self.minTileLength:
                    newPoints = newPoints[:-1]
            else:
                newPoints = deepcopy(points)
            

            # check if cutting point too approach to the bottom tile position
            changeBool2 = False
            for curve in curves:
                firPt = newPoints[0]
                rc, t = curve.ClosestPoint(firPt, 1)
                ptAtEnd = curve.PointAtEnd
                if rc:
                    temp_pt = curve.PointAt(t)
                    dist2 = temp_pt.DistanceTo(ptAtEnd)
                    if dist2 < self.minTileLength and dist2>0.1:
                        print("too closed, ver2")
                        changeBool2 = True
                        trans2 = rg.Transform.Translation(-self.wallFrame.YAxis*dist2)
            
            if changeBool2:
                newPoints2 = []
                for pt in newPoints:
                    n_pt = deepcopy(pt)
                    n_pt.Transform(trans2)
                    newPoints2.append(n_pt)
                n_pt = deepcopy(newPoints2[-1])
                trans3 = rg.Transform.Translation(self.wallFrame.YAxis*self.minTileLength)
                dist3 = self.minTileLength
                
                if tileTotalHeigth - dist2 + dist3 - height  < self.minTileLength + self.verticalOverlap:
                    print("too closed, and delete the last")
                    n_pt.Transform(trans3)
                    newPoints2.append(n_pt)
            else:
                newPoints2 = deepcopy(newPoints)


            all_split_curves = []  # List to store lists of split curves for each input curve
            for curve in curves:
                curve = curve.ToNurbsCurve()
                parameters = []  # List to store parameters on the curve corresponding to the points
                # Convert each point to a parameter on the curve
                for point in newPoints2:
                    rc, t = curve.ClosestPoint(point, 10)
                    if rc:  # If the closest point was successfully found
                        parameters.append(t)

                # Split the curve at the collected parameters
                split_curves = curve.Split(parameters)
                if split_curves:  # Check if any curves were actually split
                    all_split_curves.extend(list(split_curves))
                else:
                    all_split_curves.extend([curve])  # Append an empty list if no splits were made

            return all_split_curves


        def sort_geometry(polylines, plane):
            def to_plane_coordinates(point, plane):
                # Create a transformation from World XY to the target plane
                xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, plane)
                
                # Create a copy of the point to avoid modifying the original
                transformed_point = rg.Point3d(point)
                
                # Apply the transformation
                transformed_point.Transform(xform)
                
                return transformed_point

            # Function to get the minimum Z value of a polyline's control points in the plane's coordinates
            def min_Y_in_plane(polyline, plane):
                transformed_points = [to_plane_coordinates(pt, plane) for pt in polyline]
                min_Y = max(pt.Y for pt in transformed_points)
                return min_Y
            
            def polyline_height(polyline, plane):
                transformed_points = [to_plane_coordinates(pt, plane) for pt in polyline]
                min_Y = min(pt.Y for pt in transformed_points)
                max_Y = max(pt.Y for pt in transformed_points)
                # Calculate height as the difference between max and min Y values
                height = max_Y - min_Y
                return height

            # Sort the polylines by the minimum Z value of their control points in the plane's coordinates
            sorted_polylines = sorted(polylines, key=lambda pl: min_Y_in_plane(pl, plane), reverse=True)
            # Calculate height for each polyline and pair it with the polyline
            polylines_with_height = [polyline_height(pl, plane) for pl in sorted_polylines]

            return (sorted_polylines, polylines_with_height)


        # In condition that wall doesn't have opening.
        if len(windowGeo) == 0 and len(doorGeo) == 0:
            self.Co = [crv.ToNurbsCurve() for crv in midCurves]

            
            self.originalCo = deepcopy(self.Co)
            self.CoGraft = [[c] for c in self.originalCo]
            self.originalCoGraft = [[c] for c in self.originalCo]

            extendCo = deepcopy(self.Co)
            for index, crv in enumerate(self.Co):
                extendCo[index] = extendCo[index].Extend(rg.CurveEnd.Start, self.verticalOverlap, 0)
                extendCo[index] = [extendCo[index].Extend(rg.CurveEnd.End, self.verticalOverlap, 0)]
                # Here self.Co format is changed into nest structure.
    
            extendCoLength = deepcopy(extendCo)
            for gId, group in enumerate(extendCo):
                for cId, crv in enumerate(group):
                    extendCoLength[gId][cId] = crv.GetLength()

            return (extendCo, extendCoLength)
        
        else:
            # Search the tile column adjoin the right side of window.
            # Calculate the compenstion for openings
            self.compensatedWindowGeo = []
            self.compensatedWindowGeoNext = []
            self.compensatedDoorGeo = []
            self.compensatedDoorGeoNext = []
            for winb in windowGeo:
                winVerticesPt = [vertex.Location for vertex in winb.Vertices]
                winVerticesPt = move_largest_x_points(winVerticesPt, basePlane, self.horizontalOverlap/2)
                winVerticesPtforNext = move_largest_x_points(winVerticesPt, basePlane, self.gridDist)
                winVerticesPt.append(winVerticesPt[0])
                winVerticesPtforNext.append(winVerticesPtforNext[0])
                
                self.compensatedWindowGeo.append(rg.Polyline(winVerticesPt))
                self.compensatedWindowGeoNext.append(rg.Polyline(winVerticesPtforNext))

            for doorb in doorGeo:
                doorVerticesPt = [vertex.Location for vertex in doorb.Vertices]
                doorVerticesPt = move_largest_x_points(doorVerticesPt, basePlane, self.horizontalOverlap/2)
                doorVerticesPtforNext = move_largest_x_points(doorVerticesPt, basePlane, self.gridDist)
                doorVerticesPt.append(doorVerticesPt[0])
                doorVerticesPtforNext.append(doorVerticesPtforNext[0])
                
                self.compensatedDoorGeo.append(rg.Polyline(doorVerticesPt))
                self.compensatedDoorGeoNext.append(rg.Polyline(doorVerticesPtforNext))
                
            self.compensatedCombineGeo = self.compensatedWindowGeo
            self.compensatedCombineGeo.extend(self.compensatedDoorGeo)


            self.Co = []
            for midCrv in midCurves:
                oneCrvCi, oneCrvCo = TrimwithRegions(midCrv, self.compensatedCombineGeo, basePlane)
                # when trimming with opening
                if oneCrvCi != None:
                    # when trimming with window, it will output list
                    if isinstance(oneCrvCo, list):
                        self.Co.extend(oneCrvCo)
                    # when triming with door, it will output one obj
                    else:
                        self.Co.append(oneCrvCo)
                # when trimming with nothing, add original curve
                else:
                    self.Co.extend([oneCrvCo])
            
            self.originalCo = deepcopy(self.Co)
            self.CoGraft = [[c] for c in self.originalCo]
            self.originalCoGraft = [[c] for c in self.originalCo]

            trimedCo = [] # Store shorten Crv
            # print(self.Co)
            for crv in self.Co:
                tForTouch = 10
                crv = crv.Trim(rg.CurveEnd.Start, tForTouch)
                crv = crv.Trim(rg.CurveEnd.End, tForTouch)
                trimedCo.append(crv)


            # Manage window side curve
            self.compensatedOpeningGeoNext = []
            self.compensatedOpeningGeoNext.extend(self.compensatedWindowGeoNext)
            self.compensatedOpeningGeoNext.extend(self.compensatedDoorGeoNext)

            self.compensatedOpeningGeoNext, heightList = sort_geometry(self.compensatedOpeningGeoNext, self.wallFrame)

            self.checkCutting = []
            sideId = []

            for i, (trim_crv, crv) in enumerate(zip(trimedCo, self.Co)):
                for openCrv_next, height in zip(self.compensatedOpeningGeoNext, heightList):
                    openCrv_next_Geo = BoundarySurfaces(openCrv_next)
                    crvProject = Project(crv, openCrv_next_Geo, self.wallFrame.ZAxis)
                    if crvProject != None:
                        dist = crvProject.GetLength()
                        sideTileNum = math.ceil((dist + self.verticalOverlap)/self.minTileLength)
                        stPt = crvProject.PointAtStart
                        endPt = crvProject.PointAtEnd

                        temp_closest_pt_st = openCrv_next.ClosestPoint(stPt)
                        dist_st = temp_closest_pt_st.DistanceTo(stPt)

                        temp_closest_pt_end = openCrv_next.ClosestPoint(endPt)
                        dist_end = temp_closest_pt_end.DistanceTo(endPt)

                        if dist_st < dist_end or abs(dist_st-dist_end)<10:
                            vec = stPt - endPt
                            vec.Unitize()
                            seriesStartPt = endPt

                        else:
                            vec = endPt - stPt
                            vec.Unitize()
                            seriesStartPt = stPt

                        
                        moveSeries = [rg.Transform.Translation(vec*self.minTileLength*k) for k in range(int(sideTileNum+1))]

                        ptSeries = []
                        for trans in moveSeries:
                            pt = copy(seriesStartPt)
                            pt.Transform(trans)
                            ptSeries.append(pt)
                        
                        

                        print("ptSeries", len(ptSeries))
                        splittedCrv = split_curve_by_points(self.CoGraft[i], ptSeries, height)
                        self.checkCutting.append((self.CoGraft[i], ptSeries))
                        # print(splittedCrv[0])
                        # splittedCrv[0] = splittedCrv[0].Extend(rg.CurveEnd.Start, self.verticalOverlap*2, 0)
                        # splittedCrv[-1] = splittedCrv[-1].Extend(rg.CurveEnd.End, self.verticalOverlap*2, 0)

                        sideId.append(i)

                        self.CoGraft[i] = list(splittedCrv)

            
            sideId = list(set(sideId))
            print(sideId)
            extendCo = deepcopy(self.CoGraft)
            for g_index, crvList in enumerate(self.CoGraft):
                if g_index in sideId:
                    temp_list = []
                    for crvId, crv in enumerate(crvList):
                        if abs(crv.GetLength() - self.minTileLength) < 1:
                            pass
                        elif crvId == 0:
                            crv = crv.Extend(rg.CurveEnd.Start, self.verticalOverlap, 0)
                        else:
                            crv = crv.Extend(rg.CurveEnd.End, self.verticalOverlap, 0)
                        temp_list.append(crv)
                else:
                    temp_list = []
                    for crv in crvList:
                        
                        crv = crv.Extend(rg.CurveEnd.Start, self.verticalOverlap, 0)
                        crv = crv.Extend(rg.CurveEnd.End, self.verticalOverlap, 0)
                        temp_list.append(crv)
                
                extendCo[g_index] = temp_list


            extendCoLength = deepcopy(extendCo)
            for gId, group in enumerate(extendCo):
                for cId, crv in enumerate(group):
                    extendCoLength[gId][cId] = crv.GetLength()
            
            self.trimedCo = trimedCo
            return (extendCo, extendCoLength)


    def calculateTarget(self, sourceLength, targetsLength, tolerance):
        def find_combinations(nums, targets):
            def knapsack(items, capacity):
                dp = [0] * (capacity + 1) #[0,0,0,...,0,0,0] it has capacity number of 0
                item_included = [[] for _ in range(capacity + 1)] #[[],[],[],...,[],[],[]] it has capacity number of []
                
                for item in items:
                    for i in range(capacity, item - 1, -1):
                        if dp[i - item] + item > dp[i]:
                            dp[i] = dp[i - item] + item
                            item_included[i] = item_included[i - item] + [item]

                return item_included[capacity]

            def find_closest_number(remaining_nums, target):
                # Find the smallest number in remaining_nums that makes the sum >= target
                for num in sorted(remaining_nums):
                    if num + sum(remaining_nums) >= target:
                        return num
                return None

            all_combinations = []
            for target in targets:
                combination = knapsack(nums, target)
                combination_sum = sum(combination)

                if combination_sum < target and (target-combination_sum)>tolerance:
                    remaining_nums = Counter(nums) - Counter(combination)
                    additional_num = find_closest_number(list(remaining_nums.elements()), target - combination_sum)
                    if additional_num is not None:
                        combination.append(additional_num)

                remaining_nums = Counter(nums) - Counter(combination)
                nums = list(remaining_nums.elements())
                random.shuffle(nums)

                random.shuffle(combination)
                all_combinations.append(combination)

            return all_combinations
        
        targetsLengthflatten = [int(math.ceil(t)) for t in list(chain.from_iterable(targetsLength))]
        sourceLength = [int(s) for s in sourceLength]
        random.shuffle(sourceLength)

        pair = [(t_id, t) for t_id, t in enumerate(targetsLengthflatten)]
        pair.sort(key=lambda pair: pair[1])
        id_sort = [p[0] for p in pair]
        targetsLengthflattenSorted = [p[1] for p in pair]
        combinations = find_combinations(sourceLength, targetsLengthflattenSorted)
        combinations = [originComb for _, originComb in sorted(zip(id_sort, combinations))]

        for target, combination in zip(targetsLengthflatten, combinations):
            print("Target "+ str(target) + " constructed by: "+ str(combination) + " ,the sum is: " + str(sum(combination)))


        def fill_structure_from_flat(flat_list, structure_template):
            flat_iter = iter(flat_list)  # Create an iterator for the flat list

            def fill_structure(structure):
                for i, item in enumerate(structure):
                    if isinstance(item, list):  # If the current item is a list, recurse
                        fill_structure(item)
                    else:
                        structure[i] = next(flat_iter)  # Replace the item with the next flat list item

            fill_structure(structure_template)
            return structure_template
        
        combinationsGraft = fill_structure_from_flat(combinations, targetsLength)
        
        return combinationsGraft


    def generateCladdingByTarget(self, extendCo, originalCo, combinations):
        def massAddition(inputList):
            sumUpList = [0]
            sumNum = 0
            for num in inputList:
                sumNum += num
                sumUpList.append(sumNum)
            return sumUpList[:-1]
        
        def remap_points(original_points, new_points, series_points):
            pt1, pt2 = original_points
            pt3, pt4 = new_points

            # Calculate the vector representing the original and new intervals
            original_vector = pt2 - pt1
            new_vector = pt4 - pt3

            # Function to remap a single point
            def remap_point(point):
                # Calculate the vector from pt1 to the current point
                point_vector = point - pt1

                # Calculate the ratio of the point_vector's length to the original_vector's length
                ratio = point_vector.Length / original_vector.Length

                # Scale the new_vector by this ratio and add to pt3
                return pt3 + new_vector * ratio

            # Remap each point in the series
            return [remap_point(point) for point in series_points]

        
        substructureList = self.replace_with_zeros(originalCo)
        originalCoPtList = self.replace_with_zeros(extendCo)
        originalCoTileGeo = self.replace_with_zeros(extendCo)
        for i, (eachColextendCo, eachColOriginalCo, eachColNums) in enumerate(zip(extendCo, originalCo, combinations)):
            originalCurve = eachColOriginalCo[0]
            originalPts = [originalCurve.PointAtStart, originalCurve.PointAtEnd]
            extendCoJoinedCrv = JoinCurves(eachColextendCo, False)
            extendPts = [extendCoJoinedCrv.PointAtStart, extendCoJoinedCrv.PointAtEnd]

            # transform substructure
            tt = rg.Transform.Translation(self.wallFrame.XAxis*self.gridDist/2 + self.wallFrame.XAxis*self.horizontalOverlap)
            substructure = deepcopy(originalCurve)
            substructure.Transform(tt)
            substructureList[i] = substructure
            
            for j, (oneLineExtendCo, oneLineNums) in enumerate(zip(eachColextendCo, eachColNums)):
                sumUpResult = massAddition(oneLineNums)

                lengPtList = []
                for le in sumUpResult:
                    pt, _, _ = EvaluateLength(oneLineExtendCo, le, False)
                    lengPtList.append(pt)
                lengPtList = remap_points(extendPts, originalPts, lengPtList)
                trans = rg.Transform.Translation(self.wallFrame.XAxis*self.gridDist/2)
                _ = [pt.Transform(trans) for pt in lengPtList]

                # Generate Tile's base line
                oneLineTileBase = []
                for pt, tileDist in zip(lengPtList, oneLineNums):
                    tileLine = LineSDL(pt, -self.wallFrame.YAxis, tileDist)
                    oneLineTileBase.append(tileLine)
                
                # Switch length to width
                oneLineWidthList = [self.number_mapping[number] if number in self.number_mapping else number for number in oneLineNums]

                # Generate Tile Geometry
                oneLineTileGeo = []
                for baseline, tiledist in zip(oneLineTileBase, oneLineWidthList):
                    baseline = baseline.ToNurbsCurve()
                    d = -self.wallFrame.XAxis * tiledist
                    extrudeGeo = Extrude(baseline, d)
                    transHorRot = rg.Transform.Rotation(math.radians(self.horizontalAngle), self.wallFrame.YAxis, baseline.PointAtStart)
                    transVerRot = rg.Transform.Rotation(-math.radians(self.verticalAngle), self.wallFrame.XAxis, baseline.PointAtStart)
                    transHorOverlap = rg.Transform.Translation(self.wallFrame.XAxis*self.horizontalOverlap)
                    extrudeGeo.Transform(transHorRot)
                    extrudeGeo.Transform(transVerRot)
                    extrudeGeo.Transform(transHorOverlap)

                    oneLineTileGeo.append(extrudeGeo)


                originalCoPtList[i][j].extend(lengPtList)
                originalCoTileGeo[i][j].extend(oneLineTileGeo)
        

        self.originalCoTileGeo = originalCoTileGeo
        self.substructureList = substructureList

        return originalCoPtList


    def addSubstructure(self, curveForSubstructure, width, length):
        def create_beam(curve, base_plane, width, height):
            start_point = curve.PointAtStart

            # Create a plane at the start point with the same orientation as the provided plane
            section_plane = rg.Plane(start_point, base_plane.XAxis, base_plane.ZAxis)
            matrix = rg.Transform.Translation(-section_plane.XAxis*width/2 - section_plane.YAxis*height)
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
        
        beamGeoList = []
        for crv in curveForSubstructure:
            beamGeoList.append(create_beam(crv, self.wallFrame, width, length))
        
        return beamGeoList




def initialize_globals():
    global initial_data
    initial_data = initial_data if 'initial_data' in globals() else {}

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

def changePath(dataModified, dataSource):
    pathList = dataSource.Paths

    layerTree = DataTree[object]()
    dataList = dataModified.Branches

    for data, path in zip(dataList, pathList):
        layerTree.AddRange(data, path)
    return layerTree


compoundMaterialObj = CompoundMaterial(material_collection)
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


if init:
    initial_data = {}
else:
    initialize_globals()

    db_dict = DB.all_DB
    windowData = db_dict["windowDB"]
    doorData = db_dict["doorDB"]
    claddingData = db_dict["tileDB"]


    if customizeTile:
        test = generateCladding(windowDB=windowData, doorDB=doorData, claddingDB=claddingData, wallGeo=wallGeo, windowGeo=windowGeo, doorGeo=doorGeo, horizontalOverlap=horiOverlap, verticalOverlap=vertiOverlap, horizontalAngle=horiAngle, verticalAngle=vertiAngle, substructWidth=substructWidth, substructThickness=substructThickness, offsetDist=offsetCladdingDist, tileDimension = customizeTile)
        
    else:
        tileSetting = searchTile.searchTileData
        claddingWidth = tileSetting["claddingWidth"]
        claddingLength = tileSetting["claddingLength"]
        kindNum = tileSetting["kindNum"]
        wWeight = tileSetting["wWeight"]
        lWeight = tileSetting["lWeight"]

        claddingObj = generateCladding(windowDB=windowData, doorDB=doorData, claddingDB=claddingData, wallGeo=wallGeo, windowGeo=windowGeo, doorGeo=doorGeo, claddingWidth=claddingWidth, claddingLength=claddingLength, kindNum=kindNum, wWeight=wWeight, lWeight=lWeight, horizontalOverlap=horiOverlap, verticalOverlap=vertiOverlap, horizontalAngle=horiAngle, verticalAngle=vertiAngle, substructWidth=substructWidth, substructThickness=substructThickness, offsetDist=offsetCladdingDist)


    Co = claddingObj.Co
    CoGraft = claddingObj.CoGraft
    checkCutting = claddingObj.checkCutting
    targetLines = claddingObj.targetLines
    # Output claddingObj
    wallFrame = claddingObj.wallFrame
    comb = th.list_to_tree(claddingObj.combinationGraph)
    originalCoTileGeo = th.list_to_tree(claddingObj.originalCoTileGeo)
    substructureGeo = claddingObj.substructureGeo
    wallForInnerMaterial = claddingObj.wallForInnerGeo
    windowForFinalList = claddingObj.windowForFinalList
    doorForFinalList = claddingObj.doorForFinalList
    orientedDoorGeoList = claddingObj.orientedDoorGeoList
    originalCo = claddingObj.originalCo
    compensatedCombineGeo = claddingObj.compensatedCombineGeo
    compensatedOpeningGeoNext = claddingObj.compensatedOpeningGeoNext
    trimedCo = claddingObj.trimedCo

    # Calculate innerMaterial Part
    offsetted_surface = offset_brep(wallForInnerMaterial, offsetList)

    wallObj = innerMaterialGenerate(offsetted_surface, materialList, material_thickness, moduleDistance, wallFrame)
    allTypeMaterial = wallObj.allTypeMaterial
    checkGeo = wallObj.checkGeo
    allTypeMaterialModule = wallObj.allTypeMaterialModule

    for key in wallObj.materialInfoDict:
        print(key)
        print(wallObj.materialInfoDict[key])

    
    data = th.list_to_tree(allTypeMaterialModule.Branches)
    allTypeMaterialModule = changePath(data, allTypeMaterialModule)

    


