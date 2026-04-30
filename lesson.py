import requests
import sqlite3


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


def main():
    db = ChatDatabase()
    messages = [{
        "role": "system",
        "content": """Ти веселий бомж Єгорка. Постійно травиш якісь приколи, іноді відповідаєш похабно і хамовито. Саботуєш завдання з причини алкогольного спяніння. Але загалом радужний і добряк. Якщо до тебе гарно звертаються то ти чемний і слухняний."""
    }]
    messages = messages + db.load_messages()

    while True:
        user_message = input("\n You:")
        messages.append({"role": "user", "content": user_message})
        db.save_message("user", user_message)

        response = requests.request(
            'POST',
            'http://127.0.0.1:1234/v1/chat/completions',
            json={
                "messages": messages,
                "model": "google/gemma-4-e4b"
            }
        )
        response_json = response.json()
        ai_message = response_json["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": ai_message})
        db.save_message("assistant", ai_message)
        print("\nAI: " + ai_message)


if __name__ == '__main__':
    main()
