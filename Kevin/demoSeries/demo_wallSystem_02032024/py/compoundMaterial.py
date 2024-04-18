import math

class CompoundMaterial:
    def __init__(self, materialList, DB):
        print("class of CompoundMaterial is running")
        self.materialList = materialList
        self.boardDB = DB["boardDB"]

        self.new_materialList = self.readMaterial(self.materialList)
        self.thicknessList = self.calculateThickness(self.new_materialList)


    def updateMaterial(self, materialList):
        update_materialList = []
        for mat in materialList:
            if mat.materialType == "board" and mat.searchDB:
                useWidth, useLength, useDepth, useQuantity, useId, useObjAttr = self.find_board(self.boardDB, mat.width, mat.length, mat.thickness)
                mat.width = useWidth
                mat.length = useLength
                mat.thickness = useDepth
                mat.attrList = useObjAttr
                update_materialList.append(mat)
            else:
                update_materialList.append(mat)
        
        return update_materialList


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
            
        new_materialList = self.updateMaterial(new_materialList)

        return new_materialList


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
            euclideanDist = math.sqrt((searchWidth - w)**2 + (searchLength - l)**2 + (searchDepth - d)**2)
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

    

    def calculateThickness(self, materialList):
        thicknessList = []
        for mat in materialList:
            # print("hooooooooooo")
            # print(mat.thickness)
            thicknessList.append(mat.thickness)
        return thicknessList