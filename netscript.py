#!/bin/env python3

import sys
import coloredlogs, logging
from typing import *

from enum import IntEnum

logger = logging.getLogger('test')
logger.setLevel(logging.DEBUG)
coloredlogs.install(
    level='DEBUG',
    fmt='%(name)s [%(levelname)s]: %(message)s',
    level_styles={
        'cmd': {'color': 'cyan'},  # Color for CMD level
        'debug': {'color': 'white'},
        'info': {'color': 'green'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red'},
        'critical': {'color': 'magenta'},
    },
    field_styles={
        'name': {'color': 'cyan'},
        'levelname': {'bold': True},
    }
)
class ParamCountType(IntEnum):
    ATLEAST = 0
    EXACT = 1
    NOMORE_THAN = 2
    COUNT = 3

class ParamCount():
    def __init__(self, _type: ParamCountType, v):
        self._type = _type
        self.v = v
        self.og_v = v

    def __repr__(self):
        return f"{param_count_type_as_str(self._type)} {self.og_v}"

def param_count_type_as_str(v: ParamCountType) -> str:
    match(v):
        case ParamCountType.ATLEAST: return "at least"
        case ParamCountType.EXACT: return "exactly"
        case ParamCountType.NOMORE_THAN: return "no more than"
        case ParamCountType.COUNT: pass
    assert False, "This musn't run!"

# Exceptions
class InsufficientParamsException(Exception):
    def __init__(self, funcname: str, param_count: ParamCount, expected_args_count: int, *args: object) -> None:
        self.funcname = funcname
        self.param_count = param_count
        self.expected_args_count = expected_args_count
        super().__init__(*args)

    def __repr__(self) -> str:
        return f"{self.funcname} expects {param_count_as_str(self.param_count_type)} {self.expected_args_count} argument(s)!"

    def __str__(self) -> str:
        return self.__repr__()

class InvalidParamTypeException(Exception):
    def __init__(self, wanted_type: Type, got_type: Type, funcname: str, *args: object) -> None:
        self.wanted_type = wanted_type
        self.got_type = got_type
        self.funcname = funcname
        super().__init__(*args)

    def __repr__(self) -> str:
        return f"{self.funcname} wanted {self.wanted_type} but got {self.got_type}"

    def __str__(self) -> str:
        return self.__repr__()

class IntegerOutofRangeException(Exception):
    def __init__(self, funcname: str, min: int, max: int, *args: object) -> None:
        self.funcname = funcname
        self.min = min
        self.max = max

    def __repr__(self) -> str:
        return f"{self.funcname} wanted integer in range {self.min}..{self.max}"

    def __str__(self) -> str:
        return self.__repr__()


VERSION: str = "0.0.1a"

# Functions for subcommands
def subnet_mask_short2hosts_per_subnet(inputs) -> int:
    assert len(inputs) >= 1, "This should be handled at subcommand argument parsing!"

    v = inputs.pop(0)
    
    v = v.removeprefix("/")

    try:
        v = int(v)
    except Exception as e:
        logger.error(f"{e}")
        exit(1)

    if v < 0 or v > 32:
        logger.error("subnet mask should be between 0 ~ 32!")
        exit(1)

    hosts_per_subnet: int = 2**(32 - v) - 2
    logger.info(f"{hosts_per_subnet}")
    return hosts_per_subnet

def subnet_count(inputs):
    assert len(inputs) >= 1, "This should be handled at subcommand argument parsing!"
    b = inputs.pop(0)
    b = b.removeprefix("/")
    try:
        b = int(b)
    except Exception as e:
        logger.error(f"{e}")
        exit(1)

    if b < 0 or b > 32:
        logger.error("base subnet mask should be between 0 ~ 32!")
        exit(1)

    v = inputs.pop(0)
    v = v.removeprefix("/")
    try:
        v = int(v)
    except Exception as e:
        logger.error(f"{e}")
        exit(1)

    if v < 0 or v > 32:
        logger.error("target subnet mask should be between 0 ~ 32!")
        exit(1)

    if v < b:
        logger.info(f"0")
        return 0
    if v == 32:
        logger.info(f"1")
        return 1
    if v == 31:
        logger.info(f"2")
        return 2

    count = 2**(v - b)
    logger.info(f"{count}")
    return count


def hhelp(inputs):
    assert len(inputs) >= 1, "This should be handled at subcommand argument parsing!"
    program = inputs.pop(0)

    usage(program)

def subnet_mask_short_to_long(inputs):
    assert len(inputs) >= 1, "This should be handled at subcommand argument parsing!"

    subnet_mask_short = inputs.pop(0)

    v = subnet_mask_short.removeprefix("/")

    try:
        v = int(v)
    except Exception as e:
        logger.error(f"{e}")
        exit(1)

    if v < 0 or v > 32:
        logger.error("subnet mask should be between 0 ~ 32!")
        exit(1)

    if v == 0:
        logger.info(f"SUBNET_MASK_LONG:  0.0.0.0")
        return

    subnet_mask_long = 0
    subnet_mask_short = v

    for i in range(subnet_mask_short+1):
        subnet_mask_long = subnet_mask_long | (1 << (32 - i))

    l = subnet_mask_long
    oct1 = (l >> 8*3) & 0xFF
    oct2 = (l >> 8*2) & 0xFF
    oct3 = (l >> 8*1) & 0xFF
    oct4 = (l >> 8*0) & 0xFF

    logger.info(f"SUBNET_MASK_SHORT: /{subnet_mask_short}")
    logger.info(f"SUBNET_MASK_LONG:  {oct1}.{oct2}.{oct3}.{oct4} ({subnet_mask_long})")

def subnet_mask_long_to_short(inputs):
    assert len(inputs) >= 1, "This should be handled at subcommand argument parsing!"

    long = inputs.pop(0)

class Subcommand:
    def __init__(self, name: str, inputs: List[str], description: str, func, param_count: ParamCount):
        self.name = name
        self.inputs = inputs
        self.description = description
        self.func = func
        self.param_count = param_count

    def __repr__(self):
        return f"Subcommand: {self.name}, {self.inputs}, {self.description}, {self.func}, {self.param_count}"

    def __str__(self):
        return self.__repr__()

subcommands = {
    "subnet_hosts_count": Subcommand("subnet_hosts_count", ["target_subnet_mask"], "Calculates available hosts per subnet given short-hand subnet mask. eg: /24", subnet_mask_short2hosts_per_subnet, ParamCount(ParamCountType.EXACT, 1)),
    "subnet_count": Subcommand("subnet_count", ["base_subnet_mask", "target_subnet_mask"], "Calculates number of subnets given short-hand base subnet mask and target subnet mask.", subnet_count, ParamCount(ParamCountType.EXACT, 2)),
    "test_atleast": Subcommand("test_atleast", ["arg1", "arg2"], "For testing the ParamCount.ATLEAST parsing.", None, ParamCount(ParamCountType.ATLEAST, 2)),
    "subnet_mask_short_to_long": Subcommand("subnet_mask_short_to_long", [ "subnet_mask_short" ], "Convert short form (CIDR) of a subnet mask to the long form.", subnet_mask_short_to_long, ParamCount(ParamCountType.EXACT, 1)), "help": Subcommand("help", [], "Help.", hhelp, ParamCount(ParamCountType.ATLEAST, 0)),
    "subnet_mask_long_to_short": Subcommand("subnet_mask_long_to_short", [ "subnet_mask_long" ], "Convert long form of a subnet mask to the short form (CIDR).", subnet_mask_short_to_long, ParamCount(ParamCountType.EXACT, 1)), "help": Subcommand("help", [], "Help.", hhelp, ParamCount(ParamCountType.ATLEAST, 0)),
}

def usage(program: str):
    print(f"{program} <subcommand>")
    print("")
    print("Subcommands:")
    for subcommand_name in subcommands:
        subcmd = subcommands[subcommand_name]
        print(f"    {subcmd.name} {subcmd.inputs}        - {subcmd.description}")

def main():
    program: str = sys.argv.pop(0)

    if len(sys.argv) <= 0:
        usage(program)
        exit(1)

    while len(sys.argv) > 0:
        arg = sys.argv.pop(0)
        if arg in subcommands:
            subcmd = subcommands[arg]

            parsed_inputs = []
            if arg == "help":
                parsed_inputs.append(program)

            subcmd_input_count = len(sys.argv)
            while subcmd.param_count.v > 0 and len(sys.argv) > 0:
                subcmd_input = sys.argv.pop(0)
                # logger.info(f"{subcmd.inputs[len(subcmd.inputs)-subcmd.param_count.v]} = {subcmd_input}")
                parsed_inputs.append(subcmd_input)
                subcmd.param_count.v -= 1


            if subcmd.param_count._type == ParamCountType.EXACT:
                if subcmd.param_count.v != len(sys.argv):
                    logger.error(f"Subcommand `{arg}` wanted {subcmd.param_count} argument(s), but got {subcmd_input_count} argument(s)!: WANTS {subcmd.inputs}")
                    exit(1)
                # logger.info(f"param_count.v after parsing subcommand inputs: {subcmd.param_count.v}")
            elif subcmd.param_count._type == ParamCountType.ATLEAST:
                if subcmd.param_count.v != 0:
                    logger.error(f"Subcommand `{arg}` wanted {subcmd.param_count} argument(s), but got {subcmd_input_count} argument(s)!: WANTS {subcmd.inputs}")
                    exit(1)

            elif subcmd.param_count._type == ParamCountType.NOMORE_THAN:
                assert False, "ParamCountType.NOMORE_THAN"
            else:
                logger.error("UNREACHABLE!")
                exit(1)

            # logger.info(f"Parsed subcommand inputs: {parsed_inputs}")
            if subcmd.func:
                subcmd.func(parsed_inputs)
            else:
                logger.warning(f"`{arg}` doesn't have a function attached to it!")

        else:
            logger.error(f"Unknown subcommand: `{arg}`")
            exit(1)


if __name__ == '__main__':
    main()
