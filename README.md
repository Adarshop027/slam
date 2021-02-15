![Slam](https://telegra.ph/file/db03910496f06094f1f7a.jpg)

# Slam Mirror Bot
This is a telegram bot writen in python for mirroring files on the internet to our beloved Google Drive.

Fork of [python-aria-mirror-bot](https://github.com/lzzy12/python-aria-mirror-bot/)

Original Source [Ayanamileechbot](https://gitlab.com/Dank-del/ayanamileechbot/)

Some features from [magneto-python-aria](https://github.com/magneto261290/magneto-python-aria/)

## Getting Google OAuth API credential file

- Visit the [Google Cloud Console](https://console.developers.google.com/apis/credentials)
- Go to the OAuth Consent tab, fill it, and save.
- Go to the Credentials tab and click Create Credentials -> OAuth Client ID
- Choose Desktop and Create.
- Use the download button to download your credentials.
- Clone this repo:
```
git clone https://github.com/breakdowns/slam-mirrorbot mirrorbot/
cd mirrorbot
```
- Move that file to the root of mirrorbot, and rename it to credentials.json
- Visit [Google API page](https://console.developers.google.com/apis/library)
- Search for Drive and enable it if it is disabled
- Finally, run the script to generate token file (token.pickle) for Google Drive:
```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
python3 generate_drive_token.py
```

## Deploying on Heroku

<p><a href="https://heroku.com/deploy?template=https://github.com/breakdowns/slam-mirrorbot"> <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku" /></a></p>
