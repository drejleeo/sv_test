from django.test import TestCase
from django.urls import reverse
import json
from .views import retrieve_ip_details
from unittest.mock import Mock


# Create your tests here.
from ip.views import TrackActionAPI


class TrackActionTest(TestCase):
    def setUp(self):
        self.message_404 = b'{"errors": ["Invalid request. Specified body or request parameters are not valid."]}'
        self.actions = ('login', 'logout', 'buy', 'review', 'shopping-cart')
        self.data = {
            "ip": "95.76.1.153",
            "resolution": {
                "width": 0,
                "height": 0
            }
        }
        retrieve_ip_details = Mock()
        retrieve_ip_details.side_effect = {
            "status": "success",
            "country": "Romania",
            "countryCode": "RO",
            "region": "B",
            "regionName": "Bucharest",
            "city": "Bucharest",
            "zip": "052031",
            "lat": 44.4022,
            "lon": 26.0624,
            "timezone": "Europe/Bucharest",
            "isp": "UPC Romania",
            "org": "",
            "as": "AS6830 Liberty Global B.V.",
            "query": "95.76.1.153"
        }

    def test_route_actions_200(self):
        for action in self.actions:
            res = self.client.post(
                path=reverse('track_api', args=(action,)),
                data=json.dumps(self.data),
                content_type='content/json'
            )
            self.assertEqual(res.status_code, 200)
            for key in ('action', 'location', 'info', 'action_date'):
                self.assertIn(key, json.loads(res.content))

    def test_route_wrong_action(self):
        res = self.client.post(
            path=reverse('track_api', args=('badaction',)),
            data=json.dumps(self.data),
            content_type='content/json'
        )
        self.assertEqual(res.status_code, 400)

    def test_empty_request_body(self):
        res = self.client.post(
            path=reverse('track_api', args=('login',)),
            data=json.dumps({}),
            content_type='content/json'
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.content, self.message_404)

    def test_missing_body_key(self):
        res = res = self.client.post(
            path=reverse('track_api', args=('login',)),
            data=json.dumps({'ip': "95.76.1.153"}),
            content_type='content/json'
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.content, self.message_404)

        res = res = self.client.post(
            path=reverse('track_api', args=('login',)),
            data=json.dumps({'resolution': {"width": 0,"height": 0}}),
            content_type='content/json'
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.content, self.message_404)
