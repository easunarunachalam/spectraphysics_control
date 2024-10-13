from typing import Optional

from qtpy.QtWidgets import QPushButton, QVBoxLayout, QWidget

from .deepsee import DeepSee


class DeepSeeGui(QWidget):
    """
    Create a Qt based gui to control the DeepSee Laser.
    """

    def __init__(self, deepsee: Optional[DeepSee] = None):
        super().__init__()
        self._deepsee = DeepSee.instance() if deepsee is None else deepsee
        layout = QVBoxLayout()
        shutter1 = QPushButton("Pump Shutter")
        shutter1.clicked.connect(self._deepsee.open_pump_shutter)

        layout.addWidget(shutter1)
        shutter2 = QPushButton("Shutter 2")
        layout.addWidget(shutter2)

        self.setLayout(layout)

        # motor_position = QDoubleSpinBox("Motor Fine Tune")

        # wavelength = QSpinBox("Pump Wavelenth")


class ShutterButton(QPushButton):
    def __init__(
        self,
        shutter_name: str,
        initial_state: int,
        button_text_open_close: tuple[str, str],
        color_open_close: tuple[str, str],
    ):

        super().__init__()

        self.setText(f"{shutter_name} -- {button_text_open_close[initial_state]}")

        # self.setColor
