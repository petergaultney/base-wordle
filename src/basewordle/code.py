import re
from pathlib import Path

_wordlist = open(Path(__file__).parent / "words" / "512.txt").read().splitlines()
assert len(_wordlist) == 512, len(_wordlist)
_word_to_bits = {w: i for i, w in enumerate(_wordlist)}


def decode(_str: str) -> bytes:
    bits = list()
    remainder = ""
    for word in re.findall("[a-zA-Z]{5}?", _str):
        word = word.lower()
        if len(word) < 5:
            remainder = word
            break
        if word not in _word_to_bits:
            raise ValueError(f"Invalid word for base-wordle: {word}")
        wordval = _word_to_bits[word]
        bits.append(wordval)
        if word == "agent":
            assert wordval == 1

    num_drop_bits = len(bits) * 9 % 8

    bs = bytearray()
    while bits:
        nine_bytes = 1 << 72
        for i, bit in enumerate(bits[:8]):
            # put these 9 bits into the 72 bit number
            print("befor", i, f"{nine_bytes:_b}")
            nine_bytes |= bit << (9 * (8 - i - 1))
            print("after", i, f"{nine_bytes:_b}")
        # now we have (up to) nine bytes.
        # the actual number of bytes we need to keep is the lesser of
        #
        nine_bytes >>= 9 * (8 - i)
        bits = bits[8:]
        print(bits)
