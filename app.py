import streamlit as st
from streamlit_extras.stateful_button import button # for button that can maintain its clicked state
import random # for showing random words
from wordle_assistant_functions import * # for wordle solving
import plotly.express as px # for plots
from plots import * # for plots
import requests

### for getting daily target word
from bs4 import BeautifulSoup

url = "https://www.tomsguide.com/news/what-is-todays-wordle-answer"

response = requests.get(url)

if response.status_code != 200:
    raise ConnectionError ("There was an error loading the solutions webpage.\nReload this page and try again, and if this issue persists, please contact me at kmaurinjones@gmail.com")

soup = BeautifulSoup(response.content, "html.parser")

paras = soup.find_all("p")
for para in paras:
    text = para.text
    bolds = [word.replace(".", "").strip() for word in text.split() if word.replace(".", "").strip().isupper()]
    if len(bolds) == 1 and len(bolds[0]) == 5:
        target_word = bolds[0]
        print(target_word)
        break

### Page header
st.title("Wordle Wizard Assistant 🧙🚑")

### Loading in official word list
official_words = []
with open("data/official_words_processed.txt", "r", encoding = "utf-8") as f:
    for word in f.read().split("\n"):
        if len(word) == 5:
            official_words.append(word)
f.close() # closes connection to file

### Examples of words to use
sugg_words = []
for i in range(0, 20):
    ran_int = random.randint(0, len(official_words) - 1)
    word = official_words[ran_int]
    sugg_words.append(word)

#### USER PROVIDING GUESSES ####
num_guesses = st.sidebar.selectbox(
    'How many guesses would you like to submit?',
    (1, 2, 3, 4, 5))

guesses = []
for i in range(num_guesses):
    input_guess = st.text_input(f"Guess #{i+1}", '')
    guesses.append(input_guess)
    st.write(f"Guess #1: {input_guess}")

#### CHECKING THAT ALL GUESSES ARE VALID
def is_alphanumeric_and_of_length_5(guess):
    stripped_guess = guess.strip()
    return stripped_guess.isalpha() and len(stripped_guess) == 5 # no punctuation, no numbers, 5 letters in length

# guesses = ["guess1", "guess 2", "guess3 ", " guess4", "guess5"]
valid_guesses = all(is_alphanumeric_and_of_length_5(guess) for guess in guesses)

### Solving
# solve_button = st.button('Abracadabra')
if button('Abracadabra', key = "button2"): # button to make everything run
    
    #### CHECKING ALL GUESSES ARE LEGAL
    if not valid_guesses:
        st.write("Please check again that each guess only contains letters and is 5 letters in length. Once you have, click 'Abracadabra' to get feedback.")

    else: # if everything is legal, proceed to solving

        #### ADDING UNSEEN WORDS TO OFFICIAL LIST (THIS SHOULD MINIMIZE OVERALL ERRORS)
        for word in guesses:
            if word not in guesses:
                official_words.append(word)

        #### RUN ALGORITHM
        wordle_wizard_cheat(guesses = guesses, word_list = official_words, max_guesses = 6, 
                        target = target_word,
                        random_guess = False, random_target = False, 
                        verbose = True, drama = 0, return_stats = False, record = False)

        # post-solution prompt
        st.write("Curious about what the number beside each word means? Click the button below to find out!")

        # show plot and info
        if button(label = "More info", key = "button3"):
            
            # show plot of letters distribution
            count_plot()

            st.write("This is a distribution of the frequencies of all letters in the Wordle word list used in this app. The higher a given letter's count is, the more likely it is that that letter will be able to tell us something about the target word in a Wordle puzzle.\n")
            st.write("The rating of each word corresponds to approximately the percentage of all words of the ~2300 words of the list used for this game in which the given word's letters appear. This means that, for a word with a rating of 30, its letters show up in 30\% of the words of the entire word list. Since we cannot possibly have all 26 letters of the English alphabet in one 5-letter word, this rating can only really be used to compare one word to another. Using more highly-rated words should generally result in getting to the target word in fewer guesses than using lower-rated words.\n")

            # show plot of best and worst words
            words_plot()

            st.write("By this same rating system, here are the top 5 words, the middle 5 words, and the worst 5 words of the entire Wordle word list in terms of their respective ratings.\n\n")
            st.write("If you're interested in learning more about the theory of how Wordle Wizard actually works, check out this blog post (https://medium.com/@kmaurinjones/how-i-beat-wordle-once-and-for-all-322c8641a70d), that describes everything mentioned here (and more!) in greater detail.\n")

            st.write("-----------------------------\n")

st.write("\nThanks for checking out Wordle Wizard! If you have any feedback or requests for additions to this app, shoot me an email at kmaurinjones@gmail.com.")