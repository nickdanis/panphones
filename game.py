import nltk
from collections import defaultdict
import itertools
import random
import re
import numpy as np

import json
from ast import literal_eval

def load_game_dict():
    with open("data/game-dict.json","r") as f:
        raw_dict = json.load(f)
    game_dict = {literal_eval(k):v for k, v in raw_dict.items()}
    return game_dict

def parse_answer(user):
    result = re.findall(r"(aɪ|dʒ|eɪ|ɔɪ|tʃ|oʊ|aʊ|ɹ̩|\w)",user)
    return tuple(result)

class Puzzle:
    def __init__(self, game_dict):
        self.phones = tuple()
        self.center = ''
        self.total_points = 0
        self.top_score = 0
        self.player_score = 0
        self.puzzle_levels = ['Underspecified','Minimal', 'Elided', 'Reduced', 'Saturated', 'Optimal']
        self.player_level = self.puzzle_levels[0]
        self.puzzle_ranges = dict()
        self.answer_dict = defaultdict(list)
        self.game_dict = game_dict
        self.found = []
        self.instructions = "Welcome to Panphones! Inspired by the NY Times Spelling Bee game. Find as many English words as you can using the symbols shown. Words must be at least four phones long and they must use the center phone, though you can repeat symbols. Pronunciations are based on the Carnegie Mellon Pronouncing Dictionary. You can either type the IPA symbols as you see them, or enter a string of the corresponding digits (no spaces in either case). Note that the puzzle contains both r and syllabic r! Type 'shuffle' to shuffle the chart. Type 'quit' at any time to quit."
    
    def build_chart(self):
        '''
        picks a random length-7 key from the game dict, and sets a random phone
        from this key as the center letter
        also generates all possible combos of these phones that include center letter
        '''
        possible_phones = [pron for pron in self.game_dict.keys() if len(pron) == 7]
        self.phones = random.choice(possible_phones)
        self.center = random.choice(self.phones)
        
        
    def build_answers(self):
        combos = []
        # find all combinations of phones of min length 4 that contain the center phone
        for i in range(4,len(self.phones)+1):
            for n in itertools.combinations(self.phones,i):
                if self.center in n:
                    combos.append(tuple(sorted(n)))
        subset_dict = {k: self.game_dict[k] for k in combos if k in self.game_dict}
        answer_pairs = [pair for answer in subset_dict.values() for pair in answer]
        for pron, word in answer_pairs:
            self.answer_dict[tuple(pron)].append(word)
    
    def set_puzzle(self, num=None):
        '''
        sets a puzzle, with an optional minimum total point value
        '''
        self.build_chart()
        self.build_answers()
        self.count_points()
        self.get_level()

    def answer_points(self, answer_tuple, verbose=True):
        message = ''
        if len(answer_tuple) == 4:
            points = 1
            message += f"{points} point: "
        elif len(set(answer_tuple)) == 7:
            points = len(answer_tuple) + 7
            message += f"Panphone! {points} points: "
        else:
            points = len(answer_tuple)
            message += f"Nice! {points} points: "
        if verbose:
            message += ', '.join(self.answer_dict[answer_tuple])
            print(message)
        return points

    def count_points(self):
        for ans in self.answer_dict.keys():
            self.total_points += self.answer_points(ans,verbose=False)

    def print_chart(self,shuffle=False):
        others = [phone for phone in self.phones if phone != self.center]
        if shuffle:
            random.shuffle(others)
        sym = lambda x: f"{others[x]}({self.phones.index(others[x])})"
        print(f"\t\t{sym(0)}")
        print(f"\t{sym(1)}\t\t{sym(2)}")
        print(f"\t\t{self.center}({self.phones.index(self.center)})")
        print(f"\t{sym(3)}\t\t{sym(4)}")
        print(f"\t\t{sym(5)}")

    def get_level(self):
        self.top_score = int(self.total_points - self.total_points * .1)
        diff = int(self.top_score / (len(self.puzzle_levels)-1))
        level_ranges = {1 : self.puzzle_levels[1], self.top_score : self.puzzle_levels[-1]}
        for lvl in self.puzzle_levels[2:-1]:
            range = self.puzzle_levels.index(lvl) * diff
            level_ranges[range] = lvl
        for pts, lvl in sorted(level_ranges.items(), reverse=True):
            if self.player_score >= pts:
                self.player_level = lvl
                break
        self.puzzle_ranges = level_ranges

    def score_bar(self):
        self.get_level()
        padding = len(max(self.puzzle_levels,key=len)) + 1
        length = 30
        progress = int((self.player_score / self.top_score) * length)
        bar = ("=" * (progress - len(str(self.player_score)))) + str(self.player_score) + '-' * (length - progress)
        bar = f"{bar}"
        #print(f"{self.player_score} of {self.top_score} points.")
        print(f"{self.player_level:{padding}} {bar}")


def play_puzzle(game_dict):
    puz = Puzzle(game_dict)
    puz.set_puzzle()
    while puz.total_points < 60:
        puz = Puzzle(game_dict)
        puz.set_puzzle()
    print(puz.instructions)
    for pts, lvl in sorted(puz.puzzle_ranges.items()):
        print(f"{pts}:\t{lvl}")
    puz.score_bar()
    puz.print_chart()
    shuffle=False
    raw_guess = input("Guess: ")
    while raw_guess != "quit":
        if re.match(r"\d+",raw_guess):
            guess = []
            for n in list(raw_guess):
                guess.append(puz.phones[int(n)])
            guess = tuple(guess)
            print(f"IPA: [{''.join(guess)}]")
        else:
            guess = parse_answer(raw_guess)
        if raw_guess == "show answers":
            for key, value in puz.answer_dict.items():
                print(f"{''.join(key)}\t{', '.join(value)}")
        elif raw_guess == "idkfa":
            puz.player_score += 10
        elif raw_guess == "shuffle":
            shuffle = True
        elif len(guess) < 4:
            print("Too short")
        elif puz.center not in guess:
            print("Missing center phone")
        elif guess in puz.found:
            print("Already found")
        elif guess in puz.answer_dict.keys():
            points = puz.answer_points(guess)
            puz.player_score += points
            puz.found.append(guess)
        else:
            print("Not in word list")
        if puz.player_score >= puz.top_score and puz.player_level != puz.puzzle_levels[-1]:
            puz.score_bar()
            print("You have reached the highest level!")
            user = input("(k)eep playing, (n)ew game, (q)uit\n")
            if user == 'n':
                play_puzzle(game_dict)
                return
            elif user == 'q':
                return
        if puz.player_score >= puz.total_points:
            print("You got all the words! You are hereby coronalized.")
            user = input("(n)ew game, (q)uit\n")
            if user == 'n':
                play_puzzle(game_dict)
                return
            else:
                return
        puz.score_bar()
        puz.print_chart(shuffle=shuffle)
        raw_guess = input(f"Guess: ")

def main():
    game_dict = load_game_dict()
    play_puzzle(game_dict)

if __name__ == '__main__':
    main()



