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
    @bp_handler(['UART_init'])
    @bp_handler(['UART_Params_init'])
    @bp_handler(['UART_open'])
    @bp_handler(['UART_read'])
    @bp_handler(['UART_write'])

    # Driverlib handlers (HAL functions)