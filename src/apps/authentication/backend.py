import logging

from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, \
    get_authorization_header

from .mgmt.models import AdminToken
from .models import Token as AppToken

logger = logging.getLogger(__name__)


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        ``Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a``
    """

    keyword = b'Token'
    admin_keyword = b'AdminToken'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0] not in \
                (self.keyword, self.admin_keyword):
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. '
                    'Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. '
                    'Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        if auth[0] == self.keyword:
            logger.info(f'Logging in an application with token {token}')
            return self.authenticate_application(token)
        elif auth[0] == self.admin_keyword:
            logger.info(f'Logging in an administrator with token {token}')
            return self.authenticate_admin(token)

    def authenticate_admin(self, key):
        try:
            token = AdminToken.objects.get(key=key)
        except AdminToken.DoesNotExist as ex:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
        else:
            return token.user, token

    def authenticate_application(self, key):
        try:
            token = AppToken.objects \
                .select_related('master', 'client').get(key=key)
        except AppToken.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if token.master:
            logger.info(f'Token {token} belongs to a master '
                        f'{token.master.first_name}')
            return token.master.user, token
        elif token.client:
            logger.info(f'Token {token} belongs to a client '
                        f'{token.client.first_name}')
            return token.client.user, token
        else:
            raise exceptions.AuthenticationFailed(
                _('User inactive or deleted.'))

    def authenticate_header(self, request):
        return self.keyword.decode()
