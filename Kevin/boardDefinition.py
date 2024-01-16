class Board:
    def __init__(self, length, width, thickness):
        self.materialType = "board"
        self.length = length
        self.width = width
        self.thickness = thickness


boardObj = Board(length, width, thickness)



class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.boardData= boardObj

board_obj = allData