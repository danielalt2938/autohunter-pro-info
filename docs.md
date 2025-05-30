# THIS IS THE MOST UDPATED ONE: https://docs.google.com/document/d/18K7utf2pE9l8do_O4zHsy3kUIlBfPNw5CWucEaTOCPY/edit?usp=sharing

first login to facehook yourself
Then run all the windows script
Use the ‘windows’ branch

Create a windows vm instance (with windows OS)
Install firefox, chrome, git, nodejs, vscode & python on it
Login to facebook on firefox with our facebook account (so i guess the profile login credentials on input.csv doesn’t really matter)
Clone the github repo & switch to the windows branch (because it has all the windows script + the windows geckodriver installed)
Install all the packages for the scrapper
Then run the profiles function (use a different proxy)

# Create a virtual environment

python -m venv venv

# Activate it

venv\Scripts\activate

# Install the packages

pip install -r requirements.txt

# not available on requirements.txt

pip install pyautogui seleniumbase lxml

Note: if seleniumbase isn’t installed, see the commands at the end of the error, run it

# install geckodriver.exe if needed

Then run

python .\profile_manager.py

python .\main_gd.py (when its running, it’ll open up a new firefox window…it won’t probably be logged in, so manually login on that specific window it had opened. Might ask for recaptcha. Open a new tab asap when that window opens, so that tab that you created keeps the window open)

Change Country:
https://www.facebook.com/help/359687759689246/

After logging in to the account, go directly here to change the account: https://www.facebook.com/settings/?tab=language_and_region
