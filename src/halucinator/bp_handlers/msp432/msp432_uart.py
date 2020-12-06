from os import sys, path
from ...peripheral_models.uart import UARTPublisher
from ..bp_handler import BPHandler, bp_handler
import logging
log = logging.getLogger(__name__)

from ... import hal_log
hal_log = hal_log.getHalLogger()

class MSP432UART(BPHandler):

    int_addrs = defaultdict(lambda: -1)
    int_enabled = defaultdict(lambda: False)
    uart_int_enabled = defaultdict(lambda: False)

    def __init__(self, impl=UARTPublisher):
        self.model = impl
        self.int_addrs[21] = 0x4000c000

    # TI Drivers handlers (High level drivers)
    @bp_handler(['UART_open'])
    def get_index(self, qemu, bp_addr):
        # Add 1 so that the NULL handle check doesn't trigger an error
        uart_index = qemu.get_arg(0) + 1
        # Return the index as the handle so we know it in future operations
        hal_log.info("Uart %i initialized" % uart_index)
        return True, uart_index

    @bp_handler(['UART_write'])
    def handle_tx(self, qemu, bp_addr):
        uart_index = qemu.get_arg(0)
        buf_addr = qemu.get_arg(1)
        buf_len = qemu.get_arg(2)
        # Read buffer from QEMU memory
        data = qemu.read_memory(buf_addr, 1, buf_len, raw=True)
        hal_log.info("UART %i TX:%s" % (uart_index, data))
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
    @bp_handler(['IntEnable'])
    def int_enable(self, qemu, bp_addr):
        int_num = qemu.get_arg(0)
        if int_addrs[int_num] != -1:
            self.int_enabled[int_num] = True
            self.model.register_interrupt(int_addrs[int_num], int_num)
            # Only enable the interrupt if both the interrupt and its source are enabled
            if int_enabled[int_num] and uart_int_enabled[int_num]:
                self.model.enable_interrupt(int_addrs[int_num])

    @bp_handler(['UARTIntEnable'])
    def uart_int_enable(self, qemu, bp_addr):
        hw_addr = qemu.get_arg(0)
        for num, addr in int_addrs.items():
            if addr = hw_addr:
                int_num = num
        uart_int_enabled[int_num] = True
        # Only enable the interrupt if both the interrupt and its source are enabled
        if int_enabled[int_num] and uart_int_enabled[int_num]:
            self.model.enable_interrupt(int_addrs[int_num])


    @bp_handler(['UARTCharsAvail'])
    @bp_handler(['UARTCharGetNonBlocking'])
    @bp_handler(['UARTCharPutNonBlocking'])