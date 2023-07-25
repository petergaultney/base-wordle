#!/usr/bin/env python


def read_five(filename):
    with open(filename) as f:
        return set(map(lambda s: s.strip(), filter(None, f.read().splitlines())))


fives = read_five("src/basewordle/words/fives.txt")
foury = read_five("src/basewordle/words/foury.txt")
minus_58 = read_five("src/basewordle/words/minus_58.txt")
minus_27 = read_five("src/basewordle/words/minus_27.txt")

assert foury.isdisjoint(fives)
assert foury.isdisjoint(minus_58)
assert foury.isdisjoint(minus_27)
assert fives | minus_58 == fives
assert fives | minus_27 == fives
assert minus_58.isdisjoint(minus_27)

final = sorted([w for w in fives | foury if w not in (minus_58 | minus_27)])
for w in final:
    assert len(w) == 5

assert len(fives) == 555
assert len(foury) == 42, len(foury)
assert len(minus_27) == 27, len(minus_27)
assert len(minus_58) == 58, len(minus_58)
assert len(fives) + len(foury) - len(minus_58) - len(minus_27) == 512
assert len(final) == 512, final

with open("src/basewordle/words/512.txt", "w") as f:
    print("\n".join(final), file=f)

# print final list as an array that is 512/col_height wide
col_height = 64
for i, j in enumerate(range(col_height)):
    print(" ".join(final[i::col_height]))


fours = set([w[:4] for w in final])
assert len(fours) == 512
