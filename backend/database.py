from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
# Caminho da base de dados
DATABASE_PATH = Path(__file__).resolve().parent / "assistant.db"


# Criar a tabela de anotações
def init_db():

    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def get_all_notes():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM notes")

    notes = cursor.fetchall()

    connection.close()

    return [dict(note) for note in notes]



def create_note(title, content):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO notes (title, content) VALUES (?, ?)",
        (title, content)
    )

    connection.commit()

    note_id = cursor.lastrowid

    connection.close()

    return {
        "id": note_id,
        "title": title,
        "content": content
    }


def update_note(note_id, title, content):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE notes SET title = ?, content = ? WHERE id = ?",
        (title, content, note_id)
    )

    connection.commit()

    rows_updated = cursor.rowcount

    connection.close()

    return rows_updated


def init_reminders_table():
    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            reminder_datetime TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            recurrence_type TEXT NOT NULL DEFAULT 'none',
            recurrence_interval INTEGER DEFAULT 1,
            recurrence_end TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

def init_notifications_table():
    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("PRAGMA foreign_keys = ON")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reminder_id INTEGER NOT NULL,
            minutes_before INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,

            FOREIGN KEY (reminder_id)
            REFERENCES reminders(id)
            ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()


def create_reminder(title, description, reminder_datetime,
                    recurrence_type, recurrence_interval,
                    recurrence_end):

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO reminders (
            title,
            description,
            reminder_datetime,
            recurrence_type,
            recurrence_interval,
            recurrence_end
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title,
        description,
        reminder_datetime,
        recurrence_type,
        recurrence_interval,
        recurrence_end
    ))

    connection.commit()

    reminder_id = cursor.lastrowid

    connection.close()

    return reminder_id


def delete_note(note_id):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    connection.commit()

    rows_deleted = cursor.rowcount

    connection.close()

    return rows_deleted


#funcao de cosnultar os lemvretes
def get_all_reminders():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM reminders ORDER BY reminder_datetime ASC")

    reminders = cursor.fetchall()

    connection.close()

    return [dict(reminder) for reminder in reminders]


def update_reminder(
    reminder_id,
    title,
    description,
    reminder_datetime,
    recurrence_type,
    recurrence_interval,
    recurrence_end
):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE reminders
        SET title = ?,
            description = ?,
            reminder_datetime = ?,
            recurrence_type = ?,
            recurrence_interval = ?,
            recurrence_end = ?
        WHERE id = ?
    """, (
        title,
        description,
        reminder_datetime,
        recurrence_type,
        recurrence_interval,
        recurrence_end,
        reminder_id
    ))

    connection.commit()

    rows_updated = cursor.rowcount

    connection.close()

    return rows_updated


def reschedule_reminder(reminder_id, new_datetime):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE reminders
        SET reminder_datetime = ?,
            status = 'pending'
        WHERE id = ?
    """, (new_datetime, reminder_id))

    connection.commit()

    rows_updated = cursor.rowcount

    connection.close()

    return rows_updated

def complete_reminder(reminder_id):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    # Marcar o lembrete como concluído
    cursor.execute("""
        UPDATE reminders
        SET status = 'completed'
        WHERE id = ?
    """, (reminder_id,))

    rows_updated = cursor.rowcount

    # Se o lembrete existir, desativar as notificações
    if rows_updated > 0:
        cursor.execute("""
            UPDATE notifications
            SET is_active = 0
            WHERE reminder_id = ?
        """, (reminder_id,))

    connection.commit()
    connection.close()

    return rows_updated


# para o user conseguir apagar permanentemente uma note
def delete_reminder(reminder_id):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM reminders WHERE id = ?",
        (reminder_id,)
    )

    connection.commit()

    rows_deleted = cursor.rowcount

    connection.close()

    return rows_deleted



