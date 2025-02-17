.section .text
.globl _start
_start:
	    lui  a1,      %hi(msg)       # load msg(hi)
	    addi a1, a1,  %lo(msg)       # load msg(lo)
2:    j    2b

.section .rodata
msg:
	    .string "Hello World\n"

.section .data
.word 0x56, 0xf8
