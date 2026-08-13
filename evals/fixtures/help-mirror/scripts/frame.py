#!/usr/bin/env python3
"""Add a colored border to an image. Fixture: its --gap flag is documented nowhere."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a colored border to an image.")
    parser.add_argument("image")
    parser.add_argument("--width", type=int, default=20, help="Border width in pixels")
    parser.add_argument("--height", type=int, help="Border height; defaults to --width")
    parser.add_argument("--color", default="#ffffff", help="Border color as hex")
    parser.add_argument("--gap", type=int, default=0, help="Inner gap between image and border")
    parser.parse_args()
    raise SystemExit("fixture script — not meant to run")


if __name__ == "__main__":
    main()
