#! /bin/bash

halucinator -c m3_tidrivers_uartecho_MSP_EXP432E401Y_nortos_ccs_config.yaml \
	-c m3_tidrivers_uartecho_MSP_EXP432E401Y_nortos_ccs_addrs.yaml \
	-c m3_tidrivers_uartecho_MSP_EXP432E401Y_nortos_ccs_memory.yaml \
	--log_blocks=irq -n msp432_uart_tidrivers
