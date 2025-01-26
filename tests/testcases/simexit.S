#include "sim_control.h"

.text
.globl _start
_start:
li t0, SIM_CONTROL_BASE
addi t1, x0, 0x1
sw t1, 0(t0)
