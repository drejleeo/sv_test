from django.urls import reverse
from django.test import TestCase
from unittest.mock import Mock, patch
import json

from ip.views import TrackActionAPI


class TrackActionTest(TestCase):
    def setUp(self):
        self.actions = ('login', 'logout', 'buy', 'review', 'shopping-cart')
        self.ip = '123.123.123.123'
        TrackActionAPI.get_json_info_from_ip_service = Mock(return_value={
            "status": "success",
            "country": "Germany",
            "countryCode": "DE",
            "region": "HE",
            "regionName": "Hesse",
            "city": "Bad Soden am Taunus",
            "lat": 179.99,
            "lon": 89.99,
            "timezone": "Europe/Berlin",
            "isp": "GHOSTnet GmbH",
            "org": "IP Interactive",
            "as": "AS12586 GHOSTnet GmbH",
            "query": self.ip,
        })

    @staticmethod
    def get_request_body(ip='123.123.123.123'):
        return {
            "ip": ip,
            "resolution": {
                "width": 1920,
                "height": 1080
            }
        }

    def _assert_call_response(self, action, request_body, status=200, keys_in_res=()):
        res = self.client.post(
            path=reverse('track_api', args=(action,)),
            data=json.dumps(request_body),
            content_type='content/json'
        )
        self.assertEqual(res.status_code, status)
        content = json.loads(res.content)
        if keys_in_res:
            self.assertEqual(any(key in content for key in keys_in_res), True)

    def test_route_actions_200(self):
        for action in self.actions:
            self._assert_call_response(action, self.get_request_body(), 200, ('action', 'location', 'info', 'action_date'))

    def test_route_wrong_action(self):
        self._assert_call_response('bad_action', self.get_request_body(), 400, ('action',))

    def test_empty_request_body(self):
        self._assert_call_response('login', {}, 400, ('ip', 'resolution'))

    def test_missing_body_key(self):
        self._assert_call_response('login', {'ip': self.ip}, 400, ('resolution',))
        self._assert_call_response('login', {'resolution': {'width': 0, 'height': 0}}, 400, ('ip',))

    def test_invalid_ip(self):
        self._assert_call_response('login', self.get_request_body('12.5.as.ye4'), 400, ('ip',))

    def test_ip_service_not_available(self):
        TrackActionAPI.get_json_info_from_ip_service = Mock(return_value={"status": "fail", "message": "invalid query"})
        self._assert_call_response('login', self.get_request_body(), 503, ('service',))
