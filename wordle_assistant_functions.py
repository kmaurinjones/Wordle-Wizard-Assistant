import numpy as np # for stats
import random # for randomly generating target and start words
import operator # for sorting letter frequency distribution
import time # for #dramaticeffect
import pandas as pd
import streamlit as st

english_alphabet = "abcdefghijklmnopqrstuvwxyz"

def get_letter_counts(word_list: list, letters: str = english_alphabet, sort: str = "descending", unique: bool = True):
    """
    Given a passed str of letters and a list of words, produces a frequency distribution of all letters

    Parameters:
    ------
    `word_list`: list
        list of words (str) from which word frequencies will be counted
    `letters`: str
        a string of letters to be counted. String must only be desired letters, with no spaces. Default is local variable containing all letters of the English alphabet
    `sort`: str
        if either "descending" or "ascending" are passed, returned list of tuples will be sorted accordingly, else returned dictionary will be unsorted
    `unique`: bool
        if True, only unique letters in a word are counted. That means that words with more unique letters are rated more highly than any words with duplicate letters

    Returns:
    ------
    `letters_counts_dict`: dict
        dictionary of {letter : count} pairs for each letter in passed `letters` sequence
    `sorted_counts_dicts`: list of tuples
        list of tuples. Format is ("letter", frequency). Ordered according to `sort` values
    """

    words_counts_dict = {}

    if unique == False:
        for word in word_list: # real dataset
            word_dict = {}

            for letter in word:
                if letter in word_dict:
                    word_dict[letter] += 1
                else:
                    word_dict[letter] = 1
            words_counts_dict[word] = word_dict
    else: # if unique == True

        for word in word_list: # real dataset
            word_dict = {}

            word_letters = set(letter for letter in word)

            for letter in word_letters:
                if letter in word_dict:
                    word_dict[letter] += 1
                else:
                    word_dict[letter] = 1
            words_counts_dict[word] = word_dict

    letters_counts_dict = {}

    for letter in letters:
        letters_counts_dict[letter] = 0

    for word, count_dict in words_counts_dict.items():
        # # print (word, count_dict)
        for letter, count in count_dict.items():
            letters_counts_dict[letter] += count

    if sort == "ascending":
        sorted_counts_dict = (sorted(letters_counts_dict.items(), key = operator.itemgetter(1), reverse = False))
        return sorted_counts_dicts

    if sort == "descending":
        sorted_counts_dict = sorted(letters_counts_dict.items(), key = operator.itemgetter(1), reverse = True)
        return sorted_counts_dict
    else:
        return letters_counts_dict
    
### Best first guesses for a given Wordle list

def best_guess_words(word_list: list, show_letters: bool = False):
    """
    Given a passed list of English words of a consistent length, calculates the most statistically optimal first guess words, alongside a rating for each word. 
    
    Rating = sum(frequency of each unique letter in that word) / sum (all unique letter frequencies in word_list) * 100, rounded to 2 decimals.

    ------
    Parameters:
    ------
    `word_list`: list
        list of words (str) of consistent length
    `show_letters`: bool
        if True, also # prints set of most optimal letters to guess

    ------
    Returns:
    ------
    `word_ratings`: list
        list of tuples. Format is [(word, rating)], where rating is calculated according to above formula
    `sorted_counts`: list of tuples
        list of tuples. Format is ("letter", frequency). Sorted according to `sort` value; ["descending" or "ascending"] if passed
    """
        
    english_alphabet = "abcdefghijklmnopqrstuvwxyz"

    sorted_counts = get_letter_counts(english_alphabet, word_list, sort = "descending")

    max_len_possible = len(word_list[0])

    ### Get words with the highest letter diversity
    while max_len_possible:

        best_letters = set()
        best_words = []

        for letter, freq in sorted_counts:
            best_letters.add(letter)
            if len(best_letters) == max_len_possible:
                break

        ### Get all words that have one of each of the 5 top most frequent letters
        for word in word_list:
            word_set = set()

            for letter in word:
                word_set.add(letter)

            if best_letters.issubset(word_set):
                best_words.append(word)

        if len(best_words) > 0:
            break
        else:
            max_len_possible -= 1 # only try the top 4 letters, then 3, then 2, ...
        
        if max_len_possible == 0:
            break

    all_letters_count = 0
    for letter, freq in sorted_counts:
        all_letters_count += freq

    word_ratings = []
    for word in best_words:
        ratings_dict = {}
        for letter in word:
            for freq_letter, freq in sorted_counts:
                if letter == freq_letter:
                    ratings_dict[letter] = freq
        
        total_rating = 0
        for letter, rating in ratings_dict.items():
            total_rating += rating
        
        word_ratings.append((word, round(total_rating / all_letters_count * 100, 2)))

    word_ratings = sorted(word_ratings, key = operator.itemgetter(1), reverse = True)

    if show_letters == True:
        return word_ratings, sorted_counts
    else:
        return word_ratings
    
def count_vows_cons(word: str, y_vow = True):
    """
    Given a passed word, calculate the number of non-unique vowels and consonants in the word (duplicates counted more than once).
    
    ------
    Parameters:
    ------
    `word`: str
        a single passed word (str)
    `y_vow`: bool
        if True, "y" is considered a vowel. If False, "y" considered a consonant. Default is True

    ------
    Returns:
    ------
    `counts`: dict
        dictionary, where format is {letter type : count}
    """

    word = word.lower() # for consistency

    if y_vow == True:
        vows = "aeiouy"
        cons = "bcdfghjklmnpqrstvwxz"
    elif y_vow == False:
        vows = "aeiou"
        cons = "bcdfghjklmnpqrstvwxyz"

    counts = {}
    counts["vows"] = 0
    counts["cons"] = 0
    for letter in word:
        if letter in vows:
            counts["vows"] += 1
        if letter in cons:
            counts["cons"] += 1

    return counts

