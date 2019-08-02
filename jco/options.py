from jco.exceptions import JcoTerminate


class Option(object):
    lookup = {}
    aliases = {}

    def __init__(self, *names, default=0, help=""):
        self._value = default
        self.type = type(default)
        self.names = names
        self.help = help
        for name in self.names:
            Option.lookup[name] = self
        Option.aliases[tuple(self.names)] = self

    @property
    def value(self):
        return self.type(self._value)

    @value.setter
    def value(self, value):
        self._value = value

    @classmethod
    def set(cls, key, value):
        try:
            cls.lookup[key].value = value
        except KeyError:
            raise JcoTerminate(
                f"No option with name {key}. Try:\n{cls.opt_info()}"
            ) from None

    @classmethod
    def opt_info(cls):
        return "\n".join(
            [f"\t{opts} -> {cls.lookup[opts[0]].help}" for opts in cls.aliases]
        )


NBits = Option("n", "n_bits", default=-1, help="Number of bits")
WordSize = Option("w", "word_size", default=4, help="Word size")
Overflow = Option(
    "o", "overflow", default=1, help="Whether to overflow negative numbers"
)
Format = Option(
    "f",
    "format",
    default="fancy_grid",
    help="Table format (compatible with tabulate package)",
)
MsbFirst = Option(
    "m",
    "msbfirst",
    default=1,
    help="Whether to put the most significant bit first in a bitstring",
)
