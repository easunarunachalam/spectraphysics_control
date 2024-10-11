# spectraphysics_control
Python object for controlling Spectra-Physics lasers. The `DeepSee` class is a
wrapper around the serial interface to the laser providing convenient methods
in place of unwieldy serial commands.


## Installation
Clone this repository and then move into the top level directory. Then

`pip install .`

## Usage

To initialize a connection to the DeepSee laser use the class method `.instance()` to prevent multiple connections
to the same device.

`deepsee = DeepSee.instance() `

Then you can operate the laser:

```python
deepsee.power_on()
deepsee.set_wavelength(800)
deepsee.open_pump_shutter()
deepsee.open_stokes_shutter()
# do your experiment

deepsee.close() # Reset watchdog, close shuttters, power off, close serial connection
```


## Table of serial commands

While not all commands are wrapped it is possible to send serial commands
directly via `DeepSee.device` which is the underlying pyvisa serial object.

| Serial command | `spectraphysics_control.DeepSee` method|
|----------------|----------------------------|
| ON | `power_on` |
| OFF | `power_off`|
| IRSHUTter | `open_stokes_shutter`/`close_stokes_shutter`|
| IRSHUTter? | `stokes_shutter_state`|
| LCD:BRIGtness | `NotImplemented`|
| MODE RUN | `NotImplemented`|
| MODE ALIGN | `NotImplemented`|
| MODE? | `get_mode`|
| READ:AHIStory? | `NotImplemented`|
| READ:HUM? | `NotImplemented`|
| READ:PCTWarmedup? | `get_pct_warmup`|
| READ:PLASer:DIODe(n):CURRent? | `NotImplemented`|
| READ:PLASer:DIODe(n):TEMPerature? | `NotImplemented`|
| READ:PLASer:DIODe(n):HOURS | `NotImplemented`|
| READ:POWer? |`get_power`|
| READ:WAVelength? |`get_wavelength`|
| SAVe |`NotImplemented`|
| SHUTDOWN | `shutdown`|
| SHUTter (n) | `open_pump_shutter`/`close_pump_shutter` |
| SHUTter? | `pump_shutter_state`|
| TIMer:WATChdog (n) | `set_watchdog_time`|
| WAVelength (nnn) | `set_wavelength` |
| WAVelength? | `get_wavelength`|
| WAVelength:min? | `min_wavelength` (attribute) |
| WAVelength:max? | `max_wavelength` (attribute) |
| CONTrol:MTRMOV (nn.nn) | `set_mtrpos` |
| CONTrol:MTRMOV? | `NotImplemented` |
| CONTrol:DSMPOSition? | `get_mtrpos` |
| \*IDN? | `NotImplemented`|
| \*STB? | `get_status` |

## Status code meanings

Status codes are accessed by querying the laser with `*stb?`. Quick access is
provided by `DeepSee.get_status()`.

| Value | Interpretation |
|-------|----------------|
| 0 to 24 | Initializing |
| 25 | READY to turn on  |
| 26 to 49 | Turning on and/or optimizing |
| 50 | RUN – InSight DeepSee is operational |
| 51 to 59 | Moving to align mode |
| 60 | ALIGN mode (see bit 1) |
| 61 to 69 | Exiting align mode |
| 70 to 127 | Reserved |
