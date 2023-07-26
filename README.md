# Base-wordle

What the world(le) needs is another word-based encoding system for
binary data. In this case, a 9-bit encoding system, with one of 512 5
letter words standing in for each set of 9 bits... mostly.

9 bits may seem crazy, but there are a few advantages:

1. Every word can be five letters long, so the encoded string length
   has a stepwise linear relationship to the source data.
2. Every word can be uniquely pronounceable, such that there is no
   ambiguity when restricted to the list of common 5 letter English
   words.
3. Every word can have its accent on the first syllable, to make
   reading out loud easier for everyone.
4. Base64 is a very common 6 bit format, and 6 and 9 have a least
   common multiple of 18, so it is _fairly_ easy to alternate and
   convert between base64 and base-wordle.

The words are built on prior art; mostly, this is the
[BIP39 English wordlist](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt),
filtered to 5 letter words, then filtered again for various words that
don't fit the above restrictions or that I felt like dropping for no
particular reason. Since this leaves less than 512 words, I added some
four letter words from the BIPS wordlist that have an adjectival
version ending in `y`.

## Why would I actually use this?

There are a lot of cases where we want to represent something
determinstically and uniquely. One of the common cases is to provide a
unique, unopinionated, compressed reference to it. This is sometimes
called a `hash`.

Hashes have really nice properties, but they also have some not-nice
properties, and perhaps the main one is that they are just a jumble of
characters. For instance, here is the "git short hash" of a commit
from the BIP39 repo: `ce1862a`. That hash contains 28 bits of entropy,
which is sufficient in most cases to uniquely identify a moment in
time in the life of your repository.

What it _isn't_ is memorable, or easy to communicate. But 28 bits is
very easy to communicate using base-wordle, because you can use 3 of
these words to represent all but the last bit - and the last bit you
can represent in various ways (see below).


## Leftovers/padding

Okay, so 9 bits isn't really that convenient for representing 8-bit
bytes, because the least common multiple of 8 and 9 is 72, meaning
that before you hit 8 words, some of your bits can't complete a full
byte.

The good news is, we have an ace up our sleeve. When you need just a
couple more bits, there's one more unambiguous, pronounceable,
memorable way of representing those in a text encoding: numbers!

By using the numbers 1 through 9, we can represent 3 more bits of
information per numeric character. So if you need more than 0 but less
than 7 more bits of information to encode your bytes, just append one
or two digits to the end of your string.

In fact, these numeric digits are _more_ compact than the words, but
generally just as memorable when spread out amongst words. So, by
default, the encoding alternates two words and then two digits, to end
up with 24 bits per 12 characters, or two bits per character.

Because the digits are unambiguous, you can enable this option (or
not) depending on your preference.