def create_notification(
    reminder_id,
    reminder_datetime,
    interval_minutes=15
):
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO notifications (
            reminder_id,
            interval_minutes,
            next_send_at
        )
        VALUES (?, ?, ?)
    """, (
        reminder_id,
        interval_minutes,
        reminder_datetime
    ))

    connection.commit()

    notification_id = cursor.lastrowid

    connection.close()

    return notification_id

def calculate_first_send_at(
    reminder_datetime,
    notification_type,
    scheduled_time
):
    reminder_date = datetime.fromisoformat(reminder_datetime)

    # Notificação por intervalo:
    # A primeira notificação acontece na data do lembrete.
    if notification_type == "interval":
        return reminder_date.isoformat()

    # Notificação por horário específico:
    if notification_type == "specific_time":

        notification_time = datetime.strptime(
            scheduled_time,
            "%H:%M"
        ).time()

        next_notification = datetime.combine(
            reminder_date.date(),
            notification_time,
            tzinfo=reminder_date.tzinfo
        )

        # Se o horário escolhido já passou,
        # a próxima notificação será no dia seguinte.
        if next_notification < reminder_date:
            next_notification += timedelta(days=1)

        return next_notification.isoformat()

    return None

def get_notifications_by_reminder(reminder_id):
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Verificar se o lembrete existe
    cursor.execute(
        "SELECT id FROM reminders WHERE id = ?",
        (reminder_id,)
    )

    reminder = cursor.fetchone()

    if reminder is None:
        connection.close()
        return None

    # Consultar as notificações do lembrete
    cursor.execute(
        "SELECT * FROM notifications WHERE reminder_id = ?",
        (reminder_id,)
    )

    notifications = cursor.fetchall()

    connection.close()

    return [dict(notification) for notification in notifications]



def toggle_notification(notification_id, is_active):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE notifications
        SET is_active = ?
        WHERE id = ?
    """, (is_active, notification_id))

    connection.commit()

    rows_updated = cursor.rowcount

    connection.close()

    return rows_updated

def delete_notification(notification_id):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM notifications WHERE id = ?",
        (notification_id,)
    )

    connection.commit()

    rows_deleted = cursor.rowcount

    connection.close()

    return rows_deleted


def get_reminder_by_id(reminder_id):
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM reminders WHERE id = ?",
        (reminder_id,)
    )

    reminder = cursor.fetchone()

    connection.close()

    if reminder is None:
        return None

    return dict(reminder)


def calculate_next_date(reminder_datetime, recurrence_type, recurrence_interval):

    current_date = datetime.fromisoformat(reminder_datetime)

    if recurrence_type == "daily":
        next_date = current_date + timedelta(days=recurrence_interval)

    elif recurrence_type == "weekly":
        next_date = current_date + timedelta(weeks=recurrence_interval)

    elif recurrence_type == "monthly":
        # Vamos implementar esta parte a seguir.
        pass

    elif recurrence_type == "yearly":
        # Vamos implementar esta parte a seguir.
        pass

    else:
        return None

    return next_date.isoformat()

#notificações que estão na hora de ser enviadas 
def get_due_notifications():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    current_time = datetime.now().isoformat()

    cursor.execute("""
        SELECT
            notifications.id AS notification_id,
            notifications.reminder_id,
            notifications.interval_minutes,
            notifications.next_send_at,
            reminders.title,
            reminders.description
        FROM notifications
        JOIN reminders
            ON notifications.reminder_id = reminders.id
        WHERE notifications.is_active = 1
        AND reminders.status = 'pending'
        AND notifications.next_send_at <= ?
    """, (current_time,))

    notifications = cursor.fetchall()

    connection.close()

    return [dict(notification) for notification in notifications]




def get_due_notifications():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    current_time = datetime.now().isoformat()

    cursor.execute("""
        SELECT
            notifications.id AS notification_id,
            notifications.reminder_id,
            notifications.interval_minutes,
            notifications.next_send_at,
            reminders.title,
            reminders.description
        FROM notifications
        JOIN reminders
            ON notifications.reminder_id = reminders.id
        WHERE notifications.is_active = 1
        AND reminders.status = 'pending'
        AND notifications.next_send_at <= ?
    """, (current_time,))

    notifications = cursor.fetchall()

    connection.close()

    return [dict(notification) for notification in notifications]


# Calcula e guarda a próxima hora de envio.
def schedule_next_notification(notification_id):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT interval_minutes
        FROM notifications
        WHERE id = ?
    """, (notification_id,))

    notification = cursor.fetchone()

    if notification is None:
        connection.close()
        return False

    interval_minutes = notification[0]

    next_send = datetime.now() + timedelta(
        minutes=interval_minutes
    )

    cursor.execute("""
        UPDATE notifications
        SET next_send_at = ?
        WHERE id = ?
    """, (next_send.isoformat(), notification_id))

    connection.commit()
    connection.close()

    return True