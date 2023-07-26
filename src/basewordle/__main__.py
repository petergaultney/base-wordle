import sys

from .code import decode

if __name__ == "__main__":
    print(" ".join([f"{b:_b}" for b in decode(sys.argv[1])]))
