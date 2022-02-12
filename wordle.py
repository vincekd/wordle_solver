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
    words = []
    with open(file_path, "r") as word_file:
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

    return (words, letter_counts)

def find_word(words, letters, guesses, sort_score):
    possible_words = [word for word in words if word.word not in guesses and word.usable(letters)]
    if sort_score:
        possible_words = sorted(possible_words, key=lambda word: word.score, reverse=True)
    return possible_words[0] if len(possible_words) > 0 else None

def solve(word, words, letters, sort_score, max_tries=-1, log=False):
    chars = [char for char in word]

    if log and word not in [w.word for w in words]:
        print("Word '%s' not in dictionary." % word)
        return None

    tries = 0
    guesses = []
    while (word not in guesses and (max_tries < 1 or tries < max_tries)):
        guess = find_word(words, letters, guesses, sort_score)
        tries += 1
        guesses.append(guess.word)

        if guess.word == word:
            if log:
                print("You won with '%s' in %i tries!" % (word, tries))
            return tries
        else:
            if log:
                print("Try %i: '%s' contains %i correct letters." % (tries, guess.word, len(set(chars).intersection(set(guess.chars)))))
            for index, char in enumerate(guess.chars):
                if char not in chars:
                    letters[char] = False
                else:
                    letters[char].add(index, guess.chars[index] == chars[index])

    if max_tries > 1 and tries >= max_tries and word not in guesses:
        print("Failed to find word: '%s'" % word)

    return tries

def get_letters(letter_counts):
    return {key: UsedChar() for key in letter_counts.keys()}

def get_average(words, letter_counts, sort_score, log=True):
    solutions = []
    fails = []
    for word in words:
        tries = solve(word.word, words, get_letters(letter_counts), sort_score)
        if tries > max_tries:
            if log:
                print("'%s' took more than max tries (%i)" % (word.word, tries))
            fails.append(word.word)
        solutions.append(tries)

    average = sum(solutions) / len(solutions)
    if log:
        print("Average solution: %.2f; Failed: %i" % (average, len(fails)))
    return average, len(fails)

if __name__=="__main__":
    dict_path = sys.argv[1]
    max_tries = 6
    word_length = 5
    sort_score = False
    log = True
    iterations = 50

    print("Solving wordle in %i tries %s letter sorting." % (max_tries, "with" if sort_score else "without"))

    words, letter_counts = all_possible_words(dict_path, word_length)

    if len(sys.argv) == 3: # check if specific word passed in to solve
        solve(sys.argv[2], words, get_letters(letter_counts), sort_score, max_tries, log)
    else: # otherwise do average of every word
        if sort_score is True:
            get_average(words, letter_counts, sort_score, log)
            # Average: 3.84 tries
            # Fails: 34
        else:
            averages = []
            fails = []
            while len(averages) < iterations:
                average, failed = get_average(random.sample(words, len(words)), letter_counts, sort_score, log)
                averages.append(average)
                fails.append(failed)

            print("Random Average: %.2f; Failed average: %.2f" % ((sum(averages) / len(averages)), (sum(fails) / iterations)))
            # Average with 2 tries: 4.09 tries
            # Average with 50 tries: 4.12
            # Average with 50 tries/fails: 4.09 / 43.92
