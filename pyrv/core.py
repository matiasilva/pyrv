from pyrv.adapters import asm2instr, parse_asm
from pyrv.helpers import HartState

hart_state = HartState()


def main() -> int:
    asm_instrs = []
    with open("tests/add.s") as file:
        asm_instrs = [opargs for line in file if (opargs := parse_asm(line))]

    instrs = map(asm2instr, asm_instrs)
    for instr in instrs:
        print("")
    return 0


if __name__ == "__main__":
    main()
