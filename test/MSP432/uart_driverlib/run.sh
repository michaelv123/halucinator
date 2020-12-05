#! /bin/bash

halucinator -c m3_driverlib_uart_echo_MSP_EXP432E401Y_nortos_ccs_config.yaml \
	-c m3_driverlib_uart_echo_MSP_EXP432E401Y_nortos_ccs_addrs.yaml \
	-c m3_driverlib_uart_echo_MSP_EXP432E401Y_nortos_ccs_memory.yaml \
	--log_blocks=trace-nochain -n msp432_uart_driverlib
