import Rhino.Geometry as rg
from ghpythonlib.components import Area, SurfaceClosestPoint, EvaluateSurface


basePlane = []
for id, (srfList, matList) in enumerate(zip(surfaceList.Branches, materialList.Branches)):
    if id == 0:
        for srf in srfList:
            uvP = SurfaceClosestPoint(Area(srf)[1], srf)[1]
            frame = EvaluateSurface(srf, uvP)[4]
            basePlane.append(frame)
    

    mat = matList[0]
    print(mat)
