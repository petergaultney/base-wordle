"""CLI for base-wordle. Must provide either a string to decode or a path to file to encode."""
import argparse
import sys
from pathlib import Path

from .code import decode, encode

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        help=(
            "Encode file if it exists and is non-empty."
            " Otherwise, read stdin and decode the input string into the file."
        ),
    )
    parser.add_argument(
        "--pad-digits",
        type=int,
        default=0,
        help="A more efficient encoding that embeds some digits too.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only base-wordle the first N bytes of the file.",
    )
    parser.add_argument(
        "--hex",
        help="Decode a hex string into bytes, then encode as base-wordle.",
    )
    args = parser.parse_args()

    the_file = Path(args.file)
    if the_file.exists() and the_file.stat().st_size > 0:
        the_bytes = the_file.read_bytes()
        if args.limit:
            the_bytes = the_bytes[: args.limit]
        print(encode(the_bytes, pad_digits=args.pad_digits))
    else:
        with open(the_file, "wb") as f:
            f.write(decode(sys.stdin.read()))
