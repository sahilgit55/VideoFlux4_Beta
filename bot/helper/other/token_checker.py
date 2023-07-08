#!/usr/bin/env python3
from uuid import uuid4
from time import time

from bot import  bot_name, OWNER_ID, config_dict, user_data
from bot.helper.other.shortner import short_url
from bot.helper.pyrogram.button_build import ButtonMaker
from bot.helper.pyrogram.message_utils import sendMessage


async def isAdmin(message, user_id=None):
    user = message.from_user or message.sender_chat
    if user.id == OWNER_ID:
        return True
    if message.chat.type == message.chat.type.PRIVATE:
        return
    if user_id:
        member = await message.chat.get_member(user_id)
    else:
        member = await message.chat.get_member(user.id)
    return member.status in [member.status.ADMINISTRATOR, member.status.OWNER] 


def checking_access(user_id, button=None):
    if not config_dict['TOKEN_TIMEOUT']:
        return None, button
    user_data.setdefault(user_id, {})
    data = user_data[user_id]
    expire = data.get('time')
    isExpired = (expire is None or expire is not None and (
        time() - expire) > config_dict['TOKEN_TIMEOUT'])
    if isExpired:
        token = data['token'] if expire is None and 'token' in data else str(uuid4())
        if expire is not None:
            del data['time']
        data['token'] = token
        user_data[user_id].update(data)
        if button is None:
            button = ButtonMaker()
        button.ubutton('Refresh Token', short_url(
            f'https://t.me/{bot_name}?start={token}'))
        return 'Token is expired, refresh your token and try again.', button
    return None, button




async def checkToken(message):
    if not await isAdmin(message):
        token_msg, buttons = checking_access(message.from_user.id)
        if token_msg:
            await sendMessage(message, token_msg, buttons=buttons.build_menu(1))
            return False
    return True