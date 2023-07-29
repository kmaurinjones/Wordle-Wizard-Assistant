import streamlit as st
from streamlit_extras.stateful_button import button # for button that can maintain its clicked state
import random # for showing random words
from wordle_assistant_functions import * # for wordle solving
import plotly.express as px # for plots
from plots import * # for plots
from bs4 import BeautifulSoup
import requests


### Page header
st.title("Wordle Wizard 🧙")

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

mode = st.selectbox('Select Mode', ('Universal Solver', 'Daily Puzzle Assistant'))

if mode == 'Universal Solver':
    st.write("""
    Universal Solver: Enter any two words - a word to start the puzzle with (the first "guess"), 
    and a target word for Wordle Wizard to find, and it'll solve the puzzle in the most statistically optimal way possible! 
    You can see how your solution of a puzzle stacks up against an AI.
    """)
    
elif mode == 'Daily Puzzle Assistant':
    st.write("""
    Daily Puzzle Assistant: If you haven't solved today's puzzle yet, and would like a little nudge in the right direction, 
    you can submit all the words you've currently guessed and this solver will give you the most statistically optimal next guess, 
    that perfectly complements the words you've already tried. Like a little robot assistant!
    """)

# then you can use the 'mode' variable to determine which block of code to run
if mode == 'Universal Solver':
    # Code for Universal Solver

    st.title("Wordle Wizard Universal Solver 🧙🚑")

    # if mode 1 is chosen, do the following

    ### for guess length validation of both guesses
    valid_guesses = True
        
    ### Generate Examples Button
    st.write('Please enter a starting word and a target word, and click the "Abracadabra" button to have the puzzle solved.\n')
    st.write('If you would like some examples of words you can use, click the button below.\n')

    if st.button('Show Me Words', key = "button1"):
        st.write(f"There are {len(official_words)} in the official Wordle word list. Here are {len(sugg_words)} of them.")
        st.write(f"{sugg_words}\n")

    # user starting word
    starting_word = st.sidebar.text_input("Enter starting word here")
    starting_word = starting_word.strip().replace(" ", "").lower()
    if len(starting_word) != 5:
        valid_guesses = False
        st.write('Please double check and make sure there are exactly 5 letters in the starting word.\n')

    # user target word
    target_word = st.sidebar.text_input("Enter target word here")
    target_word = target_word.strip().replace(" ", "").lower()
    if len(target_word) != 5:
        valid_guesses = False
        st.write('Please double check and make sure there are exactly 5 letters in the target word.\n')

    ### Solving
    # solve_button = st.button('Abracadabra')
    if button('Abracadabra', key = "button2_universal"): # button to make everything run
        if valid_guesses == True: # ensure words are the correct lengths
            
            # if (starting_word.isalpha() and target_word.isalpha()): # checking there's no punctuation
            if not (starting_word.isalpha() and target_word.isalpha()): # if the passed words don't check every criterion
                st.write("Please check again that the starting word and target word only contain letter and are both 5 letters in length. Once they are, click the 'Abracadabra' button once more.")
            
            else: # if all is right in the wordle wizard world
                # if either of them isn't in the list, temporarily add them to the list. This doesn't impact things much and will save a ton of error headaches
                if starting_word not in official_words:
                    official_words.append(starting_word)
                if target_word not in official_words:
                    official_words.append(target_word)

                # puzzle solution
                wordle_wizard(word_list = official_words, max_guesses = 6, guess = starting_word, target = target_word, random_guess = False, random_target = False, verbose = True, drama = 0, return_stats = False, record = False)


# if mode 2 is chosen, do the following - default to this mode

### for getting daily target wor

elif mode == 'Daily Puzzle Assistant':
    # Code for Daily Puzzle Assistant

    st.title("Wordle Wizard Daily Puzzle Assistant 🧙🚑")

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

    #### USER PROVIDING GUESSES ####
    num_guesses = st.sidebar.selectbox(
        'How many guesses would you like to submit?',
        (1, 2, 3, 4, 5))

    guesses = []
    for i in range(num_guesses):
        input_guess = st.text_input(f"Guess #{i+1}", '')
        guesses.append(input_guess.strip().lower())
        st.write(f"Guess #{i+1}: {input_guess}")

    #### CHECKING THAT ALL GUESSES ARE VALID
    def is_alphanumeric_and_of_length_5(guess):
        stripped_guess = guess.strip()
        return stripped_guess.isalpha() and len(stripped_guess) == 5 # no punctuation, no numbers, 5 letters in length

    # guesses = ["guess1", "guess 2", "guess3 ", " guess4", "guess5"]
    valid_guesses = all(is_alphanumeric_and_of_length_5(guess) for guess in guesses)

    ### Solving
    # solve_button = st.button('Abracadabra')
    if button('Abracadabra', key = "button2_assistant"): # button to make everything run
        
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
            
# if button('Abracadabra', key = "button2_universal"): # button to make everything run
if button('Abracadabra'):

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