from superqt.fonticon import icon

import warnings
from typing import Any, Union

from fonticon_mdi6 import MDI6
from qtpy.QtCore import QSize, Qt, QTimer
from qtpy.QtGui import QPalette, QColor
from qtpy.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget, QGridLayout, QFormLayout, QLineEdit
# from superqt.fonticon import icon
from superqt.utils import signals_blocked

COLOR_TYPE = Union[
    QColor,
    int,
    str,
    Qt.GlobalColor,
    "tuple[int, int, int, int]",
    "tuple[int, int, int]",
]


class LaserControlWidget(QWidget):
    """A Widget to control a Spectra-Physics laser.

    Parameters
    ----------
    shutter_device: str:
        The shutter device Label.
    autoshutter: bool
        If True, a checkbox controlling the Micro-Manager autoshutter
        is added to the layout.
    parent : QWidget | None
        Optional parent widget. By default, None.
    """

    def __init__(
        self,
        laser_controller,
        *,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)

        self.laser_controller = laser_controller

        self._icon_open: str = MDI6.hexagon_outline
        self._icon_closed: str = MDI6.hexagon_slice_6
        self._icon_color_open: COLOR_TYPE = (0, 255, 0)
        self._icon_color_closed: COLOR_TYPE = "magenta"
        self._icon_size: int = 25
        self._button_text_on: str = "ON"
        self._button_text_off: str = "OFF"
        self._button_text_open: str = "OPEN"
        self._button_text_closed: str = "CLOSED"

        # Initialize the widget
        self.resize(230, 350)
        # self.move(350, 10)
        # self.setWindowTitle("Laser Control")
        self.setWindowTitle("Spectra-Physics Laser Control")
        self.raise_()

        self.layout = QFormLayout()

        self.status_label = QLabel("Laser status:")
        self.status_string = QLineEdit("")
        self.status_string.setReadOnly(True)
        self.layout.addRow(self.status_label, self.status_string)

        self.laser_onoff_label = QLabel("Laser On/Off:")
        self.laser_status = 0 # 0 = closed, 1 = open
        self.laser_onoff_button = QPushButton(text=self._button_text_off)
        sizepolicy_btn = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.laser_onoff_button.setSizePolicy(sizepolicy_btn)
        self.laser_onoff_button.setIcon(
            icon(self._icon_closed, color=self._icon_color_closed)
        )
        self.laser_onoff_button.setIconSize(QSize(self._icon_size, self._icon_size))
        self.laser_onoff_button.clicked.connect(self.on_laser_onoff_button_clicked)
        self.layout.addRow(self.laser_onoff_label, self.laser_onoff_button)

        self.toggle_mode_label = QLabel("Run / Align mode:")
        self.toggle_mode_status = "Run"
        self.toggle_mode_button = QPushButton("Running mode (press to switch to Align)", self)
        self.toggle_mode_button.setCheckable(True) # Makes the button toggleable
        self.layout.addRow(self.toggle_mode_label, self.toggle_mode_button)

        self.power_label = QLabel("Power (W):")
        self.power_status = QLineEdit("")
        self.power_status.setReadOnly(True)
        self.layout.addRow(self.power_label, self.power_status)

        self.wavelength_label = QLabel("Wavelength (nm):")
        self.wavelength_status = QLineEdit("")
        self.wavelength_status.setReadOnly(True)
        self.wavelength_edit = QLineEdit()
        self.wavelength_status_and_edit = QHBoxLayout()
        self.wavelength_status_and_edit.addWidget(self.wavelength_status)
        self.wavelength_status_and_edit.addWidget(self.wavelength_edit)
        self.layout.addRow(self.wavelength_label, self.wavelength_status_and_edit)

        self.ds_label = QLabel("Motor Pos:")
        self.ds_status = QLineEdit("")
        self.ds_status.setReadOnly(True)
        self.ds_edit = QLineEdit()
        self.ds_status_and_edit = QHBoxLayout()
        self.ds_status_and_edit.addWidget(self.ds_status)
        self.ds_status_and_edit.addWidget(self.ds_edit)
        self.layout.addRow(self.ds_label, self.ds_status_and_edit)

        self.pump_shutter_label = QLabel("Pump Beam Shutter:")
        self.pump_shutter_status = 0 # 0 = closed, 1 = open
        self.pump_shutter_button = QPushButton(text=self._button_text_closed)
        sizepolicy_btn = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.pump_shutter_button.setSizePolicy(sizepolicy_btn)
        self.pump_shutter_button.setIcon(
            icon(self._icon_closed, color=self._icon_color_closed)
        )
        self.pump_shutter_button.setIconSize(QSize(self._icon_size, self._icon_size))
        self.pump_shutter_button.clicked.connect(self.on_pump_shutter_button_clicked)
        self.layout.addRow(self.pump_shutter_label, self.pump_shutter_button)

        self.IR_shutter_label = QLabel("IR Beam Shutter:")
        self.IR_shutter_status = 0 # 0 = closed, 1 = open
        self.IR_shutter_button = QPushButton(text=self._button_text_closed)
        sizepolicy_btn = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.IR_shutter_button.setSizePolicy(sizepolicy_btn)
        self.IR_shutter_button.setIcon(
            icon(self._icon_closed, color=self._icon_color_closed)
        )
        self.IR_shutter_button.setIconSize(QSize(self._icon_size, self._icon_size))
        self.IR_shutter_button.clicked.connect(self.on_IR_shutter_button_clicked)
        self.layout.addRow(self.IR_shutter_label, self.IR_shutter_button)

        self.mode_label = QLabel("Mode:")
        self.mode_status = QLineEdit("")
        self.mode_status.setReadOnly(True)
        self.layout.addRow(self.mode_label, self.mode_status)

        self.temperature_label = QLabel("Temperature:")
        self.temperature_status = QLineEdit("")
        self.temperature_status.setReadOnly(True)
        self.layout.addRow(self.temperature_label, self.temperature_status)

        self.humidity_label = QLabel("Humidity:")
        self.humidity_status = QLineEdit("")
        self.humidity_status.setReadOnly(True)
        self.layout.addRow(self.humidity_label, self.humidity_status)

        self.current_label = QLabel("Current:")
        self.current_status = QLineEdit("")
        self.current_status.setReadOnly(True)
        self.layout.addRow(self.current_label, self.current_status)

        self.history_buffer_label = QLabel("History Buffer:")
        self.history_buffer_status = QLineEdit("")
        self.history_buffer_status.setReadOnly(True)
        self.layout.addRow(self.history_buffer_label, self.history_buffer_status)

        self.setLayout(self.layout)

        # periodically update internal status variables
        self.timer_updateinternals = QTimer(self)
        self.timer_updateinternals.timeout.connect(self.update_internal_status)
        self.timer_updateinternals.start(1000)

        # periodically update displayed status
        self.timer_displaystatus = QTimer(self)
        self.timer_displaystatus.timeout.connect(self.update_display_status)
        self.timer_displaystatus.start(500)

        # Connect signals to methods
        self.toggle_mode_button.clicked.connect(self.on_toggle_mode_change)
        self.wavelength_edit.editingFinished.connect(self.update_wavelength)
        self.ds_edit.editingFinished.connect(self.update_motor_position)

    def update_internal_status(self):
        """
        Update laser status indicators
        """

        self.laser_status = self.laser_controller.get_status()
        if self.laser_status == 50:
            self.laser_onoff_button.setIcon(icon(self._icon_open, color=self._icon_color_open))
            self.laser_onoff_button.setText(self._button_text_on)
            self.toggle_mode_status = "Run"
        elif self.laser_status == 60:
            self.laser_onoff_button.setIcon(icon(self._icon_open, color=self._icon_color_open))
            self.laser_onoff_button.setText(self._button_text_on)
            self.toggle_mode_status = "Align"
        else:
            self.laser_onoff_button.setIcon(icon(self._icon_closed, color=self._icon_color_closed))
            self.laser_onoff_button.setText(self._button_text_off)

        

        self.pump_shutter_status = self.laser_controller.pump_shutter_state()
        if self.pump_shutter_status == 0:
            self.pump_shutter_button.setIcon(icon(self._icon_closed, color=self._icon_color_closed))
            self.pump_shutter_button.setText(self._button_text_closed)
        elif self.pump_shutter_status == 1:
            self.pump_shutter_button.setIcon(icon(self._icon_open, color=self._icon_color_open))
            self.pump_shutter_button.setText(self._button_text_open)


        self.IR_shutter_status = self.laser_controller.IR_shutter_state()
        if self.IR_shutter_status == 0:
            self.IR_shutter_button.setIcon(icon(self._icon_closed, color=self._icon_color_closed))
            self.IR_shutter_button.setText(self._button_text_closed)
        elif self.IR_shutter_status == 1:
            self.IR_shutter_button.setIcon(icon(self._icon_open, color=self._icon_color_open))
            self.IR_shutter_button.setText(self._button_text_open)


    def update_display_status(self):
        """
        Update laser status indicators
        """

        try:

            if (self.laser_status >= 0) & (self.laser_status <= 24):
                self.status_string.setText("Initializing... (not ready to turn on)")
            elif (self.laser_status == 25):
                self.status_string.setText("Ready to turn on")
            elif (self.laser_status >= 26) & (self.laser_status <= 49):
                self.status_string.setText("Turning on...")
            elif (self.laser_status == 50):
                self.status_string.setText("Running mode")
            elif (self.laser_status >= 51) & (self.laser_status <= 59):
                self.status_string.setText("Initializing alignment mode...")
            elif (self.laser_status == 60):
                self.status_string.setText("Alignment mode")
            elif (self.laser_status >= 61) & (self.laser_status <= 69):
                self.status_string.setText("Exiting alignment mode...")
            elif (self.laser_status >= 70) & (self.laser_status <= 127):
                code = self.laser_status
                self.status_string.setText(f"Reserved status code {code:3d}")
            else:
                code = self.laser_status
                self.status_string.setText(f"Invalid status code {code:3d}")

            value = self.laser_controller.get_power()
            self.power_status.setText(f"{value:2.2f}")

            value = self.laser_controller.get_wavelength()
            self.wavelength_status.setText(f"{value:3d}")

            value = self.laser_controller.get_mtrpos()
            self.ds_status.setText(f"{value:2.2f}")

            value = self.laser_controller.get_mode()
            self.mode_status.setText(value)

            value = self.laser_controller.get_temperature()
            self.temperature_status.setText(f"{value:2.2f}")

            value = self.laser_controller.get_humidity()
            self.humidity_status.setText(f"{value:2.3f}")

            value = self.laser_controller.get_current()
            self.current_status.setText(f"{value:2.2f}")

            value = self.laser_controller.get_history()
            # only show last 8 status codes
            self.history_buffer_status.setText(value[:32])

        except:
            print("Error updating display status (laser control)")




    def on_toggle_mode_change(self) -> None:

        if self.toggle_mode_status == "Run":
            # current mode = run -> need to change to align
            self.toggle_mode_status = "Align"
            self.laser_controller.set_mode_align()
            self.toggle_mode_button.setText("Alignment mode (press to switch to Run)")
        elif self.toggle_mode_status == "Align":
            # current mode = align -> need to change to run
            self.toggle_mode_status = "Run"
            self.laser_controller.set_mode_run()
            self.toggle_mode_button.setText("Running mode (press to switch to Alignment)")

    def on_pump_shutter_button_clicked(self) -> None:

        if self.pump_shutter_status == 0:
            # currently closed -> need to open
            self.laser_controller.open_pump_shutter()
        elif self.pump_shutter_status == 1:
            # currently open -> need to close
            self.laser_controller.close_pump_shutter()
        else:
            # unknown status, close shutter
            value = self.pump_shutter_status
            self.laser_controller.close_pump_shutter()
            raise ValueError(f"Unknown pump shutter status ({value:d}).")

    def on_IR_shutter_button_clicked(self) -> None:

        if self.IR_shutter_status == 0:
            # currently closed -> need to open
            self.laser_controller.open_IR_shutter()
        elif self.IR_shutter_status == 1:
            # currently open -> need to close
            self.laser_controller.close_IR_shutter()
        else:
            # unknown status, close shutter
            value = self.IR_shutter_status
            self.laser_controller.close_IR_shutter()
            raise ValueError(f"Unknown IR shutter status ({value:d}).")

    def on_laser_onoff_button_clicked(self) -> None:

        if self.laser_status == 25:
            # currently off -> need to turn on
            self.laser_controller.power_on(blocking=False)
            self.status_string.setText("Turning on...")
            # self.status_string.setText("Turning on... (other commands blocked)")
        elif self.laser_status == 50:
            # currently on -> need to turn off
            self.laser_controller.power_off()
        else:
            # unknown status, close shutter
            value = self.pump_shutter_status
            self.laser_controller.close_pump_shutter()
            raise ValueError(f"Unknown pump shutter status ({value:d}).")

    def update_wavelength(self):
        try:
            new_wavelength = float(self.wavelength_edit.text())
            self.laser_controller.set_wavelength(new_wavelength)  # Update the laser wavelength
            self.wavelength_status.setText(f"{new_wavelength:.2f}")  # Update status display
        except ValueError:
            warnings.warn("Invalid wavelength value. Please enter a numeric value.")

    def update_motor_position(self):
        try:
            new_position = float(self.ds_edit.text())
            self.laser_controller.set_mtrpos(new_position)  # Update motor position
            self.ds_status.setText(f"{new_position:.2f}")  # Update status display
        except ValueError:
            warnings.warn("Invalid motor position value. Please enter a numeric value.")

    def read_wavelength(self):
        """
        Return wavelength value in GUI.
        Intended to allow you to avoid querying the laser itself.
        """
        return int(self.wavelength_status.text())

    def read_status(self):
        """
        Return status value that was read during previous widget update.
        Intended to allow you to avoid querying the laser itself.
        """
        return int(self.laser_status)