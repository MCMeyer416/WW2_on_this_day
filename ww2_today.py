import datetime
import os

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
# Reads Telegram secrets (kept out of the code so they never reach GitHub)
load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

# Get today's date and format it for the API request
today = datetime.date.today()
day = today.day
month = today.month

# Wikipedia's "On this day" API for today's date (month and day padded to 2 digits)
wiki_url = f'https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/events/{month:02d}/{day:02d}'
# Telegram bot API URL for sending messages (the token identifies the bot)
telegram_url = f'https://api.telegram.org/bot{token}/sendMessage'

# Wikipedia requires a user-agent that identifies the script and gives a contact URL
headers = {'user-agent': 'WW2-OnThisDay/0.1 (https://github.com/MCMeyer416)'}
response = requests.get(wiki_url, headers=headers, timeout=10)
response.raise_for_status()  # Raise an error if the request failed (e.g., 404 or 500)

# Convert JSON response to a Python dictionary and extract the list of events
data = response.json()
events = data['events']


# An event counts as WW2, if it happened between 1939 and 1945 and mentions "World War II"
# Year check alone is not enough, because some events in that range are not related to the war.
ww2_events = []
for event in events:
    year = event.get('year', 0)    # .get() avoids a crash if a key is missing
    text = event.get('text', '')
    if 1939 <= year <= 1945 and 'World War II' in text:
        text = text.removeprefix('World War II:').strip()   # Removes the redundant "World War II:" label and any leftover spaces
        ww2_events.append((year, text))


title = f"WW2 events on this day: {today.strftime('%B %d')}\n"

#Sort the oldest to newest by year only
by_year = sorted(ww2_events, key=lambda x: x[0])
if not by_year:
    lines = ["No WW2 events found for today."]
else:
    lines = [title]
    for year, text in by_year:
        lines.append(f'{year}: {text}')


message = '\n'.join(lines)

#Send a message to the Telegram bot with the WW2 events
payload = {'chat_id': chat_id, 'text': message}
telegram_response = requests.post(telegram_url, data=payload, timeout=10)
telegram_response.raise_for_status()  # Raise an error if the request failed (e.g., 404 or 500)