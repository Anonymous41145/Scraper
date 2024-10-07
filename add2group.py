#!/bin/env python3
# Modified by @Anonymous41145
# Telegram Group: http://t.me/linux_repo
# Please give me credits if you use any codes from here.

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import configparser
import os
import sys
import csv
import traceback
import time
import random

re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"

def banner():
    print(f"""
{re}╔╦╗{cy}┌─┐┬  ┌─┐{re}╔═╗  ╔═╗{cy}┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
{re} ║ {cy}├┤ │  ├┤ {re}║ ╦  ╚═╗{cy}│  ├┬┘├─┤├─┘├┤ ├┬┘
{re} ╩ {cy}└─┘┴─┘└─┘{re}╚═╝  ╚═╝{cy}└─┘┴└─┴ ┴┴  └─┘┴└─

            Version: 1.3
     Modified by @AbirHasan2005
        """)

# Read configuration
cpass = configparser.RawConfigParser()
if not os.path.exists('config.data'):
    print(f"{re}[!] Configuration file 'config.data' not found.")
    sys.exit(1)

cpass.read('config.data')

try:
    api_id = cpass['cred']['id']
    api_hash = cpass['cred']['hash']
    phone = cpass['cred']['phone']
    client = TelegramClient(phone, api_id, api_hash)
except KeyError:
    os.system('clear')
    banner()
    print(f"{re}[!] Please run {gr}python3 setup.py{re} first !!!\n")
    sys.exit(1)

# Connect to client
try:
    client.connect()
except Exception as e:
    print(f"{re}[!] Connection error: {e}")
    sys.exit(1)

if not client.is_user_authorized():
    client.send_code_request(phone)
    os.system('clear')
    banner()
    client.sign_in(phone, input(f"{gr}[+] Enter the sent code: {re}"))

os.system('clear')
banner()

if len(sys.argv) < 2:
    print(f"{re}[!] Please provide the input file as a command-line argument.")
    sys.exit(1)

input_file = sys.argv[1]
users = []
try:
    with open(input_file, encoding='UTF-8') as f:
        rows = csv.reader(f, delimiter=",", lineterminator="\n")
        next(rows, None)
        for row in rows:
            user = {
                'username': row[0],
                'id': int(row[1]),
                'access_hash': int(row[2]),
                'name': row[3],
            }
            users.append(user)
except FileNotFoundError:
    print(f"{re}[!] Error: The specified file '{input_file}' was not found.")
    sys.exit(1)

# Fetch chats
chats = []
last_date = None
chunk_size = 200
groups = []

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)

for chat in chats:
    try:
        if chat.megagroup:
            groups.append(chat)
    except AttributeError:
        continue

print(f"{gr}[+] Choose a group to add members: {re}")
for i, group in enumerate(groups):
    print(f"{i} - {group.title}")

g_index = int(input(f"{gr}Enter a Number: {re}"))
if g_index < 0 or g_index >= len(groups):
    print(f"{re}[!] Invalid group selected.")
    sys.exit(1)

target_group = groups[g_index]
target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

print(f"{gr}[1] Add member by user ID\n[2] Add member by username")
mode = int(input(f"{gr}Input: {re}"))
if mode not in [1, 2]:
    print(f"{re}[!] Invalid Mode Selected. Please Try Again.")
    sys.exit(1)

n = 0

for user in users:
    n += 1
    if n % 50 == 0:
        time.sleep(900)  # Adjust this value as needed
    try:
        print(f"Adding {user['id']}")
        if mode == 1:
            if not user['username']:
                continue
            user_to_add = client.get_input_entity(user['username'])
        elif mode == 2:
            user_to_add = InputPeerUser(user['id'], user['access_hash'])
        
        client(InviteToChannelRequest(target_group_entity, [user_to_add]))
        print(f"{gr}[+] Waiting for 60-180 sec ...")
        time.sleep(random.randrange(60, 180))
    except PeerFloodError:
        print(f"{re}[!] Getting Flood Errors from Telegram. \n[!] Script is stopping for now. \n[!] Please try again after some time.")
        break
    except UserPrivacyRestrictedError:
        print(f"{re}[!] The user's privacy settings do not allow you to do this. Skipping ...")
    except Exception as e:
        traceback.print_exc()
        print(f"{re}[!] Unexpected Error: {e} ...")
        continue
