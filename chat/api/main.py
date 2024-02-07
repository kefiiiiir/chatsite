from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js

import asyncio

chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 100

async def main():
    global chat_msgs

    async def refresh_msg(nickname, msg_box):
        global chat_msgs
        last_idx = len(chat_msgs)

        while True:
            await asyncio.sleep(1)
            for m in chat_msgs[last_idx:]:
                if m[0] != nickname:
                    msg_box.append(put_markdown(f"{m[0]}: {m[1]}"))

            if len(chat_msgs) >= MAX_MESSAGES_COUNT:
                chat_msgs = chat_msgs[len(chat_msgs) // 2:]

            last_idx = len(chat_msgs)

    put_markdown("bro heeeellloooo!!!!! ")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input("get into chat", required=True, placeholder="Enter your nickname: ", validate=lambda n: "this nickname is not valid" if n in online_users or n == "" else None)
    online_users.add(nickname)

    chat_msgs.append(('!!!', f"{nickname} joined the chat!"))
    msg_box.append(put_markdown(f"{nickname} joined the chat!"))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        data = await input_group("new message", [input(placeholder="Enter your message: ", name="msg"),
                                                 actions(name="cmd", buttons=["send", {'label':"exit chat", 'type':'cancel'}])],
                                 validate=lambda m: ('msg', 'enter your message') if m['cmd'] == 'Send'and not m['msg'] else None)
        if data is None:
            break

        msg_box.append(put_markdown(f"{nickname}: {data['msg']}"))
        chat_msgs.append((nickname, data['msg']))

    refresh_task.close()

    online_users.remove(nickname)
    toast("You've exited the chat!")
    msg_box.append(put_markdown(f"User {nickname} left the chat!"))
    chat_msgs.append((f'user {nickname} left the chat!'))

    put_buttons(["Re-join"], onclick=lambda btn: run_js('window.location.reload()'))

if __name__ == "__main__":
    start_server(main, debug=False, port=8080, cdn=False)
