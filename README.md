# TSGRain

Tennis court irrigation controller for TSG Stadtbergen (Germany). The current
hardware setup allows to manually control irrigition of up to seven tennis
courts. It can easily be expanded by cheap hardware to more than seven courts.

The repository contains Python 3 software which runs on a *Raspberry Pi 3B
Plus* under Debian Linux (currently Debian 10). 

This work is based on the bachelor thesis of Christian Graber, titled
"Entwicklung einer Zeitsteuerung zur Bewässerung von Tennisanlagen mittels
lokaler Steuerung und Web-Oberfläche", Hochschule Augsburg, 2020. I was the
supervisor of this thesis. It consists of two parts, a hardware part which
interfaces the RPi to external hardware, and a software part. The software is
split into a controller process and a website process.  The hardware
design remained unchanged after the thesis, the software part (mainly the 
controller process) has been rewritten by me.

## Hardware 

The RPi3 must be connected to three external hardware components. All of them
are driven by the same I2C bus, pins 3 (SDA) and 5 (SCL) of the RPi:

1. MCP23017 I/O Expander Nr. 1 (I2C address 0x27)

   This expander drives up to eight relais with opto-couplers on PORTB. In our
   case the relais drive 24V AC magnetic valves which open the water inflow to
   irrigate the courts.  Between the PORTB signals and the relais inputs you
   can optionally add up to eight switches each with three ways: constantly
   off, constantly on, and control via RPi.

   PORTA is used to drive LEDs which reflect the status of the relais outputs
   (common cathode).

   No interrupt lines are used.


2. MCP23017 I/O Expander Nr. 2 (I2C address 0x23)

   This expander reads up to eight push buttons on PORTA.  The buttons are 
   active low when pushed. The interrupt line of the MCP is connected to RPi 
   GPIO17.

   PORTB is used to drive a RGB-LED to display the status of the controller 
   (common cathode).


3. DS3231 Real-Time Clock  (I2C address 0x68)

   The battery-backed RTC clock is used to set the system time after rebooting
   the RPi. No interrupt line is used.
   
Finally a single push button is connected (active low) to GPIO22. This button
is used as a reboot/shutdown button.

In summary, you need only one I2C bus (SCL, SDA) and two GPIO pins to interface
all the needed external hardware. In principle it would be no problem to move
from the RPi to a similar Embedded Linux hardware, e.g. the *Beaglebone Black*.


## Installation

1. Make a directory `tsgrain` in the RPi home directory (e.g. `/home/pi/tsgrain`)
   and copy all the files in this directory into it.

2. Install the following Python 3 packages, if you don't already have them:

   - RPi.GPIO (pypi.org/project/RPi.GPIO)
   - python3-smbus (for I2C access)
   - schedule (https://schedule.readthedocs.io)
   - TinyDB (https://tinydb.readthedocs.io)

3. See a few user definable settings in conf.py.

4. Set the `PYTHONPATH` environment variable to `/home/pi/tsgrain`.

5. Change to directory `tsgrain/controller` and run

   ```
   sudo --preserve-env=PYTHONPATH python3 main.py
   ```

6. Change to directory `tsgrain/website` and run

   ```
   sudo --preserve-env=PYTHONPATH python3 -m flask run --host=0.0.0.0
   ```

Steps 5 and 6 are shown for a test environment. In a production environment you
would use `systemctl` to automatically start the processes after booting the
RPi.

A more comprehensive documentation is under way.

This work is licensed under the Apache 2.0 license, see `LICENSE` in this
directory.


Good luck,

Hubert Högl

E-mail: Hubert.Hoegl@t-online.de
