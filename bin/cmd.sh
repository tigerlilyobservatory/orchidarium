#! /usr/bin/env bash
# Start the service.


set -eo pipefail


if [ -z "$USB_VENDOR_ID" ]; then
    printf "ERROR: USB_VENDOR_ID is not defined. Please provide a valid USB vendor ID in hexadecimal (from lsusb -v output).\\n" >&2
    exit 1
fi

if [ -z "$USB_PRODUCT_ID" ]; then
    printf "ERROR: USB_PRODUCT_ID is not defined. Please provide a valid USB product ID in hexadecimal (from lsusb -v output).\\n" >&2
    exit 1
fi

# Start the service.
if [ -n "$(poetry env info -p)" ]; then
    poetry run orchidarium "$@"
else
    passoperator "$@"
fi