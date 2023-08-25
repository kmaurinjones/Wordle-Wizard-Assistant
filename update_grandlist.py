import requests
import git
from bs4 import BeautifulSoup
from tqdm import tqdm

### Scraping full list of Worlde words

print("\nUpdating Wordle list to include any new words...")

# scraping exhaustive list of all Wordle solutions/targets
url = "https://www.rockpapershotgun.com/wordle-past-answers"
response = requests.get(url)
if response.status_code != 200:
    raise ConnectionError ("There was an error loading the solutions webpage.")
soup = BeautifulSoup(response.content, "html.parser")

# get list of all words on the page
all_targets = []
words_table = soup.find_all('ul', attrs = {'class' : "inline"}) # it's only one element so all words are in one str
all_words = [word.text.strip().lower() for word in words_table if word.text][0].split("\n")

word_list_path = "/Users/kmaurinjones/Desktop/ds/github_repos/Wordle-Wizard-Assistant/data/official_words_processed.txt"

# get current list
official_list = [word.strip() for word in open(word_list_path, "r").readlines()]

# combine current list and any new additions
official_list = list(set(official_list).union(set(all_words)))

### Update full list with any new changes

# write new list (with updates, if any) to same file
with open(word_list_path, "w") as f:
    for word in tqdm(official_list, desc = "Writing updated list to file"):
        f.write(word + "\n")
    f.close()

print("List updates successful!\n")

### Pushing to Github

def git_add_commit_push(repo_path, commit_message, remote_name = 'origin', branch = 'master'):
    """
    Add, commit, and push using GitPython.

    Parameters:
    - repo_path: Path to the git repository.
    - commit_message: Commit message.
    - remote_name: The name of the remote (default is 'origin').
    - branch: The branch to push to (default is 'master').
    """

    repo = git.Repo(repo_path)
    
    # Add all changes
    repo.git.add(A=True)

    # Commit
    repo.git.commit(m=commit_message)

    # Push
    origin = repo.remote(name=remote_name)
    origin.push(branch)

    print(f"Word list updated: '{commit_message}'")

local_repo_path = "/Users/kmaurinjones/Desktop/ds/github_repos/Wordle-Wizard-Assistant/"

### Current Date + Time Webpage + Commit Messages
from datetime import datetime

def get_current_time_and_date():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    return current_date, current_time

date, time = get_current_time_and_date()
# print(f"Last updated: {date} at {time}")

logs_path = "/Users/kmaurinjones/Desktop/ds/github_repos/Wordle-Wizard-Assistant/logs.txt"

current_logs = [line.strip() for line in open(logs_path, "r").readlines()]
current_logs.append(f"Word list last updated: {date}, {time}")

with open(logs_path, "w") as logs_file:
    for line in current_logs:
        logs_file.write(line + "\n")

### commit changes to repo
git_add_commit_push(repo_path = local_repo_path, commit_message = f'Word list updated: {date}, {time}')

# pushing changes to github
print("Changes pushed to Github.\n")