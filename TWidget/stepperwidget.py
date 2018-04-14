from PyQt5.QtWidgets import QApplication, QWidget, QLayout, QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPaintEvent, QPainter, QPen, QBrush, QColor, QMouseEvent, QTextOption
from PyQt5.QtCore import Qt, QRectF
import sys


def layout_widgets(layout):
    return (layout.itemAt(i) for i in range(layout.count()))


class StepperCheckpoint(QWidget):
    STATE_PASSIVE = 0
    STATE_ACTIVE = 1
    STATE_CURRENT = 2

    def __init__(self, id, area, visualSize, onClick, initState=STATE_PASSIVE):
        QWidget.__init__(self)
        self.id = id
        self.area = area
        self.visualSize = visualSize
        self.state = initState
        self.onClick = onClick
        self.primaryText = str(id)
        self.secondaryText = "hello"

        self.setMouseTracking(True)

    def setState(self, state):
        assert state in [self.STATE_CURRENT, self.STATE_ACTIVE, self.STATE_PASSIVE]
        self.state = state

    def setOnClick(self, onClick):
        self.onClick = onClick

    def setPrimaryText(self, text):
        self.primaryText = text

    def setSecondaryText(self, text):
        self.secondaryText = text

    def setDrawParameters(self, x, area, visualSize):
        self.area = area
        self.visualSize = visualSize
        self.x = x

    def paintEvent(self, paintEvent):
        # return

        painter = QPainter(self)
        painter.setPen(QPen(Qt.NoPen))

        # painter.setBrush(QBrush(Qt.lightGray))
        # painter.drawRect(0,0,self.width(), self.height())

        if self.state == self.STATE_PASSIVE:
            painter.setBrush(QBrush(QColor(0,200,255,30)))
        elif self.state == self.STATE_ACTIVE:
            painter.setBrush(QBrush(QColor(0,200,255,100)))
        elif self.state == self.STATE_CURRENT:
            painter.setBrush(QBrush(QColor(0, 200, 255, 255)))

        top = self.height()/2 - self.visualSize/2
        left = self.x - self.visualSize/2

        painter.drawPie(left, top, self.visualSize, self.visualSize, 0, 5760*(16*360))

        painter.setPen(QPen(QColor(0,0,0)))
        painter.drawText(QRectF(left, top, self.visualSize, self.visualSize), Qt.AlignCenter, self.primaryText)
        painter.drawText(QRectF(left-self.visualSize, top+self.visualSize, self.visualSize*3, self.visualSize/2), Qt.AlignCenter, self.secondaryText)


    def checkMouse(self, mx, my):
        mid = self.width()/2, self.height()/2
        lineardist = abs(mx - mid[0]), abs(my - mid[1])
        dist = (lineardist[0]**2 + lineardist[1]**2)**0.5
        return dist <= self.visualSize/2

    def mousePressEvent(self, event):
        if self.checkMouse(event.x(), event.y()):
            print(self.id)
            self.onClick(self.id)

    def mouseMoveEvent(self, event):
        print(self.checkMouse(event.x(), event.y()))


class StepperWidget(QWidget):
    def __init__(self, numStep, parent=None, marginY=5, checkpointCover=0.5):
        QWidget.__init__(self, parent)

        self.numStep = numStep
        self.marginY = marginY
        self.checkpointCover = checkpointCover
        self.checkpoints = dict()
        self.currentStep = 0

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
            self.checkpoints[i] = StepperCheckpoint(i, self.checkpointArea, self.checkpointVisualSize, self.__onClickCheckpoint)
            layout.addWidget(self.checkpoints[i])

        self.setLayout(layout)
        self.setCurrentStep(0)

    def setCurrentStep(self, currentStep):
        self.currentStep = currentStep

        for i, checkpoint in self.checkpoints.items():
            if i < currentStep:
                print('---')
                checkpoint.setState(StepperCheckpoint.STATE_ACTIVE)
            elif i == currentStep:
                checkpoint.setState(StepperCheckpoint.STATE_CURRENT)
            elif i > currentStep:
                checkpoint.setState(StepperCheckpoint.STATE_PASSIVE)

        self.update()

    def setOnClickCheckpoint(self, onClick):
        for checkpoint in self.checkpoints.values():
            checkpoint.setOnClick(onClick)

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

    def __onClickCheckpoint(self, id):
        self.setCurrentStep(id)

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

        # painter.drawLine(0, 0, self.width(), self.height())
        # painter.drawLine(self.checkpointArea/2, 0, self.checkpointArea/2, self.height())
        # painter.drawLine(self.width() - self.checkpointArea/2, 0, self.width()-self.checkpointArea/2, self.height())



if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = QWidget()
    # layout = QVBoxLayout()
    # widget = StepperWidget(5,parent=window)
    # layout.addWidget(widget)
    # layout.setContentsMargins(0,0,0,0)
    # window.setLayout(layout)
    window = StepperWidget(4)
    window.setCurrentStep(2)
    window.show()

    sys.exit(app.exec_())
