# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS). 
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains 
# certain rights in this software.

from . import peripheral_server
#from queue import Queue
from threading import Event, Thread
from collections import deque, defaultdict
import sys
import logging
from itertools import repeat
import time

log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)

# Register the pub/sub calls and methods that need mapped
@peripheral_server.peripheral_model
class UARTPublisher(object):
    rx_buffers = defaultdict(deque)
    int_numbers = defaultdict(lambda: -1)
    int_enabled = defaultdict(lambda: False)

    @classmethod
    @peripheral_server.tx_msg
    def write(cls, uart_id, chars):
        '''
           Publishes the data to sub/pub server
        '''
        log.info("Writing: %s" % chars)
        msg = {'id': uart_id, 'chars': chars}
        return msg

    @classmethod
    def read(cls, uart_id, count=1, block=False):
        '''
            Gets data previously received from the sub/pub server
            Args:
                uart_id:   A unique id for the uart
                count:  Max number of chars to read
                block(bool): Block if data is not available
        '''
        log.debug("In: UARTPublisher.read id:%s count:%i, block:%s" %
                  (hex(uart_id), count, str(block)))
        while block and (len(cls.rx_buffers[uart_id]) < count):
            pass
        log.debug("Done Blocking: UARTPublisher.read")
        buffer = cls.rx_buffers[uart_id]
        chars_available = len(buffer)
        if chars_available >= count:
            chars = [buffer.popleft() for _ in range(count)]
            chars = ''.join(chars).encode('utf-8')
        else:
            chars = [buffer.popleft() for _ in range(chars_available)]
            chars = ''.join(chars).encode('utf-8')

        log.info("Reading %s"% chars)
        return chars

    @classmethod
    def read_line(cls, uart_id, count=1, block=False):
        '''
            Gets data previously received from the sub/pub server
            Args:
                uart_id:   A unique id for the uart
                count:  Max number of chars to read
                block(bool): Block if data is not available
        '''
        log.debug("In: UARTPublisher.read id:%s count:%i, block:%s" %
                  (hex(uart_id), count, str(block)))
        while block and (len(cls.rx_buffers[uart_id]) < count) :
            if len(cls.rx_buffers[uart_id]) > 0:
                if cls.rx_buffers[uart_id][-1] == '\n':
                    break

        log.debug("Done Blocking: UARTPublisher.read")
        log.debug("rx_buffers %s" % cls.rx_buffers[uart_id])
        buffer = cls.rx_buffers[uart_id]
        chars_available = len(buffer)
        if chars_available >= count:
            #chars = list(map(apply, repeat(buffer.popleft, count)))
            chars = [buffer.popleft() for _ in range(count)]
            chars = ''.join(chars).encode('utf-8')
        else:
            chars = [buffer.popleft() for _ in range(chars_available)]
            chars = ''.join(chars).encode('utf-8')

        log.info("Reading %s"% chars)
        return chars


    @classmethod
    @peripheral_server.reg_rx_handler
    def rx_data(cls, msg):
        '''
            Handles reception of these messages from the PeripheralServer
        '''
        log.debug("rx_data got message: %s" % str(msg))
        uart_id = msg['id']
        data = msg['chars']
        cls.rx_buffers[uart_id].extend(data)

        # If the interrupt for the UART device is enabled, send an interrupt
        if int_enabled[uart_id] and int_numbers[uart_id] != -1:
            peripheral_server.trigger_interrupt(int_numbers[uart_id])

    @classmethod
    def register_interrupt(cls, uart_id, int_id)
        int_numbers[uart_id] = int_id

    @classmethod
    def enable_interrupt(cls, uart_id):
        int_enabled[uart_id] = True

    @classmethod
    def disable_interrupt(cls, uart_id):
        int_enabled[uart_id] = False
