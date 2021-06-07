import nltk
from collections import defaultdict
import itertools
import random
import re

import json
from ast import literal_eval

# dev branch comment

def to_ipa(cmu):
    '''
    convert CMU ARPABET to IPA
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

def parse_answer(user):
    result = re.findall(r"(aɪ|dʒ|eɪ|ɔɪ|tʃ|oʊ|aʊ|ɹ̩|\w)",user)
    return result

def make_game_dict(game_list):
    '''
    Structure of game_dict:

    key: tuple of sorted, unique IPA characters
    value: list of tuple pairs,
    where each pair is (string of the orthographic word, list of the IPA characters)
    '''
    game_dict = defaultdict(list)
    for word, pron in game_list:
        k = tuple(sorted(set(pron)))
        game_dict[k].append((tuple(pron),word))
    return game_dict

def isolate_segments(game_list):
    '''
    gets individual segments from word list
    OBSOLETE??
    '''
    segments = [seg for word, pron in game_list for seg in pron]
    segments = list(set(segments))
    return segments

def generate_phones(segments):
    '''
    picks 7 random phones, with one of these marked as the center phone
    OBSOLETE
    '''
    phones = random.sample(segments, 7)
    center = random.choice(phones)
    return (phones, center)

def phone_combos(phones, center):
    '''
    find all combinations of phones of min length 4 that contain the center phone
    '''
    combos = []
    for i in range(4,len(phones)+1):
        for n in itertools.combinations(phones,i):
            if center in n:
                combos.append(tuple(sorted(n)))
    return combos

def make_puzzle():
    '''
    makes a puzzle based on a starting panphone
    '''
    possible_panphones = [pron for pron in game_dict.keys() if len(pron) == 7]
    key_panphone = random.choice(possible_panphones)
    center = random.choice(key_panphone)
    phones = list(key_panphone)
    combos = phone_combos(phones, center)
    answers = dict()
    for combo in combos:
        if combo in game_dict:
            answers[combo] = game_dict[combo]
    pron_key = defaultdict(list)
    answer_pairs = [pair for answer in answers.values() for pair in answer]
    for pron, word in answer_pairs:
        pron_key[tuple(pron)].append(word)
    return answers, pron_key, center, phones


def initialize_data():
    '''
    define wordlist, make game dict
    '''
    cmu = nltk.corpus.cmudict.entries()
    global game_list, segments, game_dict
    game_list = to_ipa(cmu)
    segments = isolate_segments(game_list)
    game_dict = make_game_dict(game_list)

def load_game_dict():
    global game_dict
    with open("game-dict.json","r") as f:
        raw_dict = json.load(f)
    game_dict = {literal_eval(k):v for k, v in raw_dict.items()}
    return game_dict

def print_phones(center, phones):
    others = [phone for phone in phones if phone != center]
    print(f"\t\t{others[0]}")
    print(f"\t{others[1]}\t\t{others[2]}")
    print(f"\t\t{center}")
    print(f"\t{others[3]}\t\t{others[4]}")
    print(f"\t\t{others[5]}")

def print_phones_rainbow(center, phones):
    others = [phone for phone in phones if phone != center]
    print(f"\t\t{others[0]}\t{others[1]}")
    print(f"\t{others[2]}\t\t\t{others[3]}")
    print(f"{others[4]}\t\t    {center}\t\t\t{others[5]}")

def answer_points(guess_key, verbose=True):
    if len(guess_key) == 4:
        points = 1
    else:
        points = len(guess_key)
    if len(set(guess_key)) == 7:
        if verbose:
            print("Panphone!")
        points += 7
    return points

def puzzle_points(pron_key):
    total = 0
    for ans in pron_key.keys():
        total += answer_points(ans,verbose=False)
    return total


def play_puzzle():
    score = 0
    answers, pron_key, center, phones = make_puzzle()
    print_phones(center, phones)
    total = puzzle_points(pron_key)
    guess = input("Guess: ")
    while guess != "quit":
        guess_key = tuple(parse_answer(guess))
        if guess == "show answers":
            print(pron_key)
        elif len(guess_key) < 4:
            print("too short")
        elif center not in guess_key:
            print("missing center phone")
        elif guess_key in pron_key.keys():
            points = answer_points(guess_key)
            pts = "point" if points == 1 else "points"
            print(f"{', '.join(pron_key[guess_key])}, {points} {pts}.")
            score += points
        else:
            print("not in word list")
        if score == total:
            scr = "point" if score == 1 else "points"
            print(f"You got {score} {scr} out of {total}.")
            user = input("You win! Play again? (y/n)")
            if user == 'y':
                play_puzzle()
                return
            else:
                return
        print_phones(center, phones)
        guess = input(f"Score: {score} of {total}\nGuess: ")
    scr = "point" if score == 1 else "points"
    print(f"You got {score} {scr} out of {total}.")



def main():
    game_dict = load_game_dict()
    play_puzzle()

if __name__ == '__main__':
    main()



