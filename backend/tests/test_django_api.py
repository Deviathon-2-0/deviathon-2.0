import json
from django.test import TestCase, Client

class ImairaApiTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_root_endpoint(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'operational')
        self.assertIn('api_endpoints', data)

    def test_health_endpoints(self):
        for path in ['/health', '/health/', '/api/health', '/api/health/']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data.get('status'), 'ok')
            self.assertIn('database', data)

    def test_api_root_endpoint(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'online')
        self.assertIn('documentation', data)

    def test_auth_registration_and_login(self):
        # 1. Register new candidate
        reg_payload = {
            "email": "test.engineer@imaira.ai",
            "password": "SecurePassword123!",
            "name": "Test Engineer"
        }
        reg_res = self.client.post('/api/auth/register/', data=json.dumps(reg_payload), content_type='application/json')
        self.assertEqual(reg_res.status_code, 201)
        reg_data = reg_res.json()
        self.assertIn('token', reg_data)
        token = reg_data['token']

        # 2. Login with credentials
        login_payload = {
            "email": "test.engineer@imaira.ai",
            "password": "SecurePassword123!"
        }
        login_res = self.client.post('/api/auth/login/', data=json.dumps(login_payload), content_type='application/json')
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.json()
        self.assertEqual(login_data['user']['email'], 'test.engineer@imaira.ai')

        # 3. Access /auth/me/ with token
        me_res = self.client.get('/api/auth/me/', HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.json()
        self.assertEqual(me_data['user']['name'], 'Test Engineer')

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
        self.assertEqual(len(data['interviewers']), 6)
        names = [inv['name'] for inv in data['interviewers']]
        self.assertIn('Kabir', names)
        self.assertIn('Payal', names)
        self.assertIn('Charlotte', names)
        self.assertIn('John', names)
        self.assertIn('Sarah', names)
        self.assertIn('Kenji', names)

        # Verify distinct gender representation
        males = [inv for inv in data['interviewers'] if inv.get('gender') == 'male']
        females = [inv for inv in data['interviewers'] if inv.get('gender') == 'female']
        self.assertEqual(len(males), 3)
        self.assertEqual(len(females), 3)

    def test_tts_accent_dispatch(self):
        payload = {
            "text": "Hello candidate, let us begin the system architecture round.",
            "interviewer_name": "Kabir",
            "pacing": "1.15"
        }
        response = self.client.post('/api/tts/generate/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('interviewer'), 'Kabir')
        self.assertEqual(data.get('bcp47'), 'en-IN')
        self.assertIn('region', data)

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

    def test_session_lifecycle_and_telemetry(self):
        # 1. Start Session
        start_payload = {
            "role": "Distributed Systems Engineer",
            "company": "Amazon",
            "track": "Tech",
            "level": "Senior SDE",
            "interviewer_name": "Charlotte",
            "interviewer_accent": "UK English (Standard)",
            "language": "python"
        }
        start_res = self.client.post('/api/sessions/start/', data=json.dumps(start_payload), content_type='application/json')
        self.assertEqual(start_res.status_code, 200)
        session_id = start_res.json()['session_id']

        # 2. Record 3-signal candidate performance & integrity telemetry
        telemetry_payload = {
            "eye_focus_ratio": 86.5,
            "upright_posture_score": 91.0,
            "pitch_variance_hz": 19.4,
            "speech_cadence_wpm": 138,
            "reading_saccades_detected": 0,
            "lip_sync_mismatch_flags": 0,
            "integrity_status": "Verified (Organic)"
        }
        tel_res = self.client.post(f'/api/sessions/{session_id}/telemetry/', data=json.dumps(telemetry_payload), content_type='application/json')
        self.assertEqual(tel_res.status_code, 200)
        self.assertEqual(tel_res.json()['status'], 'recorded')

        # 3. Retrieve Session Report with telemetry
        rep_res = self.client.get(f'/api/sessions/{session_id}/report/')
        self.assertEqual(rep_res.status_code, 200)
        rep_data = rep_res.json()
        self.assertEqual(rep_data['telemetry_matrix']['integrity_status'], 'Verified (Organic)')

    def test_dashboard_summary_empty(self):
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('total_sessions_completed'), 0)
        self.assertEqual(data.get('recent_sessions'), [])
