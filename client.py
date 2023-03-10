import configparser
import json
import asyncio
import pandas as pd
from os import system, name
from time import sleep

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, UsernameInvalidError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import (
    PeerChannel, PeerUser
)

import constants
import utils

# Setting configuration values
api_id = constants.API_ID
api_hash = str(constants.HASH_ID)
username = input(f"{Fore.LIGHTBLUE_EX}Your user tag: @{Style.RESET_ALL}")


async def get_groups():
    all_groups = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            all_groups.append({"ID": dialog.id, "TITLE": dialog.title})

    df = pd.DataFrame(all_groups)
    full_filename = username + "_groups.csv"
    df.to_csv(full_filename, index=False)
    print(f"{Fore.GREEN}Done: {full_filename}{Style.RESET_ALL}")


async def get_user_id():
    user_input_tag = input("User tag(s): @")
    user_input_tag_arr = user_input_tag.strip().split(" ")

    if len(user_input_tag_arr) > 1:
        all_ids = []
        for tag in user_input_tag_arr:
            try:
                user = await client.get_entity(tag)
                all_ids.append({"username": user.username, "ID": user.id})
            except ValueError as e:
                print(
                    f'{Fore.YELLOW}Invalid user tag ({tag}). Try another{Style.RESET_ALL}')
        df = pd.DataFrame(all_ids)
        filename = 'IDs.csv'
        df.to_csv(filename, index=False)
        print(f"{Fore.GREEN}Done: {filename}{Style.RESET_ALL}")
    else:
        try:
            user = await client.get_entity(user_input_tag)
            print(f"{Fore.GREEN}Done! {user.username}:{user.id}{Style.RESET_ALL}")
        except ValueError as e:
            print(f'{Fore.YELLOW}Invalid user tag. Try another{Style.RESET_ALL}')


async def get_messages():
    user_input_channel = input("Group URL or ID: ")
    user_input_tag = input("User TAG or ID: @")
    # Get group entity by URL or ID
    if user_input_channel.lstrip("-").isdigit():
        channel_entity = PeerChannel(int(user_input_channel))
    else:
        channel_entity = user_input_channel

    my_channel = await client.get_entity(channel_entity)
    # Get user entity by URL or ID
    if user_input_tag.isdigit():
        user_entity = PeerUser(int(user_input_tag))
    else:
        user_entity = user_input_tag

    my_user = await client.get_entity(user_entity)

    all_messages = []

    async for message in client.iter_messages(my_channel, from_user=my_user):
        all_messages.append({"id": message.id, "text": message.text})
        if message.photo:
            save_path = utils.make_photo_dir(user_input_tag)
            path = await client.download_media(message.media, save_path)
            print(f"{Fore.LIGHTGREEN_EX}Photo // {path}{Style.RESET_ALL}")

    filename = user_input_channel.replace("/", "_").replace(":", "")
    df = pd.DataFrame(all_messages)
    full_filename = user_input_tag + '_messages'+filename+'.csv'
    df.to_csv(full_filename, index=False)
    print(f"{Fore.GREEN}Done: {full_filename}{Style.RESET_ALL}")


async def get_members():
    user_input_channel = input("Group URL or ID: ")

    if user_input_channel.lstrip("-").isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset = 0
    limit = 100
    all_participants = []

    while True:
        participants = await client(GetParticipantsRequest(
            my_channel, ChannelParticipantsSearch(''), offset, limit,
            hash=0
        ))
        if not participants.users:
            break
        all_participants.extend(participants.users)
        offset += len(participants.users)

    all_user_details = []
    for participant in all_participants:
        all_user_details.append(
            {"group_title": my_channel.title,
             "user.id": participant.id,
             "first_name": participant.first_name,
             "last_name": participant.last_name,
             "username": participant.username,
             "phone": "a_"+str(participant.phone),
             "user.access_hash": participant.access_hash,
             "is_bot": participant.bot})

    filename = user_input_channel.replace("/", "_").replace(":", "")
    df = pd.DataFrame(all_user_details)
    full_filename = 'withphone_'+filename+'.csv'
    df.to_csv(full_filename, index=False)
    print(f"{Fore.GREEN}Done: {full_filename}{Style.RESET_ALL}")


async def get_options():
    utils.clear()
    print("=========\n Options:\n=========")
    print(
        f"{Fore.LIGHTYELLOW_EX}#1 : Get the group members :\n#2 : Get messages :\n#3 : Get groups :\n#4 : Get user id(s) :\n{Fore.RED}#5 : Log out :{Style.RESET_ALL}")

    your_option = input("\nEnter the option's number: #")

    if (your_option == "1"):
        try:
            await get_members()
        except ValueError as e:
            print(f"{Fore.YELLOW} : Try another URL\id : {Style.RESET_ALL}")
        sleep(2)
        await get_options()
    elif (your_option == "2"):
        try:
            await get_messages()
        except ValueError as e:
            print(f"{Fore.YELLOW} : Try another URL\id : {Style.RESET_ALL}")
        sleep(2)
        await get_options()
    elif (your_option == "3"):
        await get_groups()
        sleep(2)
        await get_options()
    elif (your_option == "4"):
        await get_user_id()
        sleep(5)
        await get_options()
    elif (your_option == "5"):
        await client.log_out()
        print(f"{Fore.GREEN} Bye, {username}{Style.RESET_ALL}")
    else:
        await get_options()

# Create seesion via user credentials
with TelegramClient(username, api_id, api_hash) as client:
    client.start()
    client.loop.run_until_complete(get_options())
