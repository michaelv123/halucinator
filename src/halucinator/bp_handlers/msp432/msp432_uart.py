from os import sys, path
from collections import defaultdict
from ...peripheral_models.uart import UARTPublisher
from ..bp_handler import BPHandler, bp_handler
import logging
log = logging.getLogger(__name__)

from ... import hal_log
hal_log = hal_log.getHalLogger()

class MSP432UART(BPHandler):

    int_addrs = defaultdict(lambda: -1)

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
        if self.int_addrs[int_num] != -1:
            self.model.register_interrupt(self.int_addrs[int_num], int_num)
        # What did we learn today?
        # Avatar2's "configurable" ARM machine initialises QEMU's NVIC at 0xe000e000 when the "cortex-m3" cpu-model is specified
        # This function interacts with the NVIC to enable interrupts, so don't return True or interrupts won't work :D
        return False, None

    @bp_handler(['UARTIntEnable'])
    def uart_int_enable(self, qemu, bp_addr):
        hw_addr = qemu.get_arg(0)
        for num, addr in self.int_addrs.items():
            if addr == hw_addr:
                int_num = num
        self.model.enable_interrupt(self.int_addrs[int_num])
        hal_log.info("UART %i interrupt %i enabled" % (self.int_addrs[int_num], int_num))
        return True, None


    @bp_handler(['UARTCharsAvail'])
    def uart_chars_available(self, qemu, bp_addr):
        hw_addr = qemu.get_arg(0)
        avail = self.model.chars_available(hw_addr)
        hal_log.info("UART %i chars available: %i" % (hw_addr, int(avail)))
        return True, int(avail)

    @bp_handler(['UARTCharGetNonBlocking'])
    def uart_char_get_non_blocking(self, qemu, bp_addr):
        hw_addr = qemu.get_arg(0)
        char = self.model.read(hw_addr, 1, block=False)
        if char == b'':
            ret = -1
        else:
            ret = char[0]
        hal_log.info("UART %i get char: %s | %i" % (hw_addr, char.decode('utf-8'), ret))
        return True, ret

    @bp_handler(['UARTCharPutNonBlocking'])
    def uart_char_put_non_blocking(self, qemu, bp_addr):
        hw_addr = qemu.get_arg(0)
        char = qemu.get_arg(1)
        char = char.to_bytes(1, byteorder='big')
        self.model.write(hw_addr, char)
        hal_log.info("UART %i put char: %s" % (hw_addr, char.decode('utf-8')))
        return True, 1