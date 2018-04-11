from PyQt5.QtWidgets import QApplication, QWidget, QLayout, QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPaintEvent, QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import Qt
import sys

def layout_widgets(layout):
   return (layout.itemAt(i) for i in range(layout.count()))

class StepperCheckpoint(QWidget):
    def __init__(self, id, area, visualSize):
        QWidget.__init__(self)
        self.id = id
        self.area = area
        self.visualSize = visualSize

    def setDrawParameters(self, x, area, visualSize):
        self.area = area
        self.visualSize = visualSize
        self.x = x
        print(self.x)

    def paintEvent(self, paintEvent):
        # return

        # visualSize = self.width()*self.visualRatio

        painter = QPainter(self)
        painter.setPen(QPen(Qt.NoPen))

        # painter.setBrush(QBrush(Qt.lightGray))
        # painter.drawRect(0,0,self.width(), self.height())

        painter.setBrush(QBrush(QColor(0,200,255,150)))
        left = self.width()/2 - self.visualSize/2
        top = self.height()/2 - self.visualSize/2
        left = self.x - self.visualSize/2

        painter.drawPie(left, top, self.visualSize, self.visualSize, 0, 5760*(16*360))


class BridgePainter(QPainter):
    def paintBridges(self):
        pass

class StepperWidget(QWidget):
    def __init__(self, numStep, parent=None, marginY=5, checkpointCover=0.5):
        QWidget.__init__(self, parent)

        self.numStep = numStep
        self.marginY = marginY
        self.checkpointCover = checkpointCover
        self.checkpoints = dict()

        self.__calculateCheckpointArea()
        self.__calculateCheckpointVisualSize()
        self.__calculateBridgeLength()
        self.__setProperMargin()

        self.setMinimumSize(200, 50)

        print('width:', self.width())
        print('area:', self.checkpointArea)
        print('visual:', self.checkpointVisualSize)
        print('bridge:', self.bridgeLength)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        for i in range(numStep):
            self.checkpoints[i] = StepperCheckpoint(i, self.checkpointArea, self.checkpointVisualSize)
            layout.addWidget(self.checkpoints[i])

        self.setLayout(layout)

    def __calculateCheckpointArea(self):
        checkpointArea = self.width()/(self.numStep+1)

        if checkpointArea + 2*self.marginY > self.height():
            checkpointArea = self.height() - 2*self.marginY

        self.checkpointArea = checkpointArea

    def __calculateCheckpointVisualSize(self):
        self.checkpointVisualSize = self.checkpointCover * self.checkpointArea

    def __calculateBridgeLength(self):
        w, area, visual, step = self.width(), self.checkpointArea, self.checkpointVisualSize, self.numStep
        self.bridgeLength = ((w - area) - visual*(step-1) - area)/(step-1)

    def __setProperMargin(self):
        self.setContentsMargins(self.checkpointArea / 2, self.marginY, self.checkpointArea / 2, self.marginY)

    def paintEvent(self, paintEvent):
        self.__calculateCheckpointArea()
        self.__calculateCheckpointVisualSize()
        self.__calculateBridgeLength()
        self.__setProperMargin()

        print()
        print('width:', self.width())
        print('area:', self.checkpointArea)
        print('visual:', self.checkpointVisualSize)
        print('bridge:', self.bridgeLength)

        # for checkpoint in self.checkpoints.values():
        #     checkpoint.setDrawParameters(self.checkpointArea, self
        #     checkpoint.setDrawParameters(self.checkpointArea, self.checkpointVisualSize)

        checkpointX = []
        t = (self.width()-self.checkpointArea)/self.numStep + 1
        halfVisual = self.checkpointVisualSize/2
        edgeArea = self.checkpointArea/2

        painter = QPainter(self)
        for i in range(self.numStep-1):
            x1 = self.checkpointArea + halfVisual + i*(self.checkpointVisualSize + self.bridgeLength)
            x2 = x1 + self.bridgeLength
            y = self.height()/2
            painter.drawLine(x1, y, x2, y)

            checkpointX.append(x1 - edgeArea - i*t - halfVisual)
        checkpointX.append(x2 - edgeArea - (self.numStep-1)*t + halfVisual)

        for checkpoint, x in zip(self.checkpoints.values(), checkpointX):
            checkpoint.setDrawParameters(x, self.checkpointArea, self.checkpointVisualSize)

        painter.drawLine(0, 0, self.width(), self.height())
        painter.drawLine(self.checkpointArea/2, 0, self.checkpointArea/2, self.height())
        painter.drawLine(self.width() - self.checkpointArea/2, 0, self.width()-self.checkpointArea/2, self.height())

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = QWidget()
    # layout = QVBoxLayout()
    # widget = StepperWidget(5,parent=window)
    # layout.addWidget(widget)
    # layout.setContentsMargins(0,0,0,0)
    # window.setLayout(layout)
    window = StepperWidget(4)
    window.show()

    sys.exit(app.exec_())
