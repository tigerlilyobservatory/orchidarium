#! /usr/bin/env python
# Read temperature and humidity data from USB sensor in my Orchidarium.


from __future__ import annotations

import os
import logging
import sys

from functools import partial
from time import sleep
from usb.core import find, USBTimeoutError, USBError
from usb.util import claim_interface, release_interface
from array import array
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
            
            
class InterfaceClaim:
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
        
        endpoint = device[0][(0,0)][0]
        
        for i in range(30):
            bytes = communicate(
                partial(
                    device.read,
                    endpoint.bEndpointAddress,
                    endpoint.wMaxPacketSize,
                    1000
                )
            )
            print(bytes.tobytes())


if __name__ == '__main__': 
    sys.exit(
        main()
    )