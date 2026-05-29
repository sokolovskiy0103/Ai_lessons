from langchain_core.tools import tool

from services.db import get_conn


@tool
def add_task(title: str, time: str) -> str:
    """Додати задачу до розкладу. Параметри: title - назва, time - час у форматі HH:MM."""
    with get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, time) VALUES (?, ?)", (title, time)
        )
        task_id = cursor.lastrowid
    return f"Задачу #{task_id} '{title}' о {time} додано."


@tool
def update_task(task_id: int, title: str = None, time: str = None, done: bool = None) -> str:
    """Оновити задачу за ID. Усі поля крім task_id необов'язкові. Передай тільки те, що потрібно змінити."""
    fields = {k: v for k, v in {"title": title, "time": time, "done": done}.items() if v is not None}
    if "done" in fields:
        fields["done"] = int(fields["done"])
    if not fields:
        return "Не вказано жодного поля для оновлення."
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    with get_conn() as conn:
        cursor = conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", (*fields.values(), task_id))
    if cursor.rowcount == 0:
        return f"Задачу #{task_id} не знайдено."
    return f"Задачу #{task_id} оновлено: {', '.join(fields)}."


@tool
def get_schedule(time_from: str = None, time_to: str = None) -> str:
    """Отримати список задач. Опційно: time_from і time_to — фільтр за часом у форматі HH:MM."""
    query = "SELECT * FROM tasks"
    params = []
    if time_from and time_to:
        query += " WHERE time BETWEEN ? AND ?"
        params = [time_from, time_to]
    elif time_from:
        query += " WHERE time >= ?"
        params = [time_from]
    elif time_to:
        query += " WHERE time <= ?"
        params = [time_to]
    query += " ORDER BY time"
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    if not rows:
        return "Розклад порожній."
    lines = [f"[{'✓' if row['done'] else '○'}] #{row['id']} {row['time']} — {row['title']}" for row in rows]
    return "\n".join(lines)