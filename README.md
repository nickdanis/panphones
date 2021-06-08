# Panphones!: a phonetic alphabet puzzle based on the NY Times Spelling Bee

Panphones! is a word-finding puzzle based on the NY Times Spelling Bee, adapted for the International Phonetic Alphabet. The same basic rules apply:

* Words must be at leat 4 phones long.
* Words must use the center phone, and any phone can be repeated.
* Words of length 4 are worth 1 point, and words of length n where n > 4 are worth n points.
* If a word uses all the phones in the chart, it is a Panphone, and worth 7 extra points.

## Notes on phonetic spelling

All transcriptions are based on the [Carnegie Mellon Pronouncing Dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict), which is "an open-source machine-readable pronunciation dictionary for North American English that contains over 134,000 words and their pronunciations", as implemented by nltk. The ARPA-bet symbols were converted to IPA, and all stress was ignored. The CMU does not use schwa as a symbol, so if you're expecting to see [ə], it's likely [ʌ] instead. Also, the rhotacized vowel "ER" has been transliterated as a syllabic-r [ɹ̩]. This is the only symbol with a diacritic, so pay attention as it is not interchangeable with consonantal [ɹ]. The exact transcriptions may differ in conventions from textbook to textbook as a result.

## Wordlist curation

The wordlist for the game created by the `generate_dict.py` script in the `data/` directory. The general method is as follows:

* Load all individual words from the nltk implementation of the Brown corpus (`nltk.corpus.brown.words()`)
* Tag these words for part of speech
* Filter out certain parts of speech (e.g. foreign words, proper nouns) and words containing digits or other punctuation (viewable in `data/taggedlist.txt`)
* Get the most common 20,000 items from this list, and get their pronounciations from the CMU dictionary (words that had no entries in the CMU dict are shown in `data/lostwords.txt`).
* The final list is in human-readable format in `data/game-list.txt`. 

The script converts this list to a dictionary tailored to the game, and exports this as `data/game-dict.json`. This file is imported when the game is loaded. Changes can be made to the process of curating the wordlist as described above, but it must be exported in this format for the game to function. 

## Playing the game

The game is currently a text-only command-line game. To start, run `python game.py`. A random puzzle is generated on every start. You can enter guesses either as IPA symbols (having an IPA keyboard helps), or as digits corresponding to the symbols on the chart. If you enter a guess in numbers, the string in IPA will be shown for confirmation. 

For debugging and testing purposes. you can also type `show answers` to see how the current puzzle is constructed. 