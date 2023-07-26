import os

import pytest

from basewordle import decode, encode


def _bytes(_bytes):
    return " ".join([f"{b:0>8_b}" for b in _bytes])


def test_simple_roundtrip():
    assert decode(encode(b"012345678")) == b"012345678"


def test_properly_encoded_with_overflow_roundtrips():
    the_bytes = decode("AgentBreadCauseGuard")
    print(_bytes(the_bytes))
    assert encode(the_bytes) == "AgentBreadCauseGuard"


def test_improperly_encoded_with_overflow_decodes_to_correct_bytes(caplog):
    the_bytes = decode("AgentBreadCauseHandy")
    assert "Ignoring 4 bits of nonzero overflow: " in caplog.text
    print(_bytes(the_bytes))
    assert encode(the_bytes) == "AgentBreadCauseGuard"


def test_lots_of_random_bytes():
    for n in range(100):
        for i in range(10):
            the_bytes = os.urandom(n)
            encoded = encode(the_bytes)
            result_bytes = decode(encoded)
            assert result_bytes == the_bytes, (
                n,
                i,
                _bytes(the_bytes),
                _bytes(result_bytes),
            )


def test_having_exactly_eight_bytes_results_in_special_encodings():
    assert encode(b"76543210") == "DirtyJazzyStoryRadarCrossFatalFlashZilch"
    assert encode(b"76543211") == "DirtyJazzyStoryRadarCrossFatalFlashWhole"
    assert encode(b"76543212") == "DirtyJazzyStoryRadarCrossFatalFloatZilch"
    assert encode(b"01234567") == "CrashHairySpawnPolarErrorRebelOnionWhole"
    assert encode(b"01234568") == "CrashHairySpawnPolarErrorRebelOrbitZilch"
    assert encode(b"01234569") == "CrashHairySpawnPolarErrorRebelOrbitWhole"


def test_having_exactly_eight_bytes_results_in_no_extra_zero_bytes():
    bs = b"76543212"
    assert decode(encode(bs))[-1] == int(bs[-1])
    assert len(decode(encode(bs))) == 8


def test_pad_digits_two():
    assert decode(encode(b"0123456789", pad_digits=2)) == b"0123456789"


@pytest.mark.parametrize("pad_digits", [0, 1, 2, 3, 4, 5, 6])
def test_lots_of_random_bytes(pad_digits):
    for n in range(100):
        for i in range(10):
            the_bytes = os.urandom(n)
            encoded = encode(the_bytes, pad_digits=pad_digits)
            result_bytes = decode(encoded)
            print(n, i, encoded, _bytes(the_bytes))
            assert result_bytes == the_bytes, (
                n,
                i,
                _bytes(the_bytes),
                _bytes(result_bytes),
            )
