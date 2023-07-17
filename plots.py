from wordle_functions import *
import pandas as pd
import streamlit as st
import plotly.express as px
import operator

### Official wordlist
official_words = []
with open("data/official_words_processed.txt", "r", encoding = "utf-8") as f:
    for word in f.read().split("\n"):
        if word.isalpha():
            official_words.append(word)
f.close() # closes connection to file

english_alphabet = "abcdefghijklmnopqrstuvwxyz"

def count_plot():
    letter_counts = get_letter_counts(word_list = official_words, letters = english_alphabet, sort = "descending", unique = True)
    letter_counts_dict = {} # {letter : count}
    letter_counts_dict["Letter"] = []
    letter_counts_dict["Count"] = []
    letter_counts_dict["Type"] = []
    for tup in letter_counts:
        letter_counts_dict["Letter"].append(tup[0].upper())
        letter_counts_dict["Count"].append(tup[1])

        if tup[0] in "aeiouy":
            letter_counts_dict["Type"].append("Vowel")
        else:
            letter_counts_dict["Type"].append("Consonant")

    letters_dist_df = pd.DataFrame(letter_counts_dict)

    counts_plot = px.bar(letters_dist_df, x = "Letter", y = "Count", title = "Distribution of Letters in Official Wordle List",
                        color = "Type", color_discrete_map = {"Vowel": "#6ca965", "Consonant": "#c8b653"})
    counts_plot.update_layout(xaxis = {'categoryorder' : 'total descending'}, title_font_size = 25, font = dict(size = 17))

    # counts_plot.show()
    st.plotly_chart(counts_plot, use_container_width = True)

def words_plot():
    letter_counts = get_letter_counts(word_list = official_words, letters = english_alphabet, sort = "descending", unique = True)
    total_letters_sum = sum(count for letter, count in letter_counts) 

    word_counts = []

    for word in official_words:
        
        # get set of all letters in the word (this intentionally doesn't count duplicate letters)
        word_letters = set()
        for letter in word:
            word_letters.add(letter)
        
        # get the sum of all counts of each letter in the word
        word_sum = 0
        for letter in word_letters:
            word_sum += dict(letter_counts)[letter]

        # finally, add the word and its letter count sum to the list    
        word_counts.append((word, round(word_sum / total_letters_sum * 100, 2)))
    # word_counts
    ### Best and worst x words
    words_counts_top_10 = sorted(word_counts, key = operator.itemgetter(1), reverse = True)[:5] # top 10 words
    words_counts_middle_10 = sorted(word_counts, key = operator.itemgetter(1), reverse = True)[(len(word_counts) // 2) - 10 : (len(word_counts) // 2) - 5] # top 10 words
    words_counts_bottom_10 = sorted(word_counts, key = operator.itemgetter(1), reverse = False)[:6] # bottom 10 words
    words_counts_x_dict = {}
    words_counts_x_dict["Word"] = []
    words_counts_x_dict["Rating"] = []

    for word, rating in words_counts_top_10:
        words_counts_x_dict["Word"].append(word)
        words_counts_x_dict["Rating"].append(rating)
    for word, rating in words_counts_middle_10:
        words_counts_x_dict["Word"].append(word)
        words_counts_x_dict["Rating"].append(rating)
    for word, rating in words_counts_bottom_10:
        words_counts_x_dict["Word"].append(word)
        words_counts_x_dict["Rating"].append(rating)

    words_counts_x_df = pd.DataFrame(words_counts_x_dict)
    words_counts_x_plot = px.bar(words_counts_x_df, x = "Word", y = "Rating", title = "A Selection of Wordle Words and Their Ratings")
    words_counts_x_plot.update_layout(xaxis = {'categoryorder' : 'total descending'}, title_font_size = 25, font = dict(size = 17))
    words_counts_x_plot.update_traces(marker_color = "#6ca965")

    # words_counts_x_plot.show()
    st.plotly_chart(words_counts_x_plot, use_container_width = True)