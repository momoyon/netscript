#!/bin/env python3

import sys
import coloredlogs, logging
from typing import *

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

VERSION: str = "0.0.1a"

def subnet_mask_short2hosts_per_subnet(v: int) -> int:
    hosts_per_subnet: int = 2**(32 - v)-2
    logger.info(f"{hosts_per_subnet}")
    return hosts_per_subnet

class Subcommand:
    def __init__(self, name: str, inputs: List[str], description: str, func):
        self.name = name
        self.inputs = inputs
        self.description = description
        self.func = func

subcommands = { "sbntm_sh_2_hts_p_sbnt": Subcommand("sbntm_sh_2_hts_p_sbnt", ["sbntm_sh"], "Calculates available hosts per subnet given short-hand subnet mask. eg: /24", subnet_mask_short2hosts_per_subnet) }

def usage(program: str):
    print(f"{program} <subcommand>")
    print("")
    print("Subcommands:")
    for subcommand_name in subcommands:
        scmd = subcommands[subcommand_name]
        print(f"    {scmd.name} {scmd.inputs}        - {scmd.description}")

def main():
    program: str = sys.argv.pop(0)

    if len(sys.argv) <= 0:
        usage(program)
        exit(1)

    for arg in sys.argv:
        if arg in subcommands:
            scmd = subcommands[arg]
            scmd.func()
        else:
            logger.error(f"Unknown subcommand: `{arg}`")
            exit(1)


if __name__ == '__main__':
    main()