def get_word_rating(words_to_rate: list, word_list: list, normalized: bool = True, ascending: bool = False):
    """
    Given a word and a word list, calculates rating each word as a measure of its impact to the next possible guesses in Wordle, ordered according to `reverse` parameter.
    
    ------
    Parameters:
    ------
    `words_to_rate`: list
        list of strings to be rated
    `word_list`: list
        list of all possible words (str) of consistent length, to which each word in `words_to_rate` will be compared
    `normalized`: bool
        if True, normalizes all ratings on a scale of 0-100, with 100 being the rating for the most optimal word, and 0 for the least optimal word
    `ascending`: bool
        if True, returns list ordered ascending. If False, returns list in descending order

    ------
    Returns:
    ------
    `word_ratings`: list
        list of tuples. Format is [(word, rating)], where rating is calculated according to above formula
    `sorted_counts`: list of tuples
        list of tuples. Format is ("letter", frequency). Sorted according to `sort` value; ["descending" or "ascending"] if passed
    """

    if ascending == True:
        # sorted_counts = get_letter_counts(english_alphabet, word_list, sort = "ascending")
        sorted_counts = get_letter_counts(word_list = word_list, letters = english_alphabet, sort = "ascending", unique = True)
    else:
        # sorted_counts = get_letter_counts(english_alphabet, word_list, sort = "descending")
        sorted_counts = get_letter_counts(word_list = word_list, letters = english_alphabet, sort = "descending", unique = True)

    all_letters_count = 0
    for letter, freq in sorted_counts:
        all_letters_count += freq

    unnormalized_ratings = []
    for word in words_to_rate:
        word = word.lower()
        ratings_dict = {}
        for letter in word:
            for freq_letter, freq in sorted_counts:
                if letter == freq_letter:
                    ratings_dict[letter] = freq
        
        total_rating = 0
        for letter, rating in ratings_dict.items():
            total_rating += rating

        unnormalized_ratings.append((word, round(total_rating / all_letters_count * 100, 2)))
    
    word_ratings = sorted(unnormalized_ratings, key = operator.itemgetter(1), reverse = True)
    # # print (word_ratings)

    if normalized == True:
        if len(word_ratings) > 1:
            new_tests = []

            for tup in word_ratings:
                try:
                    normd = round(((tup[1] - word_ratings[-1][1]) / (word_ratings[0][1] - word_ratings[-1][1])) * 100, 2)
                    new_tests.append((tup[0], normd))
                except:
                    ZeroDivisionError
                    new_tests.append((tup[0], 0.0))    
                
            return new_tests
        else:
            return [(word_ratings[0][0], float(100))]
        
    elif normalized == False:

        return word_ratings
    
### Gets most common words of all words of the dataset

def get_word_distribution(word_list: list, sort: str = "descending"):
    """
    Given a passed str of words and a list of words, produces a frequency distribution of all words
    
    ------
    Parameters:
    ------
    `word_list`: list
        list of words (str) from which word frequencies will be counted
    `sort`: str
        if either "descending" or "ascending" are passed, returned list of tuples will be sorted accoringly, else returned dictionary will be unsorted

    ------
    Returns:
    ------
    `words_counts_dict`: dict
        dictionary of {word : count} pairs for each word in passed `word_list`
    `sorted_counts_dicts`: list of tuples
        list of tuples. Format is ("word", frequency). Ordered according to `sort` values
    """

    words_counts_dict = {}

    for word in word_list: 
        if word in words_counts_dict:
            words_counts_dict[word] += 1
        else:
            words_counts_dict[word] = 1

    if sort == "ascending":
        sorted_counts_dict = (sorted(words_counts_dict.items(), key = operator.itemgetter(1), reverse = False))
        return sorted_counts_dict

    if sort == "descending":
        sorted_counts_dict = sorted(words_counts_dict.items(), key = operator.itemgetter(1), reverse = True)
        return sorted_counts_dict

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

## lines 305 - 835

