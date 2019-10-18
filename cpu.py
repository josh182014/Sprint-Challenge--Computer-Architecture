"""CPU functionality."""
import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.isRunning = True
        self.reg[SP] = 0xf4
        self.FL = 0b00000000

        self.commands = {
            HLT: self.HLTMethod,
            LDI: self.LDIMethod,
            PRN: self.PRNMethod,
            MUL: self.MULMethod,
            PUSH: self.PUSHMethod,
            POP: self.POPMethod,
            CALL: self.CALLMethod,
            RET: self.RETMethod,
            ADD: self.ADDMethod,
            JMP: self.JUMPMethod,
            CMP: self.COMPMethod,
            JEQ: self.JEQMethod,
            JNE: self.JNEMethod
        }

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MDR] = MAR

    def load(self, file):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        with open(file) as program:
            for line in program:
                instruction = line.split("#")[0].strip()
                if instruction == "":
                    continue
                value = int(instruction, 2)
                self.ram[address] = value
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.isRunning is True:
            IR = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            size = (IR >> 6) + 1
            sets = ((IR >> 4) & 0b1) == 1
            if IR in self.commands:
                self.commands[IR](operand_a, operand_b)
            else:
                print(IR)
                raise Exception('error: unknown command:')

            # self.pc += (IR >> 6) + 1
            if not sets:
                self.pc += size

    def HLTMethod(self, a, b):
        self.isRunning = False

    def LDIMethod(self, a, b):
        self.reg[a] = b

    def PRNMethod(self, a, b):
        print(self.reg[a])

    def MULMethod(self, a, b):
        self.reg[a] *= self.reg[b]

    def pushHelper(self, val):
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], val)

    def PUSHMethod(self, a, b):
        self.pushHelper(self.reg[a])

    def popHelper(self):
        val = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        return val

    def POPMethod(self, a, b):
        self.reg[a] = self.popHelper()

    def CALLMethod(self, a, b):
        self.pushHelper(self.pc + 2)
        self.pc = self.reg[a]

    def RETMethod(self, a, b):
        self.pc = self.popHelper()

    def ADDMethod(self, a, b):
        self.alu("ADD", a, b)

    def COMPMethod(self, a, b):
        if self.reg[a] == self.reg[b]:
            self.FL = 0b00000001

    def JUMPMethod(self, a, b):
        self.pc = self.reg[a]

    def JEQMethod(self, a, b):
        if self.FL == 0b00000001:
            self.JUMPMethod(a, b)
        else:
            self.pc += 2

    def JNEMethod(self, a, b):
        if self.FL != 0b00000001:
            self.JUMPMethod(a, b)
        else:
            self.pc += 2
