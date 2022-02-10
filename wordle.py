import random, sys

class Word:
    def __init__(self, word):
        self.word = word
        self.chars = [char for char in word]
        self.score = 0

    def score_word(self, letter_counts):
        self.score = 0
        num_used = dict.fromkeys(self.chars, 0)
        for char in self.chars:
            num_used[char] += 1
            self.score += (letter_counts[char] / self.word.count(char)) * num_used[char]

    def usable(self, letters):
        for char in letters:
            if letters[char] is False:
                if char in self.chars:
                    return False
            elif len(letters[char].correct) > 0 or len(letters[char].incorrect) > 0:
                if char not in self.chars or not all(char == self.chars[index] for index in letters[char].correct) or not all(char != self.chars[index] for index in letters[char].incorrect):
                    return False
        return True

class UsedChar:
    def __init__(self):
        self.correct = set()
        self.incorrect = set()

    def add(self, index, correct):
        self.correct.add(index) if correct else self.incorrect.add(index)

def all_possible_words(file_path, word_length):
    with open(file_path, "r") as word_file:
        words = []
        letter_counts = dict()
        for word in word_file:
            word = word.lower().strip()
            if len(word) == word_length and word.isalpha():
                words.append(Word(word))
                for char in word:
                    if char not in letter_counts:
                        letter_counts[char] = 0
                    letter_counts[char] += 1

        for word in words:
            word.score_word(letter_counts)

        return words

def find_word(words, word_length, letters, guesses):
    possible_words = sorted([word for word in words if word.word not in guesses and word.usable(letters)], key=lambda word: word.score, reverse=True)
    return possible_words[0] if len(possible_words) > 0 else None

if __name__=="__main__":
    file_path = sys.argv[1]
    max_tries = 6
    word_length = 5
    word = sys.argv[2]
    chars = [char for char in word]
    words = all_possible_words(file_path, word_length)

    tries = 0
    guesses = []
    letters = dict()
    while (word not in guesses and tries < max_tries):
        guess = find_word(words, word_length, letters, guesses)
        if guess is None:
            print("no possible guesses: bad word — %s" % word)
            break
        tries += 1
        guesses.append(guess.word)

        if guess.word == word:
            print("You won with '%s' in %i tries!" % (word, tries))
            break
        else:
            print("Try %i: '%s' contains %i correct letters." % (tries, guess.word, len(set(chars).intersection(set(guess.chars)))))
            for index, char in enumerate(guess.chars):
                if char not in chars:
                    letters[char] = False
                else:
                    if char not in letters:
                        letters[char] = UsedChar()
                    letters[char].add(index, guess.chars[index] == chars[index])

    if tries >= max_tries and guesses[-1] != word:
        print("Failed to find word: '%s'" % word)
