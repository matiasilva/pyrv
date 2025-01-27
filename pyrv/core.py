import logging
from pathlib import Path

from pyrv.harts import Hart
from tests.helpers import compile_sourcefile


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    def print_in_box(text: str):
        print(f"+{'-' * (len(text) + 2)}+")
        print(f"| {text} |")
        print(f"+{'-' * (len(text) + 2)}+")

    print_in_box("pyrv: RISC-V instruction set simulator")
    elf = compile_sourcefile(Path("."), "simexit.S")
    hart = Hart()
    hart.load(elf)
    return 0


if __name__ == "__main__":
    main()
