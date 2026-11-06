#!/usr/bin/env python3
"""Copy the shared worksheet helpers into independently installable skills."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if a bundled copy differs")
    args = parser.parse_args()
    tools = Path(__file__).resolve().parent
    code = (tools / "worksheet.py").read_bytes()
    for skill in ("cards", "read-along", "practice"):
        destination = tools.parent / "skills" / f"gogoga-words-{skill}" / "scripts" / "worksheet.py"
        if args.check:
            if not destination.is_file() or destination.read_bytes() != code:
                parser.error(f"Out-of-date worksheet helper: {destination}")
        else:
            destination.write_bytes(code)


if __name__ == "__main__":
    main()
