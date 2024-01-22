class Board:
    def __init__(self, length, width, thickness, direction):
        self.materialType = "board"
        self.length = length
        self.width = width
        self.thickness = thickness
        self.direction = direction


boardObj = Board(length, width, thickness, direction)



class classForOutput:
    def __init__(self):
        pass

allData = classForOutput()
allData.boardData= boardObj

board_obj = allData