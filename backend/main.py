from contextlib import asynccontextmanager
from database import (
    init_db,
    init_reminders_table,
    init_notifications_table,
    get_all_notes,
    create_note,
    update_note,
    delete_note,
    create_reminder,
    get_all_reminders,
    reschedule_reminder,
    complete_reminder,
    delete_reminder,
    create_notification,
    get_notifications_by_reminder,
    toggle_notification,
    delete_notification,
    get_reminder_by_id
)  # ligar a base de dados a main
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException #permite devolver erros 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scheduler import start_scheduler, stop_scheduler

# Criar a app
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Quando a aplicação inicia
    start_scheduler()

    yield

    # Quando a aplicação encerra
    stop_scheduler()


app = FastAPI(lifespan=lifespan)

# Inicializar as tabelas da base de dados
init_db()
init_reminders_table()
init_notifications_table()

# autorizar o  frontend local a comunicar com a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#---------------------------------------------------- S2
# CLASSES DA APP 

class Note(BaseModel):
    title: str
    content: str



class Reminder(BaseModel):
    title: str
    description: str | None = None # none=none significa que pode receber vazio e ta ok
    reminder_datetime: datetime
    recurrence_type: str = "none"
    recurrence_interval: int = 1
    recurrence_end: datetime | None = None


class RescheduleReminder(BaseModel):
    new_datetime: datetime


class Notification(BaseModel):
    notification_type: str
    interval_minutes: int | None = None
    scheduled_time: str | None = None

class NotificationStatus(BaseModel):
    is_active: bool

# -------------------------------------------------------------- S2

#ABAIXO SO AS ROTAS 

# GET
# a rota que leva a pagina inicial 
@app.get("/")
def home():
    return {"message": "Beeeem vinda, mulher!"}

@app.get("/notes")
def get_notes():
    return get_all_notes()


@app.get("/reminders/{reminder_id}/notifications")
def get_reminder_notifications(reminder_id: int):

    notifications = get_notifications_by_reminder(reminder_id)

    if notifications is None:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found"
        )

    return notifications


@app.get("/reminders")
def get_reminders():
    return get_all_reminders()


# POST
# rota para criar uma nota nova 
@app.post("/notes")
def create_new_note(note: Note):
    return create_note(note.title, note.content)


@app.post("/reminders")
def create_new_reminder(reminder: Reminder):

    # 1. Criar o lembrete
    reminder_id = create_reminder(
        reminder.title,
        reminder.description,
        reminder.reminder_datetime.isoformat(),
        reminder.recurrence_type,
        reminder.recurrence_interval,
        reminder.recurrence_end.isoformat()
        if reminder.recurrence_end else None
    )

    # 2. Criar automaticamente a configuração de notificação
    notification_id = create_notification(
        reminder_id,
        reminder.reminder_datetime.isoformat()
    )

    # 3. Devolver os dados
    return {
        "message": "O lembrete foi criado, diva! Não esquece!",
        "id": reminder_id,
        "title": reminder.title,
        "description": reminder.description,
        "reminder_datetime": reminder.reminder_datetime.isoformat(),
        "recurrence_type": reminder.recurrence_type,
        "recurrence_interval": reminder.recurrence_interval,
        "recurrence_end": (
            reminder.recurrence_end.isoformat()
            if reminder.recurrence_end else None
        ),
        "notification_id": notification_id,
        "notification_interval_minutes": 15
    }


@app.post("/reminders/{reminder_id}/notifications")
def add_notification(
    reminder_id: int,
    notification: Notification
):
    # Verificar se o lembrete existe
    reminder = get_reminder_by_id(reminder_id)

    if reminder is None:
        raise HTTPException(
            status_code=404,
            detail="Lembrete não encontrado divaaaa!"
        )

    # Validar o tipo de notificação
    if notification.notification_type not in ["interval", "specific_time"]:
        raise HTTPException(
            status_code=400,
            detail="Tipo de notificação inválido divaaaa!"
        )

    # Validar notificações por intervalo
    if notification.notification_type == "interval":

        if notification.interval_minutes is None or notification.interval_minutes <= 0:
            raise HTTPException(
                status_code=400,
                detail="O intervalo deve ser superior a zero!"
            )

        scheduled_time = None

    # Validar notificações por horário específico
    else:

        if notification.scheduled_time is None:
            raise HTTPException(
                status_code=400,
                detail="E a que horas vai ser isso???"
            )

        try:
            datetime.strptime(notification.scheduled_time, "%H:%M")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Horário inválido! Utiliza o formato HH:MM."
            )

        interval_minutes = None

        scheduled_time = notification.scheduled_time

    # Criar notificação
    notification_id = create_notification(
        reminder_id,
        notification.notification_type,
        notification.interval_minutes if notification.notification_type == "interval" else None,
        scheduled_time
    )

    return {
        "message": "Notification created successfully!",
        "notification_id": notification_id,
        "reminder_id": reminder_id,
        "notification_type": notification.notification_type,
        "interval_minutes": notification.interval_minutes if notification.notification_type == "interval" else None,
        "scheduled_time": scheduled_time
    }

