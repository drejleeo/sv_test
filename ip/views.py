from json import JSONDecodeError

from rest_framework import status
from django.http import JsonResponse
from rest_framework.views import APIView
from datetime import datetime
import json
import requests
import pytz

from skillvaluetest.settings import IP_SERVICE_URL


error_messages = {
    status.HTTP_400_BAD_REQUEST: 'Invalid request. Specified body or request parameters are not valid.',
}


class TrackActionAPI(APIView):

    @staticmethod
    def throw_error(code):
        error = {
            'errors': [error_messages[code],]
        }
        return JsonResponse(error, status=code)

    def post(self, request, *args, **kwargs):
        action = kwargs.get('action')
        try:
            info = json.loads(request.body.decode())
        except JSONDecodeError:
            return self.throw_error(400)

        # Validate parameters and body
        if (action not in ('login', 'logout', 'buy', 'review', 'shopping-cart') or
                info.get('ip') is None or
                info.get('resolution') is None):
            return self.throw_error(400)

        # Retrieve IP information
        location = retrieve_ip_details(info.get('ip'))
        if location.get('status') == 'fail':
            return self.throw_error(400)

        # Compute client time
        client_timezone = pytz.timezone(location.get('timezone'))
        utc_now = pytz.utc.localize(datetime.utcnow())
        client_now = utc_now.astimezone(client_timezone)

        # Build response
        final = {
            'action': action,
            'info': info,
            'location': {
                key: location[key] for key in ('lon', 'lat', 'city', 'region', 'country', 'countryCode')
            },
            'action_date': client_now.isoformat(),
        }
        return JsonResponse(final)


def retrieve_ip_details(ip_addr):
    res = requests.get(url='/'.join((IP_SERVICE_URL, ip_addr)))
    location = json.loads(res.content.decode())
    return location
