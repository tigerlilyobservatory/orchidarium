"""
Read temperature and humidity data from USB sensor in my Orchidarium.
"""


from __future__ import annotations

import os
import logging
import sys

from contextlib import AbstractContextManager
from functools import partial
from time import sleep
from usb.core import find, USBTimeoutError, USBError
from usb.util import claim_interface, release_interface
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from array import array
    from typing import (
        Dict,
        Callable,
        Any
    )


# Globals

log = logging.getLogger(__name__)


env: Dict[str, str]  = {
    # Retrieve these values for your sensor by running 'lsusb -v'
    'USB_VENDOR_ID': os.getenv('USB_VENDOR_ID', '0x1a86'),
    'USB_PRODUCT_ID': os.getenv('USB_PRODUCT_ID', '0x7523')
}

# Constants

# See the following manufacturers document for a table of instruction codes.
# https://sensirion.com/media/documents/CCDE1377/635000A2/Sensirion_Datasheet_Humidity_Sensor_SHT20.pdf
TRIG_TEMP_HOLD = b'\0xE3'
TRIG_HUMID_HOLD = b'\0xE5'
TRIG_TEMP_NOHOLD = b'\0xF3'
TRIG_HUMID_NOHOLD = b'\0xF5'
WRITE_USER_REG = b'\0xE6'
READ_USER_REG = b'\0xE7'
SOFT_RESET = b'\0x00'

TEMP_RES_14bit = b'\0x00'
TEMP_RES_13bit = b'\0x80'
TEMP_RES_12bit = b'\0x01'
TEMP_RES_11bit = b'\0x81'
END_OF_BATTERY = b'\0x40'
ENABLE_HEATER = b'\0x04'
DISABLE_OTP_RELOAD = b'\0x02'

# Validate

try:
    int(env['USB_VENDOR_ID'], base=16)
    int(env['USB_PRODUCT_ID'], base=16)
except TypeError as e:
    log.error(e)


def communicate(f: Callable, delay: int =1) -> array:
    """
    Retry api calls to the USB device until they go through.

    Args:
        f (Callable):
        delay (int):

    Returns:
        array:
    """
    while True:
        try:
            return f()
        except USBTimeoutError as e:
            log.warning(f'Timeout, sleeping for {delay}s before retrying connection: {e}')
            sleep(delay)
        except USBError as e:
            if 'Resource busy' in str(e):
                log.warning(f'Resource busy, retrying')
                sleep(delay)
                continue

            log.error(f'{e}')


class InterfaceClaim(AbstractContextManager):
    """
    Wrap setup and teardown while connecting to a USB interface in a context manager.
    """
    def __init__(self, device: Any, interface: int = 0, detach: bool = False) -> None:
        self.device = device
        self.interface = interface
        self.detach = detach
        # Indicate that a detachment of the kernel driver took place.
        self._detached: bool = False

    def __enter__(self) -> InterfaceClaim:
        if self.detach:
            # Detaching kernel driver if necessary (e.g., for direct communication)
            if self.device.is_kernel_driver_active(0): # Check if kernel driver is active on interface 0
                log.warning(f'Detaching kernel driver')
                communicate(
                    partial(
                        self.device.detach_kernel_driver,
                        self.interface
                    )
                )
                self._detached = True

        communicate(
            partial(
                claim_interface,
                self.device,
                self.interface
            )
        )

        return self

    def __exit__(self, *args: Any) -> None:
        communicate(
            partial(
                release_interface,
                self.device,
                self.interface
            )
        )

        if self.detach and self._detached:
            # Detaching kernel driver if necessary (e.g., for direct communication)
            communicate(
                partial(
                    self.device.attach_kernel_driver,
                    self.interface
                )
            )


def read(endpoint: Any, device: Any) -> bytes:
    """
    Read data from a device.

    Args:
        endpoint (Any): _description_
        device (Any): _description_

    Returns:
        bytes: _description_
    """
    return communicate(
        partial(
            device.read,
            endpoint.bEndpointAddress,
            endpoint.wMaxPacketSize,

        )
    ).tobytes()


def write(endpoint: Any, device: Any, data: bytes) -> bytes | None:
    """
    Write data to a device.

    Args:
        endpoint (Any): _description_
        device (Any): _description_
        data (bytes):
    """
    if len(data) >= endpoint.wMaxPacketSize:
        log.error(f'Cannot write data of size {len(data)} bytes to bus with max packet size {endpoint.wMaxPacketSize}')
        return None

    return communicate(
        partial(
            device.write,
            endpoint.bEndpointAddress,
            data + b'\x00' * (endpoint.wMaxPacketSize - len(data))
        )
    )


def main() -> int:
    device = find(
        idVendor=int(
            env['USB_VENDOR_ID'],
            base=16
        ),
        idProduct=int(
            env['USB_PRODUCT_ID'],
            base=16
        )
    )

    if device is None:
        log.error(f'USB device with idVendor "{env["USB_VENDOR_ID"]}" and idProduct "{env["USB_PRODUCT_ID"]}" not found, exiting.')
        return 1

    with InterfaceClaim(device, detach=True):
        communicate(
            partial(
                device.reset
            )
        )
        communicate(
            partial(
                device.set_configuration
            )
        )

        # device_path = f'/dev/bus/usb/{device.bus:03d}/{device.address:03d}'
        # sht = SHT20(device_path, resolution=SHT20.TEMP_RES_14bit)
        # temp = sht.read_temp()
        # humid = sht.read_humid()
        # print("Temperature (°C): " + str(temp))
        # print("Humidity (%RH): " + str(humid))

        endpoint = device[0][(0,0)][0]

        if (_user_data := write(
            endpoint,
            device,
            READ_USER_REG
        )) is None:
            return 1

        _and = lambda a, b: (int.from_bytes(a, 'big') & int.from_bytes(b, 'big')).to_bytes(max(len(a), len(b)), 'big')
        _or = lambda a, b: (int.from_bytes(a, 'big') | int.from_bytes(b, 'big')).to_bytes(max(len(a), len(b)), 'big')
        _add = lambda a, b:

        user_data = int.to_bytes(_user_data)
        user_data = _and(user_data, b'\0x38')
        print(user_data)
        user_data = _or(user_data, (TEMP_RES_14bit + DISABLE_OTP_RELOAD))

        write(
            endpoint,
            device,
            WRITE_USER_REG + user_data
        )

        write(
            endpoint,
            device,
            SOFT_RESET
        )

        write(
            endpoint,
            device,
            TRIG_TEMP_NOHOLD
        )

        write(
            endpoint,
            device,
            TRIG_HUMID_NOHOLD
        )



def cli() -> None:
    sys.exit(
        main()
    )


if __name__ == '__main__':
    sys.exit(
        main()
    )