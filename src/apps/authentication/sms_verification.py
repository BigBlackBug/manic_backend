import logging
import random
import string
from urllib import parse

import requests
from django.conf import settings
from rest_framework import status

from src.apps.core.exceptions import ApplicationError

SMS_ERROR = ApplicationError.ErrorTypes.SMS_ERROR
SMS_RU_RESPONSE_OK = 100
SMS_RU_NO_MONEY = 201
SMS_RU_SERVICE_UNAVAILABLE = 220

logger = logging.getLogger(__name__)


def _id_generator(size=8,
                  chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


_SMS_TEMPLATE = 'Доброго времени суток! Ваш код активации: {}'


def generate_code(phone: str = '88005553535'):
    # why not?
    # random.seed(phone)
    return _id_generator(size=4, chars=string.digits)


def send_code(phone: str, code: str):
    """
    Sends an sms with `code` to the `phone` number.
    Raises ApplicationError on any failure to send a message

    :param phone:
    :param code:
    :return:
    """
    args = parse.urlencode({
        'api_id': settings.SMS_API_KEY,
        'to': phone,
        'msg': _SMS_TEMPLATE.format(code),
        'json': 1
    })
    logger.info(f'Sending code {code} to {phone}')

    url = 'https://sms.ru/sms/send/'
    resp = requests.post(f'{url}?{args}')

    logger.debug(f'Response from sms.ru - {resp.status_code}')

    if resp.status_code != status.HTTP_200_OK:
        raise ApplicationError('Unable to send SMS. Unexpected error',
                               error_type=SMS_ERROR)

    json = resp.json()
    status_code = json['status_code']
    balance = json['balance']

    if balance < settings.SMS_RU_WARNING_BALANCE_RUB:
        logger.warning(f'Current Balance ({balance}) is low. '
                       f'Consider refilling.')
        # TODO send a notification
        pass

    if status_code == SMS_RU_RESPONSE_OK:
        sms_response = json['sms'][phone]

        if sms_response['status_code'] != SMS_RU_RESPONSE_OK:
            # TODO proper error handling
            raise ApplicationError(sms_response['status_text'],
                                   error_type=SMS_ERROR)
    else:
        if status_code == SMS_RU_NO_MONEY:
            # TODO send a notification
            pass
        elif status_code == SMS_RU_SERVICE_UNAVAILABLE:
            # TODO send a notification
            pass
        raise ApplicationError(
            f'Unable to send SMS. Reason: {json["status_text"]}',
            error_type=SMS_ERROR)
