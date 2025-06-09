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

def subnet_mask_short2hosts_per_subnet(v: int) -> int:
    hosts_per_subnet: int = 2**(32 - v)-2
    logger.info(f"{hosts_per_subnet}")
    return hosts_per_subnet

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

subcommands = { "sbntm_sh_2_hts_p_sbnt": Subcommand("sbntm_sh_2_hts_p_sbnt", ["sbntm_sh"], "Calculates available hosts per subnet given short-hand subnet mask. eg: /24", subnet_mask_short2hosts_per_subnet, ParamCount(ParamCountType.EXACT, 1)) }

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

            if subcmd.param_count._type == ParamCountType.ATLEAST:
                assert False, "ParamCountType.ATLEAST"
            elif subcmd.param_count._type == ParamCountType.EXACT:
                parsed_inputs = []

                subcmd_input_count = len(sys.argv)
                while subcmd.param_count.v > 0 and len(sys.argv) > 0:
                    subcmd_input = sys.argv.pop(0)
                    logger.info(f"{subcmd.inputs[len(subcmd.inputs)-subcmd.param_count.v]} = {subcmd_input}")
                    subcmd.param_count.v -= 1

                if subcmd.param_count.v != len(sys.argv):
                    logger.error(f"Subcommand `{arg}` wanted {subcmd.param_count} argument(s), but got {subcmd_input_count} argument(s)!")
                    exit(1)
                logger.info(f"param_count.v after parsing subcommand inputs: {subcmd.param_count.v}")

            elif subcmd.param_count._type == ParamCountType.NOMORE_THAN:
                assert False, "ParamCountType.NOMORE_THAN"
            else:
                logger.error("UNREACHABLE!")
                exit(1)

        else:
            logger.error(f"Unknown subcommand: `{arg}`")
            exit(1)


if __name__ == '__main__':
    main()
