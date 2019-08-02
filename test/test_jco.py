import pytest

import jco
import jco.exceptions
import jco.options
import jco.script


def fatal():
    return pytest.raises(jco.exceptions.JcoTerminate)


def run(string):
    jco.script.main(string.split(" "))


def test_import():
    pass


def test_entry():
    jco.script.entry()


def test_main():
    jco.script.main([])


def test_hex():
    run("0x42")


def test_bin():
    run("0b10010010")


def test_dec():
    run("984823")


def test_two_nums():
    run("0x42 0x43")


def test_mixed_repr():
    run("0x43 91")


def test_invalid_num():
    with fatal():
        run("0x4az")


def test_two_nums_one_invalid():
    with fatal():
        run("0x43 9v")


def test_bitfield():
    run("bf sign:1,exponent:8,fraction:23 0xfff1a238")


def test_bitfield_invalid():
    with fatal():
        run("bf sign;1,exponent:8,fraction:23 0xfff1a238")


def test_one():
    run("one 0x43")


def test_one_invalid():
    with fatal():
        run("one 0x43 43")


def test_two():
    run("two 0x45 54")


def test_two_invalid():
    with fatal():
        run("two 0x43")
