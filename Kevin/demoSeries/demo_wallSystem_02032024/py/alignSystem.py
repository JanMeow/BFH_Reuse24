import Rhino.Geometry as rg
from ghpythonlib.components import Explode, LineSDL, CurveXCurve
from copy import deepcopy

def alignSystem(windowGeo, grid, toler, basePlane):

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
            # wholePair_opening = []
            # for pt in newPts:
            #     firMoveTrace = LineSDL(pt, crvDir, toler).ToNurbsCurve()
            #     secMoveTrace = LineSDL(pt, -crvDir, toler).ToNurbsCurve()

            #     for crvKey in checkLines['opening']:
            #         crv = checkLines['opening'][crvKey]
            #         firCutPt = CurveXCurve(crv.ToNurbsCurve(), firMoveTrace)[0]
            #         secCutPt = CurveXCurve(crv.ToNurbsCurve(), secMoveTrace)[0]
            #         if firCutPt and firCutPt != pt:
            #             wholePair_opening.append((pt,firCutPt))
            #         if secCutPt and secCutPt != pt:
            #             wholePair_opening.append((pt,secCutPt))
            #             print(pt,secCutPt)
            
            
            # if len(wholePair_opening)!=0:
            #     wholePair_opening = sorted(wholePair_opening, key=lambda pair: pair[0].DistanceTo(pair[1]))
            #     closestPair = wholePair_opening[0]

            #     if not closestPair[1].DistanceTo(closestPair[0])<0.1:
            #         print("hiiii")
            #         resultVec = rg.Vector3d(closestPair[1]-closestPair[0])
            #         resultVec.Unitize()
            #         resultVec *= 0.1
            #         matrix = rg.Transform.Translation(resultVec)
            #         checkLines['opening'][crvKey].Transform(matrix)
            #         return (resultVec, True)
            #     else:
            #         return (rg.Vector3d(0,0,0), True)
            
            # else:
            #     return (rg.Vector3d(0,0,0), True)


    # Whole lines involved in this system, having opening lines and grid lines
    checkLinesFacade = grid
    checkLinesOpening = []

    pt_rect = []
    for geo in windowGeo:
        if isinstance(geo, rg.Rectangle3d):
            lines, vertics = Explode(geo, True)
            pt_rect.append((vertics[:-1], geo))
            checkLinesOpening.extend(lines)
    
    horiVec, vertiVec = basePlane.XAxis, basePlane.YAxis
    horiLinesFacade = []
    vertiLinesFacade = []
    for crv in checkLinesFacade:
        vecCrv = crv.PointAtEnd - crv.PointAtStart
        if rg.Vector3d.CrossProduct(horiVec,vecCrv).IsZero:
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
    
    see = []
    for pts, geo in pt_rect:
        horiVec, fixedBool = findMoveDist(pts, wholeLinesDict, basePlane, 'hori')
        vertiVec, fixedBool = findMoveDist(pts, wholeLinesDict, basePlane, 'verti')
        crossVec = rg.Vector3d.Add(horiVec, vertiVec)

        see.append(crossVec)


    return see




a= alignSystem(windowGeo, grid, toler, basePlane)