# PUT 
# essa rota faz a att das anotacoes que ja existem
@app.put("/notes/{note_id}")
def update_existing_note(note_id: int, updated_note: Note):

    rows_updated = update_note(
        note_id,
        updated_note.title,
        updated_note.content
    )

    if rows_updated == 0:
        raise HTTPException(status_code=404, detail="A anotação não foi encontrada :/")

    return {
        "message": "Anotação atualizadíssima!!!",
        "id": note_id,
        "title": updated_note.title,
        "content": updated_note.content
    }


@app.put("/reminders/{reminder_id}")
def update_existing_reminder(
    reminder_id: int,
    updated_reminder: Reminder
):

    rows_updated = update_reminder(
        reminder_id,
        updated_reminder.title,
        updated_reminder.description,
        updated_reminder.reminder_datetime.isoformat(),
        updated_reminder.recurrence_type,
        updated_reminder.recurrence_interval,
        updated_reminder.recurrence_end.isoformat()
        if updated_reminder.recurrence_end else None
    )

    if rows_updated == 0:
        raise HTTPException(
            status_code=404,
            detail="Não achamos o lembrete em questão, divaa :("
        )

    return {
        "message": "Lembrete atualizadooo com maestria!!",
        "id": reminder_id
    }

# DELETE

@app.delete("/notes/{note_id}")
def delete_existing_note(note_id: int):

    rows_deleted = delete_note(note_id)

    if rows_deleted == 0:
        raise HTTPException(status_code=404, detail="Xiiii, não encontramos isso ai não")

    return {
   
       "message": "Lembrete excluído com sucesso!",
        "id": note_id
    }
@app.delete("/reminders/{reminder_id}")
def delete_existing_reminder(reminder_id: int):

    rows_deleted = delete_reminder(reminder_id)

    if rows_deleted == 0:
        raise HTTPException(
            status_code=404,
            detail="Menina, não encontrei esse lembrete!"
        )

    return {
        "message": "Lembrete eliminado com sucesso divaaa!",
        "id": reminder_id
    }

@app.delete("/notifications/{notification_id}")
def delete_existing_notification(notification_id: int):

    rows_deleted = delete_notification(notification_id)

    if rows_deleted == 0:
        raise HTTPException(
            status_code=404,
            detail="Notificação não encontrada!"
        )

    return {
        "message": "Notificação eliminada com sucesso!"
    }


# PATCH 

@app.patch("/reminders/{reminder_id}/reschedule")
def reschedule_existing_reminder(
    reminder_id: int,
    reschedule_data: RescheduleReminder
):

    rows_updated = reschedule_reminder(
        reminder_id,
        reschedule_data.new_datetime.isoformat()
    )

    if rows_updated == 0:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found"
        )

    return {
        "message": "Vamos deixar pra depois! Mas, abre o olho divaaa!!!!!",
        "id": reminder_id,
        "new_datetime": reschedule_data.new_datetime.isoformat(),
        "status": "pending"
    }




@app.patch("/reminders/{reminder_id}/complete")
def complete_existing_reminder(reminder_id: int):

    rows_updated = complete_reminder(reminder_id)

    if rows_updated == 0:
        raise HTTPException(
            status_code=404,
            detail="Menina, não encontrei o lembrete!"
        )

    return {
        "message": "Lembrete completadooooo uhuulll!",
        "id": reminder_id,
        "status": "completed"
    }




@app.patch("/notifications/{notification_id}")
def update_notification_status(
    notification_id: int,
    notification_status: NotificationStatus
):

    rows_updated = toggle_notification(
        notification_id,
        int(notification_status.is_active)
    )

    if rows_updated == 0:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return {
        "message": "Notification status updated!",
        "id": notification_id,
        "is_active": notification_status.is_active
    }

