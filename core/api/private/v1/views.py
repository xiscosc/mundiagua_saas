from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from core.models import User


class UserIsAllowedToLoginView(APIView):
    def post(self, request, format=None):
        allowed = False
        try:
            user_data = request.data
            if 'email' in user_data:
                user = User.objects.get(email=user_data['email'])
                allowed = user.is_active
        except User.DoesNotExist:
            pass

        return Response(status=HTTP_200_OK, data={"allowed": allowed})
