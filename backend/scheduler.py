from apscheduler.schedulers.background import BackgroundScheduler

from database import (
    get_due_notifications,
    schedule_next_notification
)

def send_notification(notification):
    print("--------------------------------")
    print("MEALEMBRA - NOVA NOTIFICAÇÃO")
    print(f"Lembrete: {notification['title']}")
    print(f"Descrição: {notification['description']}")
    print("--------------------------------")

    return True

def check_notifications():

    notifications = get_due_notifications()

    for notification in notifications:

        sent = send_notification(notification)

        if sent:
            schedule_next_notification(
             notification["notification_id"]
            )


scheduler = BackgroundScheduler()

scheduler.add_job(
    check_notifications,
    trigger="interval",
    seconds=10
)


def start_scheduler():
    scheduler.start()
    print("MeAlembra Scheduler iniciado!")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("MeAlembra Scheduler encerrado!")