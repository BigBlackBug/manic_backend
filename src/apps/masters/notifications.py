from src.apps.masters.models import MasterStatus

MASTER_STATUS_CHANGED_TITLE = "Новый статус профиля"
MASTER_STATUS_MAP = {
    MasterStatus.VERIFIED: "Вы успешно прошли проверку профиля. "
                           "Добавьте расписание для начала работы!",
    MasterStatus.DELETED: "Ваша заявка на регистрацию была отклонена",
    MasterStatus.BLOCKED: "Ваш профиль был заблокирован",

}
