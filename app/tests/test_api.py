import unittest
import json
from app import create_app


class BasicTests(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['LOGIN_DISABLED'] = True
        app.login_manager.init_app(app)
        self.app = app.test_client()

    def test_main_page(self):
        response = self.app.get('/api/measurements/airpressure?limit=120')
        self.assertEqual(response.status_code, 200)
        air_body = response.json

        response = self.app.get('/api/measurements/temperature')
        self.assertEqual(response.status_code, 200)
        temp_body = response.json

        body = {"airpressure": air_body["data"], "temperature": temp_body["data"]}

        response = self.app.post(
            '/api/measurements/export/file', data=json.dumps(body), content_type='application/json')
        print(response.json)


if __name__ == "__main__":
    unittest.main()
