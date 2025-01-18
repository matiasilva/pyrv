# Simple loop counting down from 5
li x1, 5        # Counter
loop:
addi x1, x1, -1 # Decrement
bnez x1, loop   # Branch if not zero