def wordle_wizard(word_list: list, max_guesses: int = None, 
                  guess: str = None, target: str = None,
                  random_guess: bool = False, random_target: bool = False, 
                  verbose: bool = False, drama: float = None, 
                  return_stats: bool = False, record: bool = False):
    """
    Mimicking the popular web game, this function matches a current word to a target word automatically, in the most statistically optimal way possible.

    Parameters:
    ------
    `word_list`: list
        list of valid words to be considered
    `guess`: str
        a string -- must be the same length as `target_word`
    `target`: str
        a string -- must be the same length as `opening_word`
    `max_guesses`: int
        the maximum number of attempts allowed to solve the Wordle
    `random_guess`: bool
        if True, randomly chooses a starting word from all words within `word_list`. If False, passed starting word must be used instead
    `random_target`: bool
        if True, randomly chooses a target word from all words within `word_list`. If False, passed target word must be used instead
    `verbose`: bool
        if True, # prints progress and explanation of how function solves the puzzle. If False, # prints only the guessed word at each guess.
    `drama`: float or int
        if int provided, each guess' output is delayed by that number of seconds, else each output is shown as quickly as possible. For ~dRaMaTiC eFfEcT~
    `return_stats`: bool
        if True, # prints nothing and returns a dictionary of various statistics about the function's performance trying to solve the puzzle
    `record`: bool
        if True, creates a .txt file with the same information # printed according to the indicated verbosity

    Returns:
    ------
    `# stats_dict`: dict
        dictionary containing various statistics about the function's performance trying to solve the puzzle
    """

    guess = guess.lower()
    target = target.lower()

    sugg_words = []

    for i in range(0, 20):
        ran_int = random.randint(0, len(word_list) - 1)
        word = word_list[ran_int]
        sugg_words.append(word)

    if guess not in word_list:
        # print ("Guess word not in passed word list.\nOnly words within the given word list are valid.")
        # print (f"Here are some examples of valid words from the passed word list.\n\t{sugg_words[:10]}")
        return None
    
    if target not in word_list:
        # print ("Target word not in passed word list.\nOnly words within the given word list are valid.")
        # print (f"Here are some examples of valid words from the passed word list.\n\t{sugg_words[-10:]}")
        return None

    if random_guess == True:
        randomint_guess = random.randint(0, len(word_list) - 1)
        guess = word_list[randomint_guess]

    if random_target == True:
        randomint_target = random.randint(0, len(word_list) - 1)
        target = word_list[randomint_target]

    # stats_dict = {}
    # stats_dict['first_guess'] = guess
    # stats_dict['target_word'] = target
    # stats_dict['first_guess_vowels'] = float(count_vows_cons(guess, y_vow = True)['vows'])
    # stats_dict['first_guess_consonants'] = float(count_vows_cons(guess, y_vow = True)['cons'])
    # stats_dict['target_vowels'] = float(count_vows_cons(target, y_vow = True)['vows'])
    # stats_dict['target_consonants'] = float(count_vows_cons(target, y_vow = True)['cons'])
    
    # # get rating of the first guess word and target word in the entire word_list
    # for tup in get_word_rating(word_list, word_list, normalized = True):
    #     if tup[0] == guess:
    #         # stats_dict['first_guess_rating'] = tup[1]
    #     if tup[0] == target:
    #         # stats_dict['target_rating'] = tup[1]

    # guess_entropies = []
    # guess_entropies.append(# stats_dict['first_guess_rating'])

    # luck_guess_1 = round(1 - ((1 / len(word_list)) * guess_entropies[0] / 100), 2) * 100

    english_alphabet = "abcdefghijklmnopqrstuvwxyz"

    # word_list_sorted_counts = get_letter_counts(english_alphabet, word_list, sort = "descending")
    word_list_sorted_counts = get_letter_counts(word_list = word_list, letters = english_alphabet, sort = "descending", unique = True)

    
    wordlen = len(guess)
    letter_positions = set(i for i in range(0, wordlen))

    guess_set = set()
    perfect_dict = {}
    wrong_pos_dict = {}
    wrong_pos_set = set()
    dont_guess_again = set()

    guessed_words = [] # running set of guessed words
    guess_num = 0 # baseline for variable
    dont_guess_words = set()
    incorrect_positions = []
    reduction_per_guess = []

    if max_guesses == None: # if no value is passed, default is len(guess)
        max_guesses = wordlen
    else: # else it is the value passed
        max_guesses = max_guesses

    perfect_letts_per_guess = []
    wrong_pos_per_guess = []
    wrong_letts_per_guess = []

    while guess: # while there is any guess -- there are conditions to break it at the bottom

        guess_num += 1

        guessed_words.append(guess)

        if drama:
            time.sleep(drama)

        # guess_num += 1 # each time the guess is processed
        if return_stats == False:
            if guess_num == 1:
                print("-----------------------------\n")

        if guess == target:
            # stats_dict['target_guessed'] = True
            if return_stats == False:
                if guess_num == 1:
                    # print(f"Congratulations! The Wordle has been solved in {guess_num} guess, that's amazingly lucky!")
                    print(f"The starting word and target word are the same. Try entering two different words to see how the puzzle can be solved.")
                    # print(f"The target word was {target}")
                
                
                    perfect_letts_per_guess.append(5)
                    wrong_pos_per_guess.append(0)
                    wrong_letts_per_guess.append(0)
            break
            
        if return_stats == False:
            print(f"**Guess {guess_num}: '{guess}'**")

        guess_set = set()
        wrong_pos_set = set()

        #### Step 2 -- ALL PERFECT
        for i in letter_positions: # number of letters in each word (current word and target word)
            guess_set.add(guess[i])

            if guess[i] not in perfect_dict:
                perfect_dict[guess[i]] = set()
            if guess[i] not in wrong_pos_dict:
                wrong_pos_dict[guess[i]] = set()

            ### EVALUATE CURRENT GUESS
            if guess[i] == target[i]: # letter == correct and position == correct
                perfect_dict[guess[i]].add(i)

            if (guess[i] != target[i] and  guess[i] in target): # letter == correct and position != correct
                wrong_pos_dict[guess[i]].add(i)
                wrong_pos_set.add(guess[i])

            if guess[i] not in target: # if letter is not relevant at all
                dont_guess_again.add(guess[i])

        #### Step 3 -- ALL PERFECT
        next_letters = set()
        for letter, positions in perfect_dict.items():
            if len(positions) > 0:
                next_letters.add(letter)

        for letter, positions in wrong_pos_dict.items():
            if len(positions) > 0:
                next_letters.add(letter)

        #### List of tuples of correct letter positions in new valid words. Eg: [('e', 2), ('a', 3)]
        perfect_letters = []
        for letter, positions in perfect_dict.items():
            for pos in positions:
                if len(positions) > 0:
                    perfect_letters.append((letter, pos))

        #### all words that have correct letters in same spots
        words_matching_correct_all = []
        for word in word_list:
            word_set = set()
            for letter, pos in perfect_letters:
                if pos < len(word):
                    if word[pos] == letter:
                        words_matching_correct_all.append(word)

        #### excluding words with letters in known incorrect positions
        for letter, positions in wrong_pos_dict.items():
            for pos in positions:
                if len(positions) > 0:
                    if (letter, pos) not in incorrect_positions:
                        incorrect_positions.append((letter, pos))

        # sorting lists of tuples just to make them look nice in the # printout
        incorrect_positions = sorted(incorrect_positions, key = operator.itemgetter(1), reverse = False)
        perfect_letters = sorted(perfect_letters, key = operator.itemgetter(1), reverse = False)

        #### all words that have correct letters in incorrect spots -- so they can be excluded efficiently
        
        # print(incorrect_positions)
        
        for word in word_list:
            word_set = set()
            for letter, pos in incorrect_positions:
                if pos < len(word):
                    if word[pos] == letter:
                        dont_guess_words.add(word)
        for word in word_list:
            word_set = set()
            for letter, pos in incorrect_positions:
                if pos < len(word):
                    if word[pos] == letter:
                        dont_guess_words.add(word)

        for bad_letter in dont_guess_again:
            for word in word_list:
                if (bad_letter in word and word not in dont_guess_words):
                    dont_guess_words.add(word)

        if return_stats == False:
            if verbose == True:
                print(f"Letters in correct positions:\n\t{perfect_letters}\n")
                print(f"Letters in incorrect positions:\n\t{incorrect_positions}\n")
                # print (f"Letters to guess again:\n\t{sorted(list(next_letters), reverse = False)}\n")
                print(f"Letters to not guess again:\n\t{sorted(list(dont_guess_again), reverse = False)}\n") # works

        # Returns True
        # print(A.issubset(B)) # "if everything in A is in B", returns Bool

        perfect_letts_per_guess.append(len(perfect_letters))
        wrong_pos_per_guess.append(len(incorrect_positions))
        wrong_letts_per_guess.append(len(dont_guess_again))

        potential_next_guesses = set()
        middle_set = set()

        if len(perfect_letters) == 0 and len(incorrect_positions) == 0: # if there are NEITHER perfect letters, NOR incorrect positions, ....
            for word in word_list:
                if word not in dont_guess_words:
                    if word not in guessed_words:
                        potential_next_guesses.add(word)
                                        
            # print(f"GUESS {guess_num} : TEST 1-1")

        if len(perfect_letters) == 0 and len(incorrect_positions) != 0: # if there are no perfect letters whatsoever, but there ARE incorrect positions ....
            for word in word_list:
                for incor_letter, incor_pos in incorrect_positions:
                    if incor_pos < len(word):
                        if word[incor_pos] != incor_letter:
                            if word not in dont_guess_words: # just in case
                                word_set = set()
                                for letter in word:
                                    word_set.add(letter)
    
                                    if next_letters.issubset(word_set):
                                        if word not in guessed_words:
                                            if len(dont_guess_again) > 0:
                                                for bad_letter in dont_guess_again:
                                                    if bad_letter not in word:
                                                        # potential_next_guesses.append(word)
                                                        potential_next_guesses.add(word)
                                            else:
                                                potential_next_guesses.add(word)
            
            # print(f"GUESS {guess_num} : TEST 2-1")

        else:
            for word in word_list:
                if word not in dont_guess_words: # just in case
                    word_set = set()
                    for letter in word:
                        word_set.add(letter)
                        if next_letters.issubset(word_set):
                            if word not in guessed_words:
                                # # print ("TEST 3-2")

                                if len(dont_guess_again) > 0:
                                    for bad_letter in dont_guess_again:
                                        if bad_letter not in word:
                                            middle_set.add(word)
                                else:
                                    middle_set.add(word)
            for word in middle_set:
                dummy_list = []
                for good_lett, good_pos in perfect_letters:
                    if word[good_pos] == good_lett:
                        dummy_list.append(1)
                        if len(dummy_list) == len(perfect_letters):
                            potential_next_guesses.add(word)
            for word in middle_set:
                dummy_list = []
                for bad_lett, bad_pos in incorrect_positions:
                    if bad_pos < len(word):
                        if word[bad_pos] == bad_lett:
                            dummy_list.append(1)
                            if len(dummy_list) > 0:
                                potential_next_guesses.remove(word)
                                        
            # print(f"GUESS {guess_num} : TEST 3-1")

        if return_stats == False:
            if verbose == True:
                if len(potential_next_guesses) > 1:
                    # print(f"At this point:")
                    print(f"\t{len(word_list) - len(potential_next_guesses)}, {round((len(word_list) - len(potential_next_guesses)) / len(word_list) * 100, 2)}% of total words have been eliminated, and")
                    print(f"\t{len(potential_next_guesses)}, {round(len(potential_next_guesses) / len(word_list) * 100, 2)}% of total words remain possible.\n")
                
                else:
                    # print(f"At this point:")
                    print(f"\t{len(word_list) - len(potential_next_guesses)}, {round((len(word_list) - len(potential_next_guesses)) / len(word_list) * 100, 2)}% of total words have been eliminated, and")
                    print(f"\t{len(potential_next_guesses)}, {round(len(potential_next_guesses) / len(word_list) * 100, 2)}% of total words remain possible.\n")
        
        reduction_per_guess.append(len(potential_next_guesses))
                
        #### Guessing next word
        if len(potential_next_guesses) == 1:

            if return_stats == False:
                if verbose == True:
                    print(f"All potential next guesses:\n\t{get_word_rating(words_to_rate = list(potential_next_guesses), word_list = word_list)}\n")
                    print(f"Words guessed so far:\n\t{guessed_words}.\n")
                
                    print(f"The only remaining possible word is:\n\t'{list(potential_next_guesses)[0]}'\n")
                
            guess = list(potential_next_guesses)[0]
            # guess_entropies.append(get_word_rating([guess], word_list, normalized = False, ascending = False)[0][1])

        else:

            best_next_guesses = list(potential_next_guesses)                
            # # print (best_next_guesses)
            word_ratings = get_word_rating(best_next_guesses, word_list, normalized = False, ascending = False) # "internal" ratings
            
            # Get max rating of all words
            max_rating = -np.inf
            for word, rating in word_ratings:
                if rating > max_rating:
                    max_rating = rating

            # add best rated words (all equally best rating in next guess list) to set
            best_of_the_best_1 = []
            for word, rating in word_ratings:
                if rating == max_rating:
                    best_of_the_best_1.append(word)

            # only using top ten most frequent prefixes suffixes to bias. After that it the impact is especially negligible
            test_starts = get_gram_freq(word_list = word_list, letters_length = 1, position = "start", search = None)[:10]
            test_ends = get_gram_freq(word_list = word_list, letters_length = 1, position = "end", search = None)[:10]

            # list of the best words that also have the most frequent starting and ending letters (suffixes and prefixes didn't have an impact)
            best_of_the_best_2 = []
            for start_gram, start_count in test_starts:
                for end_gram, end_count in test_ends:
                    for word in best_of_the_best_1:
                        if word[:1] == start_gram and word[-1:] == end_gram:
                            best_of_the_best_2.append(word)

            if len(best_of_the_best_2) > 0:
                guess = best_of_the_best_2[0]
            else:
                guess = best_of_the_best_1[0] # they're all equally the best of the best possible guesses so just pick the first
            
            # guess_entropies.append(get_word_rating([guess], word_list, normalized = False, ascending = False)[0][1])

            if return_stats == False:
                if verbose == True:
                    if len(word_ratings) <= 40:
                        print(f"All potential next guesses:\n\t{word_ratings}\n")
                        print(f"Words guessed so far:\n\t{guessed_words}.\n")
                    else:
                        print(f"The top 40 potential next guesses are:\n\t{word_ratings[:40]}\n")
                        print(f"Words guessed so far:\n\t{guessed_words}.\n")

            # guess_entropies.append(get_word_rating([guess], word_list, normalized = False, ascending = False)[0][1])

        #### Guess has now been made -- what to do next
        if guess_num == max_guesses: # if at max guesses allowed
            guessed_words.append(guess)
            # stats_dict['target_guessed'] = False
            if return_stats == False:
                if verbose == True:
                    print("-----------------------------\n")
                    print(f"Unfortunately, the Wordle could not be solved in {max_guesses} guesses.\n")
                    print(f"The target word was '{target}'.\n")
                    print("-----------------------------\n")
                else:
                    print(f"\nUnfortunately, Wordle Wizard couldn't solve the puzzle in {max_guesses} guesses. Could you?")
                    print(f"The target word was '{target}'.\n")
            break
        else: # if not at max guesses yet allowed
            # # stats_dict['target_guessed'] = False
            if return_stats == False:
                if verbose == True:
                    print(f"Next guess:\n\t'{guess}'")
                    print("\n-----------------------------\n")

        if guess == target:
            guess_num += 1
            guessed_words.append(guess)
            # stats_dict['target_guessed'] = True

            if return_stats == False:
                print(f"**Guess {guess_num}: '{guess}'**\n")
                print(f"Wordle Wizard has solved the puzzle in {guess_num} guesses!")

                if max_guesses - guess_num == 1:
                    print(f"There was only {max_guesses - guess_num} guess remaining.")
                else:
                    print(f"There were still {max_guesses - guess_num} guesses remaining.")

            if return_stats == False:   
                # # stats_dict['target_guessed'] = True                 
                print(f"\nThe target word was **'{target}'**.")
                print("\n-----------------------------")
            break

    # #### STATS STUFF    
    # mid_guesses_vows = 0
    # mid_guesses_cons = 0
    # avg_perf_letters = 0
    # avg_wrong_pos_letters = 0
    # avg_wrong_letters = 0

    # for i, word in enumerate(guessed_words):
    #     mid_guesses_vows += count_vows_cons(word, y_vow = True)['vows']
    #     mid_guesses_cons += count_vows_cons(word, y_vow = True)['cons']
        
    # for i in range(0, len(guessed_words) - 1):
    #     avg_perf_letters += perfect_letts_per_guess[i]
    #     avg_wrong_pos_letters += wrong_pos_per_guess[i]
    #     avg_wrong_letters += wrong_letts_per_guess[i]

    # # stats_dict['mid_guesses_avg_vows'] = float(round(mid_guesses_vows / len(guessed_words), 2))
    # # stats_dict['mid_guesses_avg_cons'] = float(round(mid_guesses_cons / len(guessed_words), 2))

    # # stats_dict['avg_perf_letters'] = float(round(np.mean(avg_perf_letters), 2))
    # # stats_dict['avg_wrong_pos_letters'] = float(round(np.mean(avg_wrong_pos_letters), 2))
    # # stats_dict['avg_wrong_letters'] = float(round(np.mean(avg_wrong_letters), 2))
    
    # # average number of words remaining after each guess -- the higher this is, the luckier the person got (the lower, the more guesses it took)
    # # stats_dict['avg_remaining'] = float(round(np.mean(reduction_per_guess), 2))

    # # avg rating of each guessed word relative to all other words possible at that moment -- this should consistently be 100 for the algorithm, but will be different for user
    # if len(guess_entropies) > 1: # in case of guessing it correctly on the first try
    #     sum_entropies = 0
    #     for rating in guess_entropies:
    #         sum_entropies += rating

    #     average_rating = float(round(sum_entropies / len(guess_entropies), 2))
    #     # stats_dict['avg_intermediate_guess_rating'] = average_rating
    # else:
    #     # stats_dict['avg_intermediate_guess_rating'] = float(100)

    # expected_guesses = 3.85

    # # guess_num = 3
    # # average_rating = 95
    # luck = round(1 - ((((guess_num / expected_guesses) * (# stats_dict['avg_intermediate_guess_rating'] / 100)) / max_guesses) * 5), 2)
    # # stats_dict['luck'] = luck

    # if record == True:
    #     if verbose == True:
    #         with open(f"solutions/{guessed_words[0]}_{target}_wizard_detailed.txt", "w") as fout:
            
    #                 fout.write(line + "\n") # write each line of list of # printed text to .txt file
    #     else:
    #         with open(f"solutions/{guessed_words[0]}_{target}_wizard_summary.txt", "w") as fout:
            
    #                 fout.write(line + "\n") # write

    # # if guess_num <= len(guess):
    # if guess_num <= 6:
    #     # stats_dict['valid_success'] = True
    # else:
    #     # stats_dict['valid_success'] = False

    # # stats_dict['num_guesses'] = float(guess_num)

    # # if return_stats == True:
    #     return # stats_dict

