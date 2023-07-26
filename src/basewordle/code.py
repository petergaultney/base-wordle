import re
from pathlib import Path

_wordlist = open(Path(__file__).parent / "words" / "512.txt").read().splitlines()
assert len(_wordlist) == 512, len(_wordlist)
_word_to_bits = {w: i for i, w in enumerate(_wordlist)}


_WORD = re.compile(r"[a-zA-Z]{5}")
_DIGITS = re.compile(r"[0-9]{1-2}")


def decode(_str: str) -> bytes:
    # fundamentally big-endian, since bit 8 is 'next to' bit 9 in the string
    bs = bytearray()
    char_pos = 0

    bits_defined = 0
    nine_bytes = 1 << 72

    while char_pos < len(_str):
        word_match = _WORD.match(_str, char_pos)
        if word_match:
            bits_defined += 9
            word = _str[char_pos : char_pos + 5].lower()
            assert len(word) == 5
            char_pos += 5
            if word not in _word_to_bits:
                raise ValueError(f"Invalid word for base-wordle: {word}")

            bit_value = _word_to_bits[word]
            nine_bytes |= bit_value << (72 - bits_defined)

        if bits_defined == 72:
            # we have 9 bytes, so we can decode them
            for i in range(8):
                bs.append(nine_bytes >> (8 * (8 - i)) & 0xFF)
                bits_defined -= 8
            nine_bytes = 1 << 72

    if bits_defined > 8:
        for i in range(bits_defined // 8):
            bs.append(nine_bytes >> (8 * (8 - i)) & 0xFF)
        bits_defined = 0
        nine_bytes = 1 << 72

    return bytes(bs)

    while bits:
        eight_words = bits[:8]
        for i, bit in enumerate(eight_words):
            # put these 9 bits into the 72 bit number
            print("befor", i, f"{nine_bytes:_b}")
            nine_bytes |= bit << (9 * (8 - i - 1))
            bits_defined += 9
            print("after", i, f"{nine_bytes:_b}")
        # now we have (up to) nine bytes.
        # the actual number of bytes we need to keep is at most nine,
        # but if we had less than 8 words, we have to drop bits until we
        # get to a whole byte.
        #
        # with 7 words we have 63 bits, so we need to drop 2 bytes to
        # get down to 56 bits, which is 7 bytes.
        # Anything less than 7 words only drops one additional byte.
        num_bytes = bits_defined // 8

        for i in range(num_bytes):
            bs.append(nine_bytes >> (8 * (8 - i)) & 0xFF)

        for b in bs:
            print(bin(b))

        bits = bits[8:]

    return bytes(bs)
