"""Thermal printer functionality for Ethernet-connected XPrinter XP-80T."""

import os

from escpos.printer import Network


def print_to_thermal_printer(image_path, printer_ip=None, printer_port=None):
    """Print image to thermal printer via Ethernet connection.
    
    Args:
        image_path (str): Path to the image file to print
        printer_ip (str): IP address; defaults to PRINTER_IP or 172.31.23.129
        printer_port (int): Port number; defaults to PRINTER_PORT or 9100
    """
    printer_ip = printer_ip or os.getenv("PRINTER_IP", "172.31.23.129")
    printer_port = printer_port or int(os.getenv("PRINTER_PORT", "9100"))

    try:
        # Initialize Ethernet printer connection
        printer = Network(printer_ip, printer_port)

        # Print the image
        printer.image(image_path, impl="bitImageColumn", center=True)

        # Cut the paper
        printer.cut()

        print(f"Successfully printed to thermal printer at {printer_ip}:{printer_port}")

    except Exception as e:
        print(f"ERROR printing to thermal printer at {printer_ip}:{printer_port}: {str(e)}")
        raise e  # Re-raise to allow calling code to handle the error
