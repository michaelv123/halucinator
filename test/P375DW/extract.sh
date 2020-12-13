#!/bin/sh

dd if=D015U4_D2007201727 of=pagetable.bin bs=1 count=$((0x8400)) skip=$((0x93))
dd if=D015U4_D2007201727 of=kernel.bin bs=1 count=$((0x49314)) skip=$((0x8827))
