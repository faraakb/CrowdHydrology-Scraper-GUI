import os
import requests
import shutil
import re
import store_tokens
from twilio.rest import Client
from PIL import ImageTk, Image

ACCOUNT_SID= store_tokens.get_auth()
AUTH_TOKEN = store_tokens.get_tok()

client = Client(ACCOUNT_SID, AUTH_TOKEN)
people_folder = "has_people"
media_dir = 'messages_with_media'
if not os.path.exists(media_dir):
    os.makedirs(media_dir)
if not os.path.exists(people_folder):
    os.makedirs(people_folder)
list_of_folders = []
list_of_folders.append(media_dir)
cache_of_imagepaths = []

def fetch_all_messages_with_media(client, c): #read c # of pages from twilio database, messages with media (images) are stored for later use
    all_messages_with_media = []
    page = client.messages.page() #date changed from _created to _sent
    count = 0
    while page.next_page() and count!=c:
        for message in page:
            media_list = client.messages(message.sid).media.list()
            file_label = format_label(message)
            if media_list != []:
                message_data = {
                    'media': [],
                    'body' : message.body.replace("\r\n", " ")
                }
                for media in media_list:
                    media_url = f"https://api.twilio.com{media.uri.replace('.json', '')}"
                    media_filename = f"{file_label}.{media.content_type.split('/')[-1]}"
                    media_data = {
                        'url': media_url,
                        'filename': media_filename
                    }
                    message_data['media'].append(media_data)
                all_messages_with_media.append(message_data)
        page = page.next_page() if page.next_page() else None
        count+=1
        print(str(count) + '/' + f"{c}")
    return all_messages_with_media
def format_label(message): #format timestamp for each message, ex: "2024-12-16 13:27:27 EST" --> "2024-12-16 at 1:27:27 PM"
    t = str(message.date_sent).replace("+00:00", "").split()
    t_copy = str(message.date_sent).replace("+00:00", "").split()
    mdy = t[0]
    t_copy.remove(mdy)
    sep = t_copy[0].split(":")
    wrong_hour_maybe = int(sep[0])
    reg_time = ""
    if wrong_hour_maybe > 12:
        correct_hour = wrong_hour_maybe-4
        reg_time = str(t_copy[0].replace(str(wrong_hour_maybe), str(correct_hour)))
    else:
        reg_time = t_copy[0]
    file_label = mdy + " at " + military_to_regular(reg_time).replace(":", "-")
    return file_label
def military_to_regular(military_time): #convert from military time to regular, ex: "13:27:27" --> "127:27 PM"
    hours, minutes, seconds = map(int, military_time.split(':'))

    period = 'AM' if hours < 12 else 'PM'

    regular_hours = hours % 12
    if regular_hours == 0:
        regular_hours = 12

    fin_mins = "0" + str(minutes) if (minutes - 10) < 0 else str(minutes)
    regular_time = str(regular_hours) + ":" + fin_mins + ":" + str(seconds) + " " + period
    return regular_time
def download_media_files(messages_with_media, media_dir): #store each image to its respective folder if possible, otherwise stored in general folder
    for message in messages_with_media:
        if message['body'] != "":
            media_dir2 = sanitize_dirname(message['body'])
            if not is_valid_filename_or_dirname(media_dir2):
                continue
            if not os.path.exists(media_dir2):
                os.makedirs(media_dir2)
            if media_dir2 not in list_of_folders:
                list_of_folders.append(media_dir2)
            download_and_write(message, media_dir2)
        else:
            download_and_write(message, media_dir)
def download_and_write(message, media_dir): #write contents of respective image to its provided media_dir
    for media in message['media']:
        media_url = media['url']
        media_filename = os.path.join(media_dir, media['filename'])
        cache_of_imagepaths.append(media_filename)
        media_response = requests.get(media_url, auth=(ACCOUNT_SID, AUTH_TOKEN))
        with open(media_filename, 'wb') as media_file:
            media_file.write(media_response.content)
        print(f"Downloaded {media_filename}")

def sanitize_dirname(dirname, replacement='_'): #implementation taken off internet to validate file/dir names
    if os.name == 'nt':  # Windows
        # Windows invalid characters
        invalid_chars = r'<>:"/\\|?*'
        # Windows reserved names
        reserved_names = [
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        ]

        # Replace invalid characters with the replacement character
        dirname = re.sub(r'[<>:"/\\|?*]', replacement, dirname)

        # Remove leading and trailing dots and spaces
        dirname = dirname.strip('. ')

        # Check if dirname is a reserved name and append an underscore if it is
        if dirname.upper() in reserved_names:
            dirname += replacement
    else:  # Unix-like
        # Unix-like invalid character
        invalid_chars = '/'
        # Replace invalid characters with the replacement character
        dirname = dirname.replace('/', replacement)

    # Common restrictions
    if len(dirname) == 0 or dirname in ['.', '..']:
        dirname = 'default_dir'

    return dirname
def is_valid_filename_or_dirname(name): #implementation taken off internet to validate file/dir names
    # Check for empty or whitespace-only names
    if not name or name.isspace():
        return False

    # Length check (assuming 255 character limit for filenames)
    if len(name) > 255:
        return False

    # Define prohibited characters based on platform
    prohibited_chars = r'[<>:"/\\|?*\x00-\x1f]'
    reserved_names = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10))
    }
    # Check if name is a reserved name
    if name.upper() in reserved_names:
        return False

    # Check for prohibited characters
    if re.search(prohibited_chars, name):
        return False

    # Check for trailing spaces or dots (issue on Windows)
    if name[-1] in {" ", "."}:
        return False

    # If all checks are passed
    return True

def main():
    messages_with_media = fetch_all_messages_with_media(client, 10) #currently reading 10 pages off database
    download_media_files(messages_with_media, media_dir)
main()
