from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QSlider, QWidget, QGridLayout, QLabel, QLineEdit


class SliderWidget(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._minimum = 0
        self._maximum = 1
        self._inputValidator = QIntValidator()
        self._inputValidator.setRange(self._minimum, self._maximum)
        self._input = QLineEdit(self)
        self._input.setValidator(self._inputValidator)
        self._input.setAlignment(Qt.AlignCenter)
        self._maxLabel = QLabel(self)
        self._maxLabel.setAlignment(Qt.AlignCenter)
        self._minLabel = QLabel(self)
        self._minLabel.setAlignment(Qt.AlignCenter)
        self._slider = QSlider(self)
        self._slider.setOrientation(Qt.Horizontal)

        self._layout = QGridLayout(self)
        self._layout.addWidget(self._minLabel, 0, 0, 1, 1)
        self._layout.addWidget(self._slider, 0, 1, 1, 1)
        self._layout.addWidget(self._maxLabel, 0, 2, 1, 1)
        self._layout.addWidget(self._input, 1, 1, 1, 1)
        self.setLayout(self._layout)

        self._input.textEdited.connect(self.setValue)
        self._slider.sliderMoved.connect(self.setValue)

    def setMaximum(self, value: int):
        self._maximum = value
        self._refreshRange()

    def setMinimum(self, value: int):
        self._minimum = value
        self._refreshRange()

    def setValue(self, value):
        if not value:
            return
        value = int(value)
        value = min(max(value, self._minimum), self._maximum)
        self._slider.setSliderPosition(value)
        self._input.setText(str(value))

    def _refreshRange(self):
        self._minLabel.setText(str(self._minimum))
        self._slider.setRange(self._minimum, self._maximum)
        self._maxLabel.setText(str(self._maximum))
        self._inputValidator.setRange(self._minimum, self._maximum)

    def value(self):
        return self._slider.value()