def wordle_wizard_cheat(guesses: list, word_list: list, max_guesses: int = None, 
                  target: str = None,
                  random_guess: bool = False, random_target: bool = False, 
                  verbose: bool = False, drama: float = None, 
                  return_stats: bool = False, record: bool = False):
    """
    Mimicking the popular web game, this function matches a current word to a target word automatically, in the most statistically optimal way possible.

    Parameters:
    ------
    `word_list`: list
        list of valid words to be considered
    `guess`: str
        a string -- must be the same length as `target_word`
    `target`: str
        a string -- must be the same length as `opening_word`
    `max_guesses`: int
        the maximum number of attempts allowed to solve the Wordle
    `random_guess`: bool
        if True, randomly chooses a starting word from all words within `word_list`. If False, passed starting word must be used instead
    `random_target`: bool
        if True, randomly chooses a target word from all words within `word_list`. If False, passed target word must be used instead
    `verbose`: bool
        if True, # st.writes progress and explanation of how function solves the puzzle. If False, # st.writes only the guessed word at each guess.
    `drama`: float or int
        if int provided, each guess' output is delayed by that number of seconds, else each output is shown as quickly as possible. For ~dRaMaTiC eFfEcT~
    `return_stats`: bool
        if True, # st.writes nothing and returns a dictionary of various statistics about the function's performance trying to solve the puzzle
    `record`: bool
        if True, creates a .txt file with the same information # st.writeed according to the indicated verbosity

    Returns:
    ------
    `# stats_dict`: dict
        dictionary containing various statistics about the function's performance trying to solve the puzzle
    """

    # guess = guess.lower()
    target = target.lower()

    sugg_words = []

    for i in range(0, 20):
        ran_int = random.randint(0, len(word_list) - 1)
        word = word_list[ran_int]
        sugg_words.append(word)

    guess = guesses[0]

    # stats_dict = {}
    # stats_dict['first_guess'] = guess
    # stats_dict['target_word'] = target
    # stats_dict['first_guess_vowels'] = float(count_vows_cons(guess, y_vow = True)['vows'])
    # stats_dict['first_guess_consonants'] = float(count_vows_cons(guess, y_vow = True)['cons'])
    # stats_dict['target_vowels'] = float(count_vows_cons(target, y_vow = True)['vows'])
    # stats_dict['target_consonants'] = float(count_vows_cons(target, y_vow = True)['cons'])
    
    # get rating of the first guess word and target word in the entire word_list
    # for tup in get_word_rating(word_list, word_list, normalized = True):
        # if tup[0] == guess:
            # stats_dict['first_guess_rating'] = tup[1]
        # if tup[0] == target:
            # stats_dict['target_rating'] = tup[1]

    # guess_entropies = []
    # guess_entropies.append(# stats_dict['first_guess_rating'])

    # luck_guess_1 = round(1 - ((1 / len(word_list)) * guess_entropies[0] / 100), 2) * 100

    english_alphabet = "abcdefghijklmnopqrstuvwxyz"

    # word_list_sorted_counts = get_letter_counts(english_alphabet, word_list, sort = "descending")
    word_list_sorted_counts = get_letter_counts(word_list = word_list, letters = english_alphabet, sort = "descending", unique = True)

    wordlen = len(guesses[0])
    letter_positions = set(i for i in range(0, wordlen))

    guess_set = set()
    perfect_dict = {}
    wrong_pos_dict = {}
    wrong_pos_set = set()
    dont_guess_again = set()

    guessed_words = [] # running set of guessed words
    guess_num = 0 # baseline for variable
    dont_guess_words = set()
    incorrect_positions = []
    reduction_per_guess = []

    if max_guesses == None: # if no value is passed, default is len(guess)
        max_guesses = wordlen
    else: # else it is the value passed
        max_guesses = max_guesses

    perfect_letts_per_guess = []
    wrong_pos_per_guess = []
    wrong_letts_per_guess = []

    # while guess: # while there is any guess -- there are conditions to break it at the bottom

    for guess_num, guess in enumerate(guesses):

        guess_num += 1

        guessed_words.append(guess)

        if drama:
            time.sleep(drama)

        # guess_num += 1 # each time the guess is processed
        if return_stats == False:
            if guess_num == 1:
                st.write("-----------------------------\n")

        if guess == target:
            # stats_dict['target_guessed'] = True
            if return_stats == False:
                if guess_num == 1:
                    # st.write(f"Congratulations! The Wordle has been solved in {guess_num} guess, that's amazingly lucky!")
                    st.write(f"The starting word and target word are the same. Try entering two different words to see how the puzzle can be solved.")
                    # st.write(f"The target word was {target}")
                
                
                    perfect_letts_per_guess.append(5)
                    wrong_pos_per_guess.append(0)
                    wrong_letts_per_guess.append(0)
            break
            
        if return_stats == False:
            st.write(f"**Guess {guess_num}: '{guess}'**")

        guess_set = set()
        wrong_pos_set = set()

        #### Step 2 -- ALL PERFECT
        for i in letter_positions: # number of letters in each word (current word and target word)
            guess_set.add(guess[i])

            if guess[i] not in perfect_dict:
                perfect_dict[guess[i]] = set()
            if guess[i] not in wrong_pos_dict:
                wrong_pos_dict[guess[i]] = set()

            ### EVALUATE CURRENT GUESS
            if guess[i] == target[i]: # letter == correct and position == correct
                perfect_dict[guess[i]].add(i)

            if (guess[i] != target[i] and  guess[i] in target): # letter == correct and position != correct
                wrong_pos_dict[guess[i]].add(i)
                wrong_pos_set.add(guess[i])

            if guess[i] not in target: # if letter is not relevant at all
                dont_guess_again.add(guess[i])

        #### Step 3 -- ALL PERFECT
        next_letters = set()
        for letter, positions in perfect_dict.items():
            if len(positions) > 0:
                next_letters.add(letter)

        for letter, positions in wrong_pos_dict.items():
            if len(positions) > 0:
                next_letters.add(letter)

        #### List of tuples of correct letter positions in new valid words. Eg: [('e', 2), ('a', 3)]
        perfect_letters = []
        for letter, positions in perfect_dict.items():
            for pos in positions:
                if len(positions) > 0:
                    perfect_letters.append((letter, pos))

        #### all words that have correct letters in same spots
        words_matching_correct_all = []
        for word in word_list:
            word_set = set()
            for letter, pos in perfect_letters:
                if pos < len(word):
                    if word[pos] == letter:
                        words_matching_correct_all.append(word)

        #### excluding words with letters in known incorrect positions
        for letter, positions in wrong_pos_dict.items():
            for pos in positions:
                if len(positions) > 0:
                    if (letter, pos) not in incorrect_positions:
                        incorrect_positions.append((letter, pos))

        # sorting lists of tuples just to make them look nice in the # st.writeout
        incorrect_positions = sorted(incorrect_positions, key = operator.itemgetter(1), reverse = False)
        perfect_letters = sorted(perfect_letters, key = operator.itemgetter(1), reverse = False)

        #### all words that have correct letters in incorrect spots -- so they can be excluded efficiently
        
        # st.write(incorrect_positions)
        
        for word in word_list:
            word_set = set()
            for letter, pos in incorrect_positions:
                if pos < len(word):
                    if word[pos] == letter:
                        dont_guess_words.add(word)
        for word in word_list:
            word_set = set()
            for letter, pos in incorrect_positions:
                if pos < len(word):
                    if word[pos] == letter:
                        dont_guess_words.add(word)

        for bad_letter in dont_guess_again:
            for word in word_list:
                if (bad_letter in word and word not in dont_guess_words):
                    dont_guess_words.add(word)

        if return_stats == False:
            if verbose == True:
                st.write(f"Letters in correct positions:\n\t{perfect_letters}\n")
                st.write(f"Letters in incorrect positions:\n\t{incorrect_positions}\n")
                # st.write (f"Letters to guess again:\n\t{sorted(list(next_letters), reverse = False)}\n")
                st.write(f"Letters to not guess again:\n\t{sorted(list(dont_guess_again), reverse = False)}\n") # works

        # Returns True
        # st.write(A.issubset(B)) # "if everything in A is in B", returns Bool

        perfect_letts_per_guess.append(len(perfect_letters))
        wrong_pos_per_guess.append(len(incorrect_positions))
        wrong_letts_per_guess.append(len(dont_guess_again))

        potential_next_guesses = set()
        middle_set = set()

        if len(perfect_letters) == 0 and len(incorrect_positions) == 0: # if there are NEITHER perfect letters, NOR incorrect positions, ....
            for word in word_list:
                if word not in dont_guess_words:
                    if word not in guessed_words:
                        potential_next_guesses.add(word)
                                        
            # st.write(f"GUESS {guess_num} : TEST 1-1")

        if len(perfect_letters) == 0 and len(incorrect_positions) != 0: # if there are no perfect letters whatsoever, but there ARE incorrect positions ....
            for word in word_list:
                for incor_letter, incor_pos in incorrect_positions:
                    if incor_pos < len(word):
                        if word[incor_pos] != incor_letter:
                            if word not in dont_guess_words: # just in case
                                word_set = set()
                                for letter in word:
                                    word_set.add(letter)
    
                                    if next_letters.issubset(word_set):
                                        if word not in guessed_words:
                                            if len(dont_guess_again) > 0:
                                                for bad_letter in dont_guess_again:
                                                    if bad_letter not in word:
                                                        # potential_next_guesses.append(word)
                                                        potential_next_guesses.add(word)
                                            else:
                                                potential_next_guesses.add(word)
            
            # st.write(f"GUESS {guess_num} : TEST 2-1")

        else:
            for word in word_list:
                if word not in dont_guess_words: # just in case
                    word_set = set()
                    for letter in word:
                        word_set.add(letter)
                        if next_letters.issubset(word_set):
                            if word not in guessed_words:
                                # # st.write ("TEST 3-2")

                                if len(dont_guess_again) > 0:
                                    for bad_letter in dont_guess_again:
                                        if bad_letter not in word:
                                            middle_set.add(word)
                                else:
                                    middle_set.add(word)
            for word in middle_set:
                dummy_list = []
                for good_lett, good_pos in perfect_letters:
                    if word[good_pos] == good_lett:
                        dummy_list.append(1)
                        if len(dummy_list) == len(perfect_letters):
                            potential_next_guesses.add(word)
            for word in middle_set:
                dummy_list = []
                for bad_lett, bad_pos in incorrect_positions:
                    if bad_pos < len(word):
                        if word[bad_pos] == bad_lett:
                            dummy_list.append(1)
                            if len(dummy_list) > 0:
                                potential_next_guesses.remove(word)
                                        
            # st.write(f"GUESS {guess_num} : TEST 3-1")

        if return_stats == False:
            if verbose == True:
                if len(potential_next_guesses) > 1:
                    # st.write(f"At this point:")
                    st.write(f"\t{len(word_list) - len(potential_next_guesses)}, {round((len(word_list) - len(potential_next_guesses)) / len(word_list) * 100, 2)}% of total words have been eliminated, and")
                    st.write(f"\t{len(potential_next_guesses)}, {round(len(potential_next_guesses) / len(word_list) * 100, 2)}% of total words remain possible.\n")
                
                else:
                    # st.write(f"At this point:")
                    st.write(f"\t{len(word_list) - len(potential_next_guesses)}, {round((len(word_list) - len(potential_next_guesses)) / len(word_list) * 100, 2)}% of total words have been eliminated, and")
                    st.write(f"\t{len(potential_next_guesses)}, {round(len(potential_next_guesses) / len(word_list) * 100, 2)}% of total words remain possible.\n")
        
        reduction_per_guess.append(len(potential_next_guesses))
                
        #### Guessing next word
        if len(potential_next_guesses) == 1:

            if return_stats == False:
                if verbose == True:
                    st.write(f"All potential next guesses:\n\t{get_word_rating(words_to_rate = list(potential_next_guesses), word_list = word_list)}\n")
                    st.write(f"Words guessed so far:\n\t{guessed_words}.\n")
                    st.write(f"The only remaining possible word is:\n\t'{list(potential_next_guesses)[0]}'")
                
            # guess = list(potential_next_guesses)[0]
            if guess_num < len(guesses):
                guess = guesses[guess_num]
            # guess_entropies.append(get_word_rating([guess], word_list, normalized = False, ascending = False)[0][1])

        else:

            best_next_guesses = list(potential_next_guesses)                
            # # st.write (best_next_guesses)
            word_ratings = get_word_rating(best_next_guesses, word_list, normalized = False, ascending = False) # "internal" ratings
            
            # Get max rating of all words
            max_rating = -np.inf
            for word, rating in word_ratings:
                if rating > max_rating:
                    max_rating = rating

            # add best rated words (all equally best rating in next guess list) to set
            best_of_the_best_1 = []
            for word, rating in word_ratings:
                if rating == max_rating:
                    best_of_the_best_1.append(word)

            # only using top ten most frequent prefixes suffixes to bias. After that it the impact is especially negligible
            test_starts = get_gram_freq(word_list = word_list, letters_length = 1, position = "start", search = None)[:10]
            test_ends = get_gram_freq(word_list = word_list, letters_length = 1, position = "end", search = None)[:10]

            # list of the best words that also have the most frequent starting and ending letters (suffixes and prefixes didn't have an impact)
            best_of_the_best_2 = []
            for start_gram, start_count in test_starts:
                for end_gram, end_count in test_ends:
                    for word in best_of_the_best_1:
                        if word[:1] == start_gram and word[-1:] == end_gram:
                            best_of_the_best_2.append(word)

            # if len(best_of_the_best_2) > 0:
            #     guess = best_of_the_best_2[0]
            # else:
            #     guess = best_of_the_best_1[0] # they're all equally the best of the best possible guesses so just pick the first

            if guess_num < len(guesses):
                guess = guesses[guess_num]
            
            # guess_entropies.append(get_word_rating([guess], word_list, normalized = False, ascending = False)[0][1])

            if return_stats == False:
                if verbose == True:
                    if len(word_ratings) <= 40:
                        st.write(f"All potential next guesses:\n\t{word_ratings}\n")
                        st.write(f"Words guessed so far:\n\t{guessed_words}.\n")
                    else:
                        st.write(f"The top 40 potential next guesses are:\n\t{word_ratings[:40]}\n")
                        st.write(f"Words guessed so far:\n\t{guessed_words}.\n")

            # guess_entropies.append(get_word_rating([guess], word_list, normalized = False, ascending = False)[0][1])

        #### Guess has now been made -- what to do next
        if guess_num == max_guesses: # if at max guesses allowed
            guessed_words.append(guess)
            # stats_dict['target_guessed'] = False
            if return_stats == False:
                if verbose == True:
                    st.write("-----------------------------\n")
                    st.write(f"\nUnfortunately, the puzzle was not solved in {max_guesses} guesses. Better luck next time!")
                    st.write(f"The target word was '{target}'.\n")
                    st.write("-----------------------------\n")
                else:
                    st.write(f"\nUnfortunately, the puzzle was not solved in {max_guesses} guesses. Better luck next time!")
                    st.write(f"The target word was '{target}'.\n")
            break
        else: # if not at max guesses yet allowed
            # # stats_dict['target_guessed'] = False
            if return_stats == False:
                if verbose == True:
                    if len(potential_next_guesses) > 1:
                        st.write(f"Recommended next guess:\n\t'{word_ratings[0][0]}'")
                        
                        # st.write(f"Next guess:\n\t'{guess}'")
                    st.write("\n-----------------------------\n")

        if guess == target:
            guess_num += 1
            guessed_words.append(guess)
            # stats_dict['target_guessed'] = True

            if return_stats == False:
                st.write(f"**Guess {guess_num}: '{guess}'**\n")
                st.write(f"You solved the puzzle in {guess_num} guesses!")

                if max_guesses - guess_num == 1:
                    st.write(f"There was only {max_guesses - guess_num} guess remaining.")
                else:
                    st.write(f"There were still {max_guesses - guess_num} guesses remaining.")

            if return_stats == False:   
                # # stats_dict['target_guessed'] = True                 
                st.write(f"\nThe target word was **'{target}'**.")
                st.write("\n-----------------------------")
            break

    # #### STATS STUFF    
    # mid_guesses_vows = 0
    # mid_guesses_cons = 0
    # avg_perf_letters = 0
    # avg_wrong_pos_letters = 0
    # avg_wrong_letters = 0

    # for i, word in enumerate(guessed_words):
    #     mid_guesses_vows += count_vows_cons(word, y_vow = True)['vows']
    #     mid_guesses_cons += count_vows_cons(word, y_vow = True)['cons']
        
    # for i in range(0, len(guessed_words) - 1):
    #     avg_perf_letters += perfect_letts_per_guess[i]
    #     avg_wrong_pos_letters += wrong_pos_per_guess[i]
    #     avg_wrong_letters += wrong_letts_per_guess[i]

    # # stats_dict['mid_guesses_avg_vows'] = float(round(mid_guesses_vows / len(guessed_words), 2))
    # # stats_dict['mid_guesses_avg_cons'] = float(round(mid_guesses_cons / len(guessed_words), 2))

    # # stats_dict['avg_perf_letters'] = float(round(np.mean(avg_perf_letters), 2))
    # # stats_dict['avg_wrong_pos_letters'] = float(round(np.mean(avg_wrong_pos_letters), 2))
    # # stats_dict['avg_wrong_letters'] = float(round(np.mean(avg_wrong_letters), 2))
    
    # # average number of words remaining after each guess -- the higher this is, the luckier the person got (the lower, the more guesses it took)
    # # stats_dict['avg_remaining'] = float(round(np.mean(reduction_per_guess), 2))

    # # avg rating of each guessed word relative to all other words possible at that moment -- this should consistently be 100 for the algorithm, but will be different for user
    # if len(guess_entropies) > 1: # in case of guessing it correctly on the first try
    #     sum_entropies = 0
    #     for rating in guess_entropies:
    #         sum_entropies += rating

    #     average_rating = float(round(sum_entropies / len(guess_entropies), 2))
    #     # stats_dict['avg_intermediate_guess_rating'] = average_rating
    # else:
    #     # stats_dict['avg_intermediate_guess_rating'] = float(100)

    # expected_guesses = 3.85

    # # guess_num = 3
    # # average_rating = 95
    # luck = round(1 - ((((guess_num / expected_guesses) * (# stats_dict['avg_intermediate_guess_rating'] / 100)) / max_guesses) * 5), 2)
    # # stats_dict['luck'] = luck

    # if record == True:
    #     if verbose == True:
    #         with open(f"solutions/{guessed_words[0]}_{target}_wizard_detailed.txt", "w") as fout:
            
    #                 fout.write(line + "\n") # write each line of list of # st.writeed text to .txt file
    #     else:
    #         with open(f"solutions/{guessed_words[0]}_{target}_wizard_summary.txt", "w") as fout:
            
    #                 fout.write(line + "\n") # write

    # if guess_num <= 6:
    #     # stats_dict['valid_success'] = True
    # else:
    #     # stats_dict['valid_success'] = False

    # stats_dict['num_guesses'] = float(guess_num)
    
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
    
