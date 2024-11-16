from fastapi import APIRouter, BackgroundTasks, Depends

from src.test.test import send_email_report_dashboard
from src.user.base_config import current_user

router = APIRouter(prefix="/report")


@router.get("/dashboard")
def get_dashboard_report(background_tasks: BackgroundTasks, user=Depends(current_user)):
    background_tasks.add_task(send_email_report_dashboard, user.username)
    # 1400 ms - Клиент ждет
    return {
        "status": 200,
        "data": "Письмо отправлено",
        "details": None
    }
