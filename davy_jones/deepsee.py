from __future__ import annotations

import time
import warnings

import serial
from pyvisa import ResourceManager
from pyvisa.resources.serial import SerialInstrument
from serial import SerialException
from serial.tools import list_ports

from .status_codes import state_number


def port_map() -> None:
    for p in list_ports.comports():
        try:
            s_test = serial.Serial(p.name)
            s_test.close()
            print(p)
        except SerialException:
            pass


_instance = None


class DeepSee:
    @classmethod
    def instance(cls, port_name: str = "ASRL4::INSTR", disable_watchdog: bool = True, fake: bool = False) -> DeepSee:
        global _instance
        if _instance is None:
            _instance = cls(port_name, disable_watchdog, fake)
        return _instance

    def __init__(self, port_name: str = "ASRL4::INSTR", disable_watchdog: bool = True, fake: bool = False):
        if not fake:
            self.rm = ResourceManager()
            self.device = self._setup_device(port_name)
            wdt = self.get_watchdog_time()
            if (wdt > 0) and disable_watchdog: 
                self.set_watchdog_time(0)
                print("Disabling watchdog timer.")
            elif wdt>0:
                warnings.warn(f"Found watchdog timer set to {wdt:0.1f} seconds.")
        else:
            from .fake_device import FakeDevice

            self.device = FakeDevice()

        self.min_wavelength = int(self.device.query("wav:min?"))
        self.max_wavelenth = int(self.device.query("wav:max?"))

    def _setup_device(self, port_name: str) -> SerialInstrument:
        """
        Open a serial connection to the laser and configure some basic
        communication settings as specified in the user manual

        Parameters
        ----------
        port_name: str
            Name of the laser's connection.

        Returns
        -------
        device: serial.SerialInstrument
            pyvisa serial device object.
        """
        device = ResourceManager().open_resource(port_name)
        device.baud_rate = 115200
        device.read_termination = "\n"
        device.write_termination = "\n"
        return device

    def power_on(self, blocking: bool = True, verbose: bool = False) -> None:
        """
        Parameters
        ----------
        blocking: bool default True
            Whether or not to block futher processing while the device powers
            on. This typically takes a few minutes.
        verbose : bool = False
            Whether to print status updates from the laser during power up and
            optimization.

        Returns
        -------
        None

        """

        status = self.get_status()

        if status != 25:
            raise ValueError(
                f"DeepSee is not ready to turn on. Found status number {status}"
            )
        self.device.write("on")

        if blocking:
            count = 0
            while True:
                time.sleep(1)
                count += 1
                status = self.get_status()
                if verbose:
                    print(f"{count} s - {status=:03d}\r")

                if status == 50:
                    break

    def power_off(self):
        """
        Turn off the laser diodes but leave the ovens on for quick restart.
        To fully power down the system see shutdown.
        """
        self.device.write("off")

    def shutdown(self):
        """
        Fully power down the laser to prepare to shut of the power main.
        """
        self.device.write("shutdown")

    def get_status(self) -> int:
        """
        Get the status number of the system. See Appendix B of the user manual
        or the table in the README of this library for meanings of each number.
        """
        status = self.device.query("*stb?")
        return state_number(status)

    def set_wavelength(self, wav: int) -> None:
        """
        Set the wavelength of the pump laser

        Parameters
        ----------
        wav: int
            Desired wavelength in nm

        Returns
        -------
        None

        """

        wav = int(wav)
        low = self.min_wavelength
        high = self.max_wavelenth

        if (self.min_wavelength > wav) or (self.max_wavelenth < wav):
            raise ValueError(f"Require {low} <= wav <= {high}. Found {wav=}.")

        self.device.write(f"wav {wav}")

    def get_wavelength(self) -> int:
        """
        Get the current wavelength of the pump beam.
        """

        return int(self.device.query("read:wav?"))

    def get_power(self) -> int:
        """
        Get the current power.
        """

        return float(self.device.query("read:pow?"))

    def get_mode(self) -> int:
        """
        Get the current mode.
        """

        return self.device.query("MODE?")

    def get_mtrpos(self) -> int:
        """
        Get the current DeepSee motor position.
        """

        return float(self.device.query("control:dsmpos?"))

    def set_mtrpos(self, pos: float) -> None:
        """
        Set target DeepSee motor position.
        """

        self.device.write(f"control:mtrmov {pos}")

    def get_pct_warmup(self) -> int:
        """
        Get the current warmup state.
        """

        return int(self.device.query("read:pctwarmedup?"))

    def open_pump_shutter(self)-> None:
        """
        Open the pump beam shutter.
        """
        self.device.write("shut 1")

    def open_stokes_shutter(self) -> None:
        """
        Open the stokes/IR/fixed beam shutter.
        """
        self.device.write("irshut 1")

    def pump_shutter_state(self) -> bool:
        status = int(self.device.query("*stb?"))
        bit_mask = 0x00000004
        return bool(status & bit_mask)

    def stokes_shutter_state(self) -> bool:
        status = self.device.query("*stb?")
        bit_mask = 0x00000008
        return bool(status & bit_mask)

    def close_pump_shutter(self):
        """
        Close the pump beam shutter.
        """
        self.device.write("shut 0")

    def close_stokes_shutter(self):
        """
        Close the stokes/IR/fixed beam shutter
        """

        self.device.write("irshut 0")

    def get_watchdog_time(self) -> float:
        """
        Get the current watchdog time in seconds. This is the time interval
        where if the laser does not receive a communication from the computer,
        it will power off to prevent emission.
        """

        return float(self.device.query("tim:watc?"))

    def set_watchdog_time(self, seconds: int) -> None:
        """
        Set the watchdog time -  time interval
        where if the laser does not receive a communication from the computer,
        it will power off to prevent emission. Set the watchdog timer to 0 to
        disable the watchdog (recommended for programmatic control).

        Parameters
        ----------
        seconds: int
            Desired watchdog time in seconds.

        Returns
        -------
        None
        """
        self.device.write(f"tim:watc {seconds}")

    def close(self):
        self.set_watchdog_time(3)
        self.close_pump_shutter()
        self.close_stokes_shutter()
        self.power_off()
        self.device.close()
