from typing import List
import sys
import math

from tabulate import tabulate

from jco.exceptions import JcoTerminate
from jco.options import Option, NBits, Overflow, Format, WordSize


class Undefined(object):
    def __format__(self, fmt):
        return "undefined"


undefined = Undefined()


def ones_complement(value: int):
    if value is undefined:
        return value
    nbits = NBits.value
    bitstring = bin(value).replace("0b", "")
    bitstring = "0" * (nbits - len(bitstring)) + bitstring
    outstring = "".join(["1" if c == "0" else "0" for c in bitstring])
    outvalue = int(outstring, 2)
    return outvalue


def twos_complement(value: int):
    if value is undefined:
        return value
    nbits = NBits.value
    outvalue = ones_complement(value)
    outvalue += 1
    if outvalue == 2 ** nbits:
        outvalue = 0
    return outvalue


def popcount(value):
    if value is undefined:
        return undefined
    else:
        return bin(value).count("1")


def hamming_distance(a, b):
    if a is undefined or b is undefined:
        return undefined
    return sum(e1 != e2 for e1, e2 in zip(a, b))


class Int(object):
    def __init__(self, inp, name):
        if inp is undefined:
            self.int = undefined
            self.string = undefined
        elif isinstance(inp, int):
            self.int = inp
            self.string = str(inp)
        else:
            self.string = inp
            self.int = int(inp, 0)
        self.name = name
        self.raw = False

    @property
    def out(self):
        if self.int is undefined:
            return undefined
        if not self.raw and int(Overflow.value) and self.int < 0:
            result = twos_complement(self.int)
        else:
            result = self.int
        if result > 2 ** NBits.value - 1:
            return undefined
        return result

    @property
    def hex(self):
        hexes = int(NBits.value / 4)
        return f"{self.out:0{hexes}x}"

    @property
    def dec(self):
        decs = int(math.ceil(NBits.value * math.log(2) / math.log(10)))
        return f"{self.out: {decs}d}"

    @property
    def bin(self):
        return f"{self.out:0{NBits.value}b}"

    def row(self):
        return [self.name, self.dec, self.hex, self.bin]


def tab(rows, **kwargs):
    return tabulate(rows, tablefmt=Format.value, headers=["", "Dec", "Hex", "Bin"])


def checklen(strings, n):
    if len(strings) != n:
        raise JcoTerminate(f"Should have {n} inputs, got {len(strings)}: {strings}")


def _one(string, *, name="A"):
    a = Int(string, name)
    one_comp = Int(ones_complement(a.out), f"~{name}")
    one_comp.raw = True
    two_comp = Int(twos_complement(a.out), f"twos_compl({name})")
    two_comp.raw = True
    pc = Int(popcount(a.out), f"popcount({name})")
    return [a, one_comp, two_comp, pc]


def one(*args, **kwargs):
    checklen(args, 1)
    return tab([data.row() for data in _one(*args, **kwargs)])


def _two(first, second):
    a = Int(first, "A")
    b = Int(second, "B")

    return [
        *_one(first, name="A"),
        *_one(second, name="B"),
        Int(a.int - b.int, "A - B"),
        Int(b.int - a.int, "B - A"),
        Int(a.int + b.int, "A + B"),
        Int(a.int | b.int, "A | B"),
        Int(a.int & b.int, "A & B"),
        Int(a.int ^ b.int, "A ^ B"),
        Int((a.int << WordSize.value) + b.int, f"A << {WordSize.value} + B"),
        Int((b.int << WordSize.value) + a.int, f"B << {WordSize.value} + A"),
        Int(a.int & twos_complement(b.int), "A &~ B"),
        Int(hamming_distance(a.bin, b.bin), "distance(A, B)"),
    ]


def two(*args, **kwargs):
    checklen(args, 2)
    return tab(
        [data.row() if hasattr(data, "row") else data for data in _two(*args, **kwargs)]
    )
