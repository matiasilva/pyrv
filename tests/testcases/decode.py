import pyrv.instructions as i

DECODE_TESTCASES = [
    i.LoadUpperImmediate({"rd": 5, "imm": 0xDEADB000}),
    i.AddUpperImmediateToPc({"rd": 6, "imm": 0x12345000}),
    i.AddImmediate({"rd": 1, "rs1": 2, "imm": 42}),
    i.SetOnLessThanImmediate({"rd": 3, "rs1": 4, "imm": -10}),
    i.SetOnLessThanImmediateU({"rd": 5, "rs1": 6, "imm": 20}),
    i.ExclusiveOrImmediate({"rd": 7, "rs1": 8, "imm": 0xFF}),
    i.OrImmediate({"rd": 9, "rs1": 10, "imm": 0x0F}),
    i.AndImmediate({"rd": 11, "rs1": 12, "imm": 0x3F}),
    i.ShiftLeftLogicalImmediate({"rd": 13, "rs1": 14, "imm": 5}),
    i.ShiftRightLogicalImmediate({"rd": 15, "rs1": 16, "imm": 4}),
    i.ShiftRightArithmeticImmediate({"rd": 17, "rs1": 18, "imm": 3}),
    i.Add({"rd": 1, "rs1": 2, "rs2": 3}),
    i.Sub({"rd": 4, "rs1": 5, "rs2": 6}),
    i.ShiftLeftLogical({"rd": 7, "rs1": 8, "rs2": 9}),
    i.SetOnLessThan({"rd": 10, "rs1": 11, "rs2": 12}),
    i.SetOnLessThanU({"rd": 13, "rs1": 14, "rs2": 15}),
    i.ExclusiveOr({"rd": 16, "rs1": 17, "rs2": 18}),
    i.ShiftRightLogical({"rd": 19, "rs1": 20, "rs2": 21}),
    i.ShiftRightArithmetic({"rd": 22, "rs1": 23, "rs2": 24}),
    i.Or({"rd": 25, "rs1": 26, "rs2": 27}),
    i.And({"rd": 28, "rs1": 29, "rs2": 30}),
    i.BranchEqual({"rs1": 1, "rs2": 2, "imm": 64}),
    i.BranchNotEqual({"rs1": 3, "rs2": 4, "imm": 60}),
    i.BranchOnLessThan({"rs1": 5, "rs2": 6, "imm": 56}),
    i.BranchOnGreaterThanEqual({"rs1": 7, "rs2": 8, "imm": 52}),
    i.BranchOnLessThanU({"rs1": 9, "rs2": 10, "imm": 48}),
    i.BranchOnGreaterThanEqualU({"rs1": 11, "rs2": 12, "imm": 44}),
    i.StoreByte({"rs1": 2, "rs2": 1, "imm": 4}),
    i.StoreHalfword({"rs1": 4, "rs2": 3, "imm": -8}),
    i.StoreWord({"rs1": 6, "rs2": 5, "imm": 12}),
    i.LoadByte({"rd": 1, "rs1": 2, "imm": 12}),
    i.LoadHalfword({"rd": 3, "rs1": 4, "imm": -4}),
    i.LoadWord({"rd": 5, "rs1": 6, "imm": 8}),
    i.LoadByteU({"rd": 7, "rs1": 8, "imm": 16}),
    i.LoadHalfwordU({"rd": 9, "rs1": 10, "imm": 24}),
    i.JumpAndLink({"rd": 7, "imm": -32}),
    i.JumpAndLinkRegister({"rd": 28, "rs1": 7, "imm": 0x10}),
    i.AddImmediate({"rd": 0, "rs1": 0, "imm": 0}),
]
