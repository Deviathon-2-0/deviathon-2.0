from django.urls import path
from api import views

urlpatterns = [
    # 0. API Overview & Health Check
    path('', views.api_root, name='api_root'),
    path('health', views.health_check, name='api_health_raw'),
    path('health/', views.health_check, name='api_health'),

    # 1. Authentication (Register, Login, Google OAuth, Me, Logout)
    path('auth/register', views.auth_register, name='auth_register_raw'),
    path('auth/register/', views.auth_register, name='auth_register'),
    path('auth/login', views.auth_login, name='auth_login_raw'),
    path('auth/login/', views.auth_login, name='auth_login'),
    path('auth/google', views.auth_google, name='auth_google_raw'),
    path('auth/google/', views.auth_google, name='auth_google'),
    path('auth/me', views.auth_me, name='auth_me_raw'),
    path('auth/me/', views.auth_me, name='auth_me'),
    path('auth/logout', views.auth_logout, name='auth_logout_raw'),
    path('auth/logout/', views.auth_logout, name='auth_logout'),

    # 2. Catalog & Roles
    path('roles', views.get_roles, name='api_roles_raw'),
    path('roles/', views.get_roles, name='api_roles'),
    path('companies', views.get_companies, name='api_companies_raw'),
    path('companies/', views.get_companies, name='api_companies'),
    path('companies/<str:company_id>/subroles', views.get_company_subroles, name='api_company_subroles_raw'),
    path('companies/<str:company_id>/subroles/', views.get_company_subroles, name='api_company_subroles'),

    # 3. Interviewers & Multilingual TTS / STT
    path('interviewers', views.get_interviewers, name='api_interviewers_raw'),
    path('interviewers/', views.get_interviewers, name='api_interviewers'),
    path('tts/generate', views.synthesize_tts, name='api_tts_generate_raw'),
    path('tts/generate/', views.synthesize_tts, name='api_tts_generate'),
    path('audio/tts', views.synthesize_tts, name='api_audio_tts_raw'),
    path('audio/tts/', views.synthesize_tts, name='api_audio_tts'),
    path('stt/transcribe', views.transcribe_stt, name='api_stt_transcribe_raw'),
    path('stt/transcribe/', views.transcribe_stt, name='api_stt_transcribe'),
    path('audio/stt', views.transcribe_stt, name='api_audio_stt_raw'),
    path('audio/stt/', views.transcribe_stt, name='api_audio_stt'),

    # 4. Dynamic Questions & Session Lifecycle
    path('questions', views.generate_questions_api, name='api_questions_raw'),
    path('questions/', views.generate_questions_api, name='api_questions'),
    path('interview/questions', views.generate_questions_api, name='api_interview_questions_raw'),
    path('interview/questions/', views.generate_questions_api, name='api_interview_questions'),
    path('sessions/start', views.start_interview_session, name='api_sessions_start_raw'),
    path('sessions/start/', views.start_interview_session, name='api_sessions_start'),
    path('sessions/evaluate', views.evaluate_session_pipeline, name='api_sessions_evaluate_raw'),
    path('sessions/evaluate/', views.evaluate_session_pipeline, name='api_sessions_evaluate'),
    path('sessions/<uuid:session_id>/submit', views.submit_interview_session, name='api_sessions_submit_raw'),
    path('sessions/<uuid:session_id>/submit/', views.submit_interview_session, name='api_sessions_submit'),
    path('sessions/<uuid:session_id>/report', views.get_session_report, name='api_sessions_report_raw'),
    path('sessions/<uuid:session_id>/report/', views.get_session_report, name='api_sessions_report'),
    path('sessions/<uuid:session_id>/telemetry', views.record_session_telemetry, name='api_session_telemetry_raw'),
    path('sessions/<uuid:session_id>/telemetry/', views.record_session_telemetry, name='api_session_telemetry'),

    # 5. Compiler & Code Execution Sandbox
    path('compiler/execute', views.execute_compiler_code, name='api_compiler_execute_raw'),
    path('compiler/execute/', views.execute_compiler_code, name='api_compiler_execute'),

    # 6. Resume Audit & ATS
    path('resume/analyze', views.analyze_resume, name='api_resume_analyze_raw'),
    path('resume/analyze/', views.analyze_resume, name='api_resume_analyze'),

    # 7. Assessments
    path('assessments/tracks', views.get_assessment_tracks, name='api_assessment_tracks_raw'),
    path('assessments/tracks/', views.get_assessment_tracks, name='api_assessment_tracks'),
    path('assessments/submit', views.submit_assessment, name='api_assessment_submit_raw'),
    path('assessments/submit/', views.submit_assessment, name='api_assessment_submit'),

    # 8. Prep Roadmap
    path('prep-plan/generate', views.generate_prep_plan, name='api_prep_plan_generate_raw'),
    path('prep-plan/generate/', views.generate_prep_plan, name='api_prep_plan_generate'),

    # 9. Dashboard & Profile
    path('dashboard/summary', views.get_dashboard_summary, name='api_dashboard_summary_raw'),
    path('dashboard/summary/', views.get_dashboard_summary, name='api_dashboard_summary'),
    path('profile', views.user_profile_endpoint, name='api_profile_raw'),
    path('profile/', views.user_profile_endpoint, name='api_profile'),
]
