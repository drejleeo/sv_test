from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from django.http import JsonResponse

from datetime import datetime
import requests
import pytz
import io

from skillvaluetest.settings import IP_SERVICE_URL
from ip.serializers import (
    SessionActionDetailsSerializer,
    SessionActionSerializer,
    SessionLocationDetails,
    SessionActionType,
)


class TrackActionAPI(APIView):

    @staticmethod
    def get_json_info_from_ip_service(ip: str):
        """
        Retrieve JSON information from IP Service endpoint.
        :param ip: str
        :return: dict
        """
        res = requests.get(url='/'.join((IP_SERVICE_URL, ip)))
        stream = io.BytesIO(res.content)
        return JSONParser().parse(stream)

    def post(self, request, *args, **kwargs):
        # Parse path parameter and body
        action = kwargs.get('action')
        action_ser = SessionActionType(data={'action': action})

        stream = io.BytesIO(request.body)
        json_body = JSONParser().parse(stream)
        info_ser = SessionActionSerializer(data=json_body)

        # Validate user input
        for serial in (action_ser, info_ser):
            if not serial.is_valid():
                return JsonResponse(serial.errors, status=400)

        # Retrieve IP information
        geo_json = self.get_json_info_from_ip_service(info_ser.data.get('ip'))
        location_ser = SessionLocationDetails(data=geo_json)
        if geo_json.get('status') != 'success' or not location_ser.is_valid():
            return JsonResponse({
                'service': 'Service temporarily unavailable.'
            }, status=503)
        client_tz = geo_json.get('timezone')

        # Compute client time
        client_timezone = pytz.timezone(client_tz)
        utc_now = pytz.utc.localize(datetime.utcnow())
        client_now = utc_now.astimezone(client_timezone)

        # Build response
        serializer = SessionActionDetailsSerializer(data={
            'action': action_ser.data.get('action'),
            'info': info_ser.data,
            'location': location_ser.data,
            'action_date': client_now.isoformat(),
        })
        if serializer.is_valid():
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
