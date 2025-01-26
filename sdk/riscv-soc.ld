MEMORY {
  CODE : ORIGIN = 0x00000000,  LENGTH = 2M
  DATA : ORIGIN = 0x02000000,  LENGTH = 6M
}


SECTIONS {
  . = ALIGN(4);
  .text : {
    *(.text)
    *(.text.*)
  } > CODE
  .bss : { *(.bss); *(.bss.*) } > DATA
  .data : { *(.data); *(.data.*) } > DATA
  .rodata : { *(.rodata); *(.rodata.*) } > DATA
}
