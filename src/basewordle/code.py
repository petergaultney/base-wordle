import re
from logging import getLogger
from pathlib import Path

_wordlist = open(Path(__file__).parent / "words" / "512.txt").read().splitlines()
assert len(_wordlist) == 512, len(_wordlist)
_VALUE_from_word = {w: i for i, w in enumerate(_wordlist)}

_SPECIAL_VALUES = {"whole": 1, "zilch": 0}
_SPECIAL_WORDS = {v: k for k, v in _SPECIAL_VALUES.items()}

assert set(_SPECIAL_VALUES).isdisjoint(_VALUE_from_word)
# assert _ONE not in _VALUE_from_word

_VALUE_from_digit = {
    # we use only the digits that require only a single syllable to pronounce.
    "1": 0b000,
    "2": 0b001,
    "3": 0b010,
    "4": 0b011,
    "5": 0b100,
    "6": 0b101,
    "8": 0b110,
    "9": 0b111,
}

_DIGIT_from_bit = {v: k for k, v in _VALUE_from_digit.items()}

_WORD = re.compile(r"[a-zA-Z]{5}")
_DIGIT = re.compile(r"[0-9]{1}")


logger = getLogger(__name__)


def decode(_str: str) -> bytes:
    # fundamentally big-endian, since bit 8 is 'next to' bit 9 in the string
    decoded_bytes = bytearray()
    char_pos = 0

    bits_defined = 0
    bit_accum = 0

    while char_pos < len(_str):
        word_match = _WORD.match(_str, char_pos)
        if word_match:
            word = _str[char_pos : char_pos + 5].lower()
            assert len(word) == 5
            char_pos += 5

            if word in _VALUE_from_word:
                word_value = _VALUE_from_word[word]
                bits_defined += 9
                bit_accum <<= 9
                # shift what we already have to the left by the number of
                # bytes we're about to receive
                bit_accum |= word_value
            elif word in _SPECIAL_VALUES:
                bits_defined += 1
                bit_accum <<= 1
                bit_accum |= _SPECIAL_VALUES[word]
            else:
                raise ValueError(
                    f"Invalid word '{word}' for base-wordle at position {char_pos}"
                )

        digit_match = _DIGIT.match(_str, char_pos)
        if digit_match:
            digit = _str[char_pos]
            if digit not in _VALUE_from_digit:
                raise ValueError(
                    f"Invalid digit {digit} for base-wordle at position {char_pos}"
                )
            char_pos += 1
            bits_defined += 3
            bit_accum <<= 3
            bit_accum |= _VALUE_from_digit[digit]
        while bits_defined >= 8:
            # we have at least one byte to write, starting with the 'highest 8 bits'
            decoded_bytes.append(bit_accum >> (bits_defined - 8) & 0xFF)
            bits_defined -= 8

        # anything less than 8 bits is overflow that we ignore when
        # the string finally ends.
    if bits_defined:
        if bit_accum & ((1 << bits_defined) - 1):
            logger.warning(
                f"Ignoring {bits_defined} bits of nonzero overflow: {bin(bit_accum)}"
            )
    return bytes(decoded_bytes)


def encode(_bytes: bytes, pad_digits: int = 0, titlecase: bool = True) -> str:
    """If pad_digits is zero, digit padding will not be used; only #
    words will be emitted. This will encode at most 1.8 bits of
    data per UTF-8 character emitted, excluding overflow bits.

    If pad_digits is greater than zero, N=pad_digits digits will be
    emitted after every N words. I.e. for pad_digits=2, you might get
    SpawnChest82, whereas for pad_digits=1, you would get Clock3Vault.

    pad_digits > 0 will result in a more efficient encoding, as it
    will average 2 bits per character emitted. pad_digits=2 is the
    recommended setting for most use cases, as two-digit numbers are
    relatively easy to read and remember.

    If titlecase is True, the first letter of each word will be
    capitalized for readbility. The value of the encoding is not
    affected by capitalization.
    """
    assert pad_digits >= 0, pad_digits
    emit_bits = (12 * pad_digits) or 9

    total_bits_encoded = 0
    encoded_str = ""
    bit_accum = 0
    bits_defined = 0

    def title(word: str) -> str:
        return word.title() if titlecase else word

    consecutive_digits = 0
    byte_pos = 0
    while byte_pos < len(_bytes):
        consecutive_words = 0
        consecutive_digits = 0

        while byte_pos < len(_bytes) and bits_defined < emit_bits:
            bit_accum <<= 8
            bit_accum |= _bytes[byte_pos]
            bits_defined += 8
            byte_pos += 1

        # we need 9 bits to emit a word.
        # if padding with digits, we only emit N words at a time before emitting digits.
        while bits_defined >= 9 and (consecutive_words < pad_digits or not pad_digits):
            # emit a word from the highest 9 bits
            word_value = bit_accum >> (bits_defined - 9) & 0x1FF
            encoded_str += title(_wordlist[word_value])
            bits_defined -= 9
            consecutive_words += 1
            total_bits_encoded += 9

        while bits_defined >= 3 and consecutive_digits < pad_digits:
            # emit a digit from the highest 3 bits
            digit_value = bit_accum >> (bits_defined - 3) & 0x7
            encoded_str += _DIGIT_from_bit[digit_value]
            bits_defined -= 3
            consecutive_digits += 1
            total_bits_encoded += 3

        # zero out any 'used' bits (above bits_defined), so
        # that we don't grow without bound.
        bit_accum &= (1 << (bits_defined + 1)) - 1
        if bits_defined == 0:
            bit_accum = 0

    assert bits_defined >= 0
    assert bits_defined < 9, f"We should have emitted a full word for {bits_defined}."
    if consecutive_digits > pad_digits:
        assert (
            bits_defined < 3
        ), f"We should have emitted a full digit for {bits_defined}."

    # we may have some bits left over that did not make a full word or
    # digit, so we need to pad them out to either 9 or 12 depending on
    # whether we're emitting digits or words and emit the last
    # characters with some overflow bits.  Those overflow bits will
    # always be zero in order to make the encoding deterministic.
    allowed_digits = pad_digits - consecutive_digits
    while bits_defined > 0 and allowed_digits * 3 >= bits_defined:
        # we can emit a digit or two to satisfy the encoding
        # and it will be most efficient.

        ander = (1 << min(bits_defined, 3)) - 1
        leftshift = 3 - bits_defined
        digit = _DIGIT_from_bit[(bit_accum & ander) << leftshift]
        encoded_str += digit
        bits_defined -= 3

    if bits_defined > 0:
        if bits_defined == 1:
            # danger! encoding this as a full word
            # will make the encoding look like we intended to encode an extra full byte.
            # therefore, we instead encode the one remaining bit specially.
            encoded_str += title(_SPECIAL_WORDS[bit_accum & 1])
            bits_defined -= 1
        else:
            ander = (1 << min(bits_defined, 9)) - 1
            leftshift = 9 - bits_defined
            print(
                f"{bits_defined} bits defined - anding by {bin(ander)} and leftshifting by {leftshift}"
            )
            encoded_str += title(_wordlist[(bit_accum & ander) << leftshift])
            bits_defined -= 9

    assert bits_defined <= 0, (bits_defined, pad_digits, byte_pos, bin(bit_accum))
    return encoded_str