def get_gram_freq(word_list: list, letters_length: int = 2, position: bool = "start", search: any = None):
    """
    Given a word list, a selected number of letter, a selected word position to start from ("start" or "end"),
    and an optional gram to search within the list, this function will get a frequency distribution of all n-grams
    from the passed word list and returned a frequency distribution in descending order.

    Parameters:
    ------
    `word_list`: list
        list of words of the same 
    `letters_length`: int
        number of letters in succession. Size/length of "gram". Must be between 1 and length of words in word list
    `position`: bool
        Whether to start the gram from the start of the word (like a prefix) or the end of the word (like a suffix)
    `search`: str
        If != None, string of characters to search for within the generated list. If string not found in list, function will # print an error message.

    Returns:
    ------
    `tup`: tuple
        If search != None, will return a tuple with the passed search criteria, and its count
    `sorted_gram_list`: list
        List of tuples in the form of (gram, count) for each combination of the gram size in the pass word_list
    """

    gram_freq_dist = {}

    for word in word_list:
        if position == "start":
            gram = word[:letters_length] # first 2 letters
        if position == "end":
            gram = word[-(letters_length):] # first 2 letters

        if gram not in gram_freq_dist:
            gram_freq_dist[gram] = 1
        else:
            gram_freq_dist[gram] += 1

    sorted_gram_dist = sorted(gram_freq_dist.items(), key = operator.itemgetter(1), reverse = True)

    if search:
        nos = []
        for tup in sorted_gram_dist:
            if tup[0] == search:
                return tup
            else:
                nos.append("not here")
        
        if len(nos) == len(sorted_gram_dist):
            print ("Search criteria not found in list. Please enter a gram from within the list.")
    else:
        return sorted_gram_dist