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
from telethon.errors import SessionPasswordNeededError
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
phone = "+" + input(f"{Fore.LIGHTBLUE_EX}Your phone: +{Style.RESET_ALL}")
username = input(f"{Fore.LIGHTBLUE_EX}Your user tag: @{Style.RESET_ALL}")

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)


async def auth(phone):
    await client.start()
    print("[scrappy] Client has been created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()


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
    user_input_tag = input("User tag: @")
    try:
        user = await client.get_entity(user_input_tag)
        print(f"{Fore.GREEN}Done! {user.username}:{user.id}{Style.RESET_ALL}")
    except UsernameInvalidError as e:
        await event.respond(f'{Fore.YELLOW}Invalid user tag. Try another{Style.RESET_ALL}')
        raise events.StopPropagation


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

    filename = user_input_channel.replace("/", "_").replace(":", "")
    df = pd.DataFrame(all_messages)
    full_filename = user_input_tag + '_messages'+filename+'.csv'
    df.to_csv(full_filename, index=False)
    print(f"{Fore.GREEN}Done: {full_filename}{Style.RESET_ALL}")


async def get_members():
    user_input_channel = input("Group URL or ID: ")

    if user_input_channel.isdigit():
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
            {"user.id": participant.id,
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
        f"{Fore.LIGHTYELLOW_EX}#1 : Get the group members :\n#2 : Get messages :\n#3 : Get groups :\n#4 : Get user id :\n{Fore.RED}#5 : Log out :{Style.RESET_ALL}")

    your_option = input("\nEnter the option's number: #")

    if (your_option == "1"):
        try:
            await get_members()
        except ValueError as e:
            print(f"{Fore.YELLOW} : Try another URL\id : {Style.RESET_ALL}")
        sleep(2)
        await get_options()
    elif (your_option == "2"):
        await get_messages()
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


async def main(phone):
    utils.clear()
    auth(phone)
    await get_options()


with client:
    client.loop.run_until_complete(main(phone))
