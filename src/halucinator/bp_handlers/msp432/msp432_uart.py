from os import sys, path
from ...peripheral_models.uart import UARTPublisher
from ..bp_handler import BPHandler, bp_handler
import logging
log = logging.getLogger(__name__)

from ... import hal_log
hal_log = hal_log.getHalLogger()

class MSP432UART(BPHandler):

    def __init__(self, impl=UARTPublisher)
        self.model = impl

    # TI Drivers handlers (High level drivers)
    @bp_handler(['UART_open'])
    def get_index(self, qemu, bp_addr):
        uart_index = qemu.get_arg(0)
        # Return the index as the handle so we know it in future operations
        # Add 1 so that the NULL handle check doesn't trigger an error
        hal_log.info("Uart %i initialized" % uart_index)
        return True, uart_index + 1

    @bp_handler(['UART_write'])
    def handle_tx(self, qemu, bp_addr):
        uart_index = qemu.get_arg(0)
        buf_addr = qemu.get_arg(1)
        buf_len = qemu.get_arg(2)
        # Read buffer from QEMU memory
        data = qemu.read_memory(buf_addr, 1, buf_len, raw=True)
        hal_log.info("UART %i TX:%s" % (hw_addr, data))
        self.model.write(uart_index, data)
        # Return the number of bytes written
        return True, buf_len

    @bp_handler(['UART_read'])
    def handle_rx(self, qemu, bp_addr):
        uart_index = qemu.get_arg(0)
        buf_addr = qemu.get_arg(1)
        buf_len = qemu.get_arg(2)
        log.info("Waiting for data: %i" % buf_len)
        data = self.model.read(uart_index, buf_len, block=True)
        hal_log.info("UART %i RX: %s" % (uart_index, data))
        # Write data to QEMU memory
        qemu.write_memory(buf_addr, 1, data, buf_len, raw=True)
        # Return the number of bytes read
        return True, buf_len

    # Driverlib handlers (HAL functions)
    # TODO