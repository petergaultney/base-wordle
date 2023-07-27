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
characters. For instance, here is a shortened, 6-character hash of a
commit from the BIP39 repo: `ce1862`. That hash contains 24 bits of
entropy, which is sufficient in most cases to uniquely identify a
moment in time in the life of your repository.

What it _isn't_ is memorable, or easy to communicate. But 24 bits is
very easy to communicate using base-wordle, because you can use 3 of
these 9-bit words to represent those three bytes. `ce1862` (in
hexadecimal) is `SprayCrawlNight` in base-wordle. I bet you can
remember that for long enough to switch browser tabs!

## Leftovers/padding

...docs coming soon.

## base-wordle1, base-wordle2, etc.

Numbers can make these things even easier to communicate!

When encoding, you can add one or more digits after each 5-letter word.

Numbers actually encode more information per character, and most of
them are one syllable, easy to read, and easy to remember.

This behavior is not enabled by default but is available via the
minimal CLI and also via the `encode` Python function.

# Installation/Usage

`pip install basewordle`

* encode:

`cat <file> | python -m basewordle`
`python -m basewordle --input-file <file>`

* decode:

`echo "CrashHairySpawnPolarErrorRebelOrbitZilch" | python -m basewordle -d > output.b`
`python -m basewordle -d --input-file input.b --output-file output.b`
