import itertools, random, re, json
from collections import defaultdict
from ast import literal_eval

class Puzzle:
    puzzle_levels = ['Underspecified', 'Minimal', 'Weak Position', 'Lenited', 'Reduced', 'Strong Position', 'Saturated', 'Hardened', 'Optimal']
    instructions = "Welcome to Panphones! [...]"

    def __init__(self, raw_game_dict="game-dict.json"):
        self.phones = tuple() # all 7 phones of the game
        self.center = '' # the center phone
        self.total_points = 0 # absolute max possible points
        self.top_score = 0 # points required to reach top level
        self.player_score = 0 # player's current score
        self.player_progress = 0 # player's current progress (for score bar)
        self.chart_layout = [] # ordered list of all non-center phones, for chart generation
        self.player_level = self.puzzle_levels[0] # current player level
        self.puzzle_ranges = dict() # dictionary of point values needed to reach each level
        self.answer_dict = defaultdict(list) # answer dictionary
        self.raw_game_dict = raw_game_dict # the passed filename for the game_dict json file
        self.game_dict = dict() # the parsed game_dict
        self.found = [] # running log of all answers found
        self.load_game_dict() # load dict on init
    
    def load_game_dict(self):
        with open(f"data/{self.raw_game_dict}","r") as f:
            raw_dict = json.load(f)
        self.game_dict = {literal_eval(k):v for k, v in raw_dict.items()}
    
    def build_chart(self):
        '''
        picks a random length-7 key from the game dict, and sets a random phone
        from this key as the center letter
        also generates all possible combos of these phones that include center letter
        '''
        possible_phones = [pron for pron in self.game_dict.keys() if len(pron) == 7]
        self.phones = random.choice(possible_phones)
        self.center = random.choice(self.phones)
        self.chart_layout = [phone for phone in self.phones if phone != self.center]
        
    def build_answers(self):
        '''based on the chosen phones, finds all possible words that can be legally built
        assigns these to answer_dict'''
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

    def evaluate_guess(self, guess):
        points = 0
        if len(guess) < 4:
            message = "Too short"
        elif self.center not in guess:
            message = "Missing center phone"
        elif guess in self.found:
            message = "Already found"
        elif guess in self.answer_dict.keys():
            points, message = self.score_answer(guess)
            self.found.append(guess)
        else:
            message = "Not in word list"
        return points, message

    def score_answer(self, guess):
        '''takes an GOOD guess and returns the number of points
        and a message'''
        message = ''
        if len(guess) == 4:
            points = 1
            message += f"{points} point: "
        elif len(set(guess)) == 7:
            points = len(guess) + 7
            message += f"\U0001F308Panphone!\U0001F308 {points} points: "
        else:
            points = len(guess)
            message += f"Nice! {points} points: "
        message += ', '.join(self.answer_dict[guess])
        return points, message

    def count_points(self):
        '''counts the total point vowel for the puzzle'''
        for ans in self.answer_dict.keys():
            self.total_points += self.score_answer(ans)[0]

    def get_level(self):
        '''assigns the puzzle levels and player progress and level based on the total points'''
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
        self.player_progress = self.player_score / self.top_score

    def check_endgame(self):
        has_won = False
        message = ''
        if self.player_score >= self.top_score and self.player_level != self.puzzle_levels[-1]:
            has_won = True
            message += f"You have reached the highest level: {self.puzzle_levels[-1]}!"
        if self.player_score >= self.total_points:
            has_won = True
            message += "\nYou found all the words! You are hereby coronalized. \U0001F451\U0001F445"
        return has_won, message
    

class TextPlay(Puzzle):
    '''functions for playing Panphones in the commandline'''
    
    def parse_ipa(self, raw_guess):
        '''converts string of IPA characters to list, respecting digraphs'''
        guess = re.findall(r"(aɪ|dʒ|eɪ|ɔɪ|tʃ|oʊ|aʊ|ɹ̩|\w)",raw_guess)
        
        return tuple(guess)

    def parse_digits(self, raw_guess, verbose=True):
        '''converts digits to IPA symbols based on index
        accepts mixed digits and IPAǃ'''
        guess = []
        for n in list(raw_guess):
            if re.search(r'\d',n):
                guess.append(self.phones[int(n)])
            else:
                guess.append(n)
        if verbose:
            print(f"IPA: [{''.join(guess)}]")
        return tuple(guess)

    def print_levels(self):
        '''print the puzzle levels as a fancy list'''
        formatted_levels = [f"{lvl} ({pts})" for pts, lvl in sorted(self.puzzle_ranges.items())]
        print(", ".join(formatted_levels))

    def print_chart(self,shuffle=False):
        '''prints the game chart'''
        if shuffle:
            random.shuffle(self.chart_layout)
        sym = lambda x: f"{self.chart_layout[x]}({self.phones.index(self.chart_layout[x])})"
        cen = f"{self.center}({self.phones.index(self.center)})"
        print()
        print(f"\t\t{sym(0)}")
        print(f"\t{sym(1)}\t\t{sym(2)}")
        print(f"\t\t{cen}")
        print(f"\t{sym(3)}\t\t{sym(4)}")
        print(f"\t\t{sym(5)}")
        print()
    
    def score_bar(self):
        '''generates and prints the score bar'''
        self.get_level()
        padding = len(max(self.puzzle_levels,key=len)) + 1
        length = 30
        progress = int(self.player_progress * length)
        bar = ("=" * (progress - len(str(self.player_score)))) + str(self.player_score) + '-' * (length - progress)
        print(f"{self.player_level:{padding}} {bar}")

def play_puzzle():
    puz = TextPlay()
    puz.set_puzzle()
    while puz.total_points < 60:
        puz = TextPlay()
        puz.set_puzzle()
    print("\n",puz.instructions,"\n")
    puz.score_bar()
    puz.print_chart()
    shuffle=False
    raw_guess = input("Guess: ")
    while raw_guess != "quit":
        if re.search(r"\d+",raw_guess):
            try:
                guess = puz.parse_digits(raw_guess)
            except:
                print("Use only the digits on the puzzle!")
                raw_guess = input("Guess: ")
                continue 
        else:
            guess = puz.parse_ipa(raw_guess)
        if raw_guess == "show answers":
            for key, value in puz.answer_dict.items():
                print(f"{''.join(key)}\t{', '.join(value)}")
        elif raw_guess == 'n':
            play_puzzle()
            return
        elif raw_guess == "idkfa":
            puz.player_score += 10
        elif raw_guess == "shuffle":
            shuffle = True
        elif raw_guess == "levels":
            puz.print_levels()
        else:
            points, message = puz.evaluate_guess(guess)
            print(message)
            puz.player_score += points
        has_won, message = puz.check_endgame()
        if has_won:
            print(message)
            user = input("(k)eep playing, (n)ew game, (q)uit\n")
            if user == 'n':
                play_puzzle()
                return
            elif user == 'q':
                return
        puz.score_bar()
        puz.print_chart(shuffle=shuffle)
        shuffle=False
        raw_guess = input(f"Guess: ")

def main():
    play_puzzle()

if __name__ == '__main__':
    main()



