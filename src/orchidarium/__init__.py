import logging
import os

from typing import Dict


log = logging.getLogger(__name__)

env: Dict[str, str]  = {
    # Retrieve these values for your sensor by running 'lsusb -v'. See /conf/lsusb.out
    'USB_VENDOR_ID': os.getenv('USB_VENDOR_ID', '0x1a86'),
    'USB_PRODUCT_ID': os.getenv('USB_PRODUCT_ID', '0x7523')
}

# Validate
try:
    int(env['USB_VENDOR_ID'], base=16)
    int(env['USB_PRODUCT_ID'], base=16)
except TypeError as e:
    log.error(e)