#!/usr/bin/env python3

import subprocess
import argparse
import sys
import os

parser = argparse.ArgumentParser(prog="JDBL", description='JDBL interface')

def run():
    program = None
    if sys.argv[1] == "compile":
        program = "compile.py"
    elif sys.argv[1] == "debloat":
        program = "jdbl.py"
    elif sys.argv[1] == "usage":
        program = "usage.py"
    elif sys.argv[1] == "verify":
        program = "verify.py"
    elif sys.argv[1] == "bloat_report":
        program = "bloat_report.py"
    subprocess.call("./%s %s" % (program, " ".join(sys.argv[2:])), shell=True)

if __name__ == "__main__":
    run()