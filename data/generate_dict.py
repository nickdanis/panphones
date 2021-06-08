import nltk, re, json, random, string
from nltk.corpus import brown
from collections import Counter, defaultdict
from random import sample

'''
run this script to modify the wordlist for the game
currently it takes the num_words most common words from the Brown corpus
consisting of only letter characters (no punctuation or numerals)
'''

# this is the 'most common' words to extract
num_words = 20000

# matching pattern
# if you want to include hyphenated words or contractions, modify this pattern
game_word = re.compile(r"^[A-Za-z]+$")

# the following parts of speech will not be included
# run nltk.help.upenn_tagset() for definitions
banned_pos = ["NNP","NNPS","SYM","LS","FW"]

## bad word filtering functions
# make a cipher with random seed 42
random.seed(42)
cipher = list(string.ascii_lowercase)
random.shuffle(cipher)

# make encoding and decoding dictionaries and function
alpha = list(string.ascii_lowercase)

encode = dict()
for code, letter in zip(cipher, alpha):
    encode[letter] = code

decode = dict()
for code, letter in zip(cipher, alpha):
    decode[code] = letter

def code_word(code_dic, word):
    result = ''
    for s in word:
        result += code_dic[s]
    return result
## end bad word filtering functions

def to_ipa(cmu):
    '''
    convert CMU ARPABET to IPA
    used in generate_dict.py
    '''
    arpa_dict = {'AY' : 'aɪ',
			'D' : 'd',
			'IY' : 'i',
			'V' : 'v',
			'AE' : 'æ',
			'JH' : 'dʒ',
			'UH' : 'ʊ',
			'T' : 't',
			'Y' : 'j',
			'AH' : 'ʌ',
			'G' : 'g',
			'Z' : 'z',
			'P' : 'p',
			'TH' : 'θ',
			'M' : 'm',
			'R' : 'ɹ',
			'K' : 'k',
			'EH' : 'ɛ',
			'EY' : 'eɪ',
			'NG' : 'ŋ',
			'ZH' : 'ʒ',
			'HH' : 'h',
			'SH' : 'ʃ',
			'OY' : 'ɔɪ',
			'S' : 's',
			'AO' : 'ɔ',
			'F' : 'f',
			'W' : 'w',
			'IH' : 'ɪ',
			'DH' : 'ð',
			'L' : 'l',
			'N' : 'n',
			'CH' : 'tʃ',
			'AA' : 'ɑ',
			'B' : 'b',
			'OW' : 'oʊ',
			'UW' : 'u',
			'AW' : 'aʊ',
			'ER' : 'ɹ̩'}
    cmu_ipa = []
    for word, pron in cmu:
        ipa = []
        for seg in pron:
            ipa.append(arpa_dict[re.sub(r"\d","",seg)])
        cmu_ipa.append((word, ipa))
    return cmu_ipa

def make_game_dict(game_list):
    '''
    Used in generate_dict.py. Structure of game_dict:

    key: tuple of sorted, unique IPA characters
    value: list of tuple pairs,
    where each pair is (string of the orthographic word, list of the IPA characters)
    '''
    game_dict = defaultdict(list)
    for word, pron in game_list:
        k = tuple(sorted(set(pron)))
        game_dict[k].append((tuple(pron),word))
    return game_dict

# load a whole lotta words from Brown
raw_brown = brown.words()

print(f"Length of Brown corpus words: {len(raw_brown)}")

tagged_brown = nltk.pos_tag(raw_brown)

print(f"Done tagging...")

filtered_tagged = [(word.lower(), pos) for word, pos in tagged_brown if pos not in banned_pos and game_word.match(word)]

# for inspection
with open('taggedlist.txt','w',encoding='utf-8') as f:
    for word in filtered_tagged:
        f.write(f"{word}\n")

filtered_brown = [word for word, pos in filtered_tagged]

# get the most common num_words for the game
master_list_b = [word for word, i in Counter(filtered_brown).most_common(num_words)]

# filtering out bad words

with open('badwords.txt','r',encoding='utf-8') as f:
    bad_coded = f.readlines()

bad = [code_word(decode, word.strip()) for word in bad_coded]

master_list = [word for word in master_list_b if word not in bad]

print(f"Unique words extracted: {len(master_list)}")

# cross-reference these common words to ones that have pronunciations in CMU
cmu = nltk.corpus.cmudict.entries()
filtered_cmu = [(word, pron) for word, pron in cmu if word in master_list]
game_list = to_ipa(filtered_cmu)

cmu_words = [word for word, pron in cmu]
lost_words = [word for word in master_list if word not in cmu_words]

print(f"Words not in CMU: {len(lost_words)}")

with open('lostwords.txt','w',encoding='utf-8') as f:
    for word in lost_words:
        f.write(f"{word}\n")

with open('game-list.txt','w',encoding='utf-8') as f:
    for word, pron in game_list:
        f.write(f"{word}\t{''.join(pron)}\n")

print(f"Total game words: {len(game_list)}")
print(f"Sample from list: {sample(game_list, 10)}")


game_dict = make_game_dict(game_list)

print(f"Sample from dictionary: {sample(game_dict.items(), 10)}")

# https://stackoverflow.com/questions/7001606/json-serialize-a-dictionary-with-tuples-as-key
with open("game-dict.json", "w") as f:
    json.dump({str(k):v for k, v in game_dict.items()}, f)

print("Finished.")



