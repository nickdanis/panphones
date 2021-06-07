import nltk
from collections import defaultdict
import itertools
import random
import re

import json
from ast import literal_eval

def load_game_dict():
    with open("game-dict.json","r") as f:
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
        self.player_score = 0
        self.answer_dict = defaultdict(list)
        self.game_dict = game_dict
    
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
    
    def set_puzzle(self, min=1):
        '''
        sets a puzzle, with an optional minimum total point value
        '''
        while self.total_points < min:
            self.build_chart()
            self.build_answers()
            self.count_points()

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

    def print_chart(self):
        others = [phone for phone in self.phones if phone != self.center]
        print(f"\t\t{others[0]}")
        print(f"\t{others[1]}\t\t{others[2]}")
        print(f"\t\t{self.center}")
        print(f"\t{others[3]}\t\t{others[4]}")
        print(f"\t\t{others[5]}")

def play_puzzle(game_dict):
    puz = Puzzle(game_dict)
    puz.set_puzzle(50)
    puz.print_chart()
    raw_guess = input("Guess: ")
    while raw_guess != "quit":
        guess = parse_answer(raw_guess)
        if raw_guess == "show answers":
            print(puz.answer_dict)
        elif len(guess) < 4:
            print("too short")
        elif puz.center not in guess:
            print("missing center phone")
        elif guess in puz.answer_dict.keys():
            points = puz.answer_points(guess)
            puz.player_score += points
        else:
            print("not in word list")
        if puz.player_score == puz.total_points:
            scr = "point" if puz.player_score == 1 else "points"
            print(f"You got {puz.player_score} {scr} out of {puz.total_points}.")
            user = input("You win! Play again? (y/n)")
            if user == 'y':
                play_puzzle(game_dict)
                return
            else:
                return
        puz.print_chart()
        raw_guess = input(f"Score: {puz.player_score} of {puz.total_points}\nGuess: ")
    scr = "point" if puz.player_score == 1 else "points"
    print(f"You got {puz.player_score} {scr} out of {puz.total_points}.")

def main():
    game_dict = load_game_dict()
    play_puzzle(game_dict)

if __name__ == '__main__':
    main()



