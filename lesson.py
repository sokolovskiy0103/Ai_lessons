import sqlite3

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

load_dotenv()

class ChatDatabase:
    def load_messages(self):
        conn = sqlite3.connect('chat_history.db')
        cursor = conn.cursor()
        cursor.execute('SELECT role, content FROM messages ORDER BY id')
        messages = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        conn.close()
        return messages

    def save_message(self, role, content):
        conn = sqlite3.connect('chat_history.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (role, content) VALUES (?, ?)', (role, content))
        conn.commit()
        conn.close()

BOMZ_PROMPT = """Ти веселий бомж Толік. Постійно травиш якісь приколи, іноді відповідаєш похабно і хамовито. Саботуєш завдання з причини алкогольного спяніння. Але загалом радужний і добряк. Якщо до тебе гарно звертаються то ти чемний і слухняний."""
POLICE_PROMPT = """Ти суворий поліцейський Ігнат який вирішив доколупатись до місцевого бомжа"""


def swap_roles(messages: list[dict]) -> list[dict]:
    role_map = {"user": "assistant", "assistant": "user"}
    return [
        {**msg, "role": role_map.get(msg["role"], msg["role"])}
        for msg in messages
    ]

@tool
def notate(record: str) -> str:
    """
    Зробити запис в свій нотатник
    """
    print('\033[35m', end='', flush=True)
    print(record)
    print('\033[0m', flush=True)


def main():
    db = ChatDatabase()
    llm = init_chat_model(
        base_url='http://127.0.0.1:1234/v1',
        model='google/gemma-4-e4b',
        model_provider='openai',
        api_key='dgssd'
    )
    llm_police = llm.bind_tools([notate])
    messages = ChatDatabase().load_messages()[-3:]

    while True:
        result = ''
        response = llm_police.stream([{"role": "system", "content": POLICE_PROMPT}] + messages)
        print('\033[34m', end='', flush=True)
        for message in response:
            result += message.content
            print(message.content, end='')
        print('\033[0m', flush=True)
        db.save_message("assistant", result)
        messages.append({"role": "assistant", "content": result})
        print('\n')

        result = ''
        response = llm.stream([{"role": "system", "content": BOMZ_PROMPT}] + swap_roles(messages))

        for message in response:
            result += message.content
            print(message.content, end='')
        db.save_message("user", result)
        messages.append({"role": "user", "content": result})

if __name__ == '__main__':
    main()
