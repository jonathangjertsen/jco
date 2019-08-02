from typing import List
import sys
import math

from tabulate import tabulate

from jco.exceptions import JcoTerminate
from jco.options import Option, NBits, Overflow, Format, MsbFirst, WordSize


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


def min_num_bits(a):
    if a is undefined:
        return undefined
    return math.ceil(math.log(a, 2))

class Int(object):
    def __init__(self, inp, name):
        try:
            if inp is undefined:
                self.int = undefined
                self.string = undefined
            elif isinstance(inp, int):
                self.int = inp
                self.string = str(inp)
            else:
                self.string = inp
                self.int = int(inp, 0)
        except Exception:
            raise JcoTerminate(f"This doesn't seem like a number: {inp}")
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
    if NBits.value == -1:
        NBits.value = nbits(a.int)
    one_comp = Int(ones_complement(a.out), f"~{name} ({NBits.value} bits)")
    one_comp.raw = True
    two_comp = Int(twos_complement(a.out), f"twos_compl({name}, {NBits.value} bits)")
    two_comp.raw = True
    pc = Int(popcount(a.out), f"popcount({name})")
    nb = Int(min_num_bits(a.out), f"nbits({name})")
    shift = Int(a.int >> WordSize.value, f"{name} >> {WordSize.value}")
    return [a, one_comp, two_comp, pc, nb, shift]


def one(*args, **kwargs):
    checklen(args, 1)
    return tab([data.row() for data in _one(*args, **kwargs)])


def _two(first, second):
    a = Int(first, "A")
    b = Int(second, "B")

    if NBits.value == -1:
        NBits.value = max(min_num_bits(a.int), min_num_bits(b.int))

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

def parse_spec(spec):
    try:
        spec = spec.strip()
        fields = [field.split(":") for field in spec.split(",")]
        return [(name, int(nbits)) for name, nbits in fields]
    except Exception as exc:
        raise JcoTerminate(f"Couldn't parse bitfield '{spec}' (exception='{exc}')")

def bitfield(spec_str, numstr):
    num = Int(numstr, "num")
    spec = parse_spec(spec_str)
    NBits.value = sum(_nbits for name, _nbits in spec)
    headers = [""] + [f"{name} [{_nbits}]" for name, _nbits in spec]
    num_nbits = min_num_bits(num.int)
    if num_nbits > NBits.value:
        raise JcoTerminate(f"Bit field has total width {NBits.value}, but {numstr} is a {num_nbits}-bit number")
    else:
        bits = num.bin
        if not MsbFirst.value:
            bits = "".join(reversed(bits))
        field_values = []
        cursor = 0
        for name, nbits in spec:
            field_values.append(bits[cursor:cursor+nbits])
            cursor += nbits

    rows = [
        ["Bin"] + field_values,
        ["Dec"] + [int(value, 2) for value in field_values],
        ["Hex"] + [hex(int(value, 2)).replace("0x", "") for value in field_values],
    ]
    return tabulate(rows, tablefmt=Format.value, headers=headers, numalign="center", stralign="center")
