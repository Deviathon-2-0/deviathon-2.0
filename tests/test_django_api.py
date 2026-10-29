import json
from django.test import TestCase, Client
from django.urls import reverse

class ImairaApiTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_roles_endpoint(self):
        response = self.client.get('/api/roles/?category=Tech')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('roles', data)
        self.assertGreater(data['count'], 0)

    def test_companies_endpoint(self):
        response = self.client.get('/api/companies/?sector=Big Tech')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('companies', data)
        self.assertGreater(data['count'], 0)

    def test_interviewers_endpoint(self):
        response = self.client.get('/api/interviewers/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('interviewers', data)
        self.assertEqual(len(data['interviewers']), 9)
        names = [inv['name'] for inv in data['interviewers']]
        self.assertIn('Kabir', names)
        self.assertIn('Charlotte', names)
        self.assertIn('Kenji', names)

    def test_tts_accent_dispatch(self):
        payload = {
            "text": "Hello candidate, let us begin the system architecture round.",
            "interviewer_name": "Kabir"
        }
        response = self.client.post('/api/tts/generate/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('interviewer'), 'Kabir')
        self.assertEqual(data.get('bcp47'), 'en-IN')

    def test_compiler_execution(self):
        payload = {
            "code": "def add(a, b): return a + b\nprint(add(2, 3))",
            "language": "python",
            "test_cases": [{"input": "2, 3", "expected": "5"}]
        }
        response = self.client.post('/api/compiler/execute/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('5', data.get('stdout'))
        self.assertEqual(data.get('passed_tests'), 1)

    def test_session_start(self):
        payload = {
            "role": "Distributed Systems Engineer",
            "company": "Amazon",
            "track": "Tech",
            "level": "Senior SDE",
            "interviewer_name": "Charlotte",
            "interviewer_accent": "UK English (Standard)",
            "language": "python"
        }
        response = self.client.post('/api/sessions/start/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('session_id', data)
        self.assertEqual(len(data.get('questions', [])), 4)

    def test_dashboard_summary(self):
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('mean_evaluated_score', data)
        self.assertIn('performance_trends', data)
