from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from src.apps.authentication.mgmt.models import AdminToken
from src.apps.authentication.utils import get_admin_user_model

AdminUser = get_admin_user_model()


class MgmtLoginView(GenericAPIView):
    view_name = 'mgmt_login'
    permission_classes = ()
    serializer_class = serializers.Serializer

    def post(self, request, *args, **kwargs):
        """
        A temporary(or permanent) endpoint for admin app auth

        Input:
        ``` { 'username':'super', 'password':'boss' } ```

        Response:
        ```  { 'token':'my_token' } ```
        """
        username = request.data['username']
        password = request.data['password']
        try:
            user = AdminUser.objects.get(username=username)
        except AdminUser.DoesNotExist as ex:
            raise PermissionDenied("Unknown user")
        else:
            if user.check_password(password):
                token, created = AdminToken.objects.get_or_create(user=user)
                return Response(data={
                    'token': token.key
                })
            else:
                raise PermissionDenied("invalid pass")