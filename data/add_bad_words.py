import string, random

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

# ask user for bad words
bad_words = []
bad_word = input("Enter a word, or 'quit': ")
while bad_word != 'quit':
    bad_words.append(code_word(encode,bad_word))
    bad_word = input("Enter a word, or 'quit': ")

# write coded words to file in append file
# you can run this script multiple times
# but you must run generate_dict.py after each time
# for the changes to apply to the game! 
with open('badwords.txt','a',encoding='utf-8') as f:
    for line in bad_words:
        f.write(f"{line}\n")
    

