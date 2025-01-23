# lui
lui t0, 0xDEADB

# auipc
auipc t1, 0x12345

# register-register arithmetic
addi x1, x2, 42
slti x3, x4, -10
sltiu x5, x6, 20
xori x7, x8, 0xFF
ori x9, x10, 0x0F
andi x11, x12, 0x3F
slli x13, x14, 5
srli x15, x16, 4
srai x17, x18, 3


# register-immediate arithmetic
addi x1, x2, 42
slti x3, x4, -10
sltiu x5, x6, 20
xori x7, x8, 0xFF
ori x9, x10, 0x0F
andi x11, x12, 0x3F
slli x13, x14, 5
srli x15, x16, 4
srai x17, x18, 3


# branches
beq x1, x2, label1
bne x3, x4, label1
blt x5, x6, label1
bge x7, x8, label1
bltu x9, x10, label1
bgeu x11, x12, label1

# load/stores
sb x1, 4(x2)
sh x3, -8(x4)
sw x5, 12(x6)

lb x1, 12(x2)
lh x3, -4(x4)
lw x5, 8(x6)
lbu x7, 16(x8)
lhu x9, 24(x10)

# jumps
jal t2, -8
jalr t3, t2, 0x10

# pseudoinstructions
label1:
nop

# fence                # Fence
# fence.i              # Fence Instruction
# ecall                # Environment Call
# ebreak              # Environment Break
