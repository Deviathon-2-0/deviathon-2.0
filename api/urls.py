from django.urls import path
from api import views

urlpatterns = [
    # 1. Catalog & Roles
    path('roles/', views.get_roles, name='api_roles'),
    path('companies/', views.get_companies, name='api_companies'),
    path('companies/<str:company_id>/subroles/', views.get_company_subroles, name='api_company_subroles'),

    # 2. Interviewers & Multilingual TTS / STT
    path('interviewers/', views.get_interviewers, name='api_interviewers'),
    path('tts/generate/', views.synthesize_tts, name='api_tts_generate'),
    path('audio/tts/', views.synthesize_tts, name='api_audio_tts'),
    path('stt/transcribe/', views.transcribe_stt, name='api_stt_transcribe'),
    path('audio/stt/', views.transcribe_stt, name='api_audio_stt'),

    # 3. Dynamic Questions & Session Lifecycle
    path('questions/', views.generate_questions_api, name='api_questions'),
    path('sessions/start/', views.start_interview_session, name='api_sessions_start'),
    path('sessions/<uuid:session_id>/submit/', views.submit_interview_session, name='api_sessions_submit'),
    path('sessions/<uuid:session_id>/report/', views.get_session_report, name='api_sessions_report'),

    # 4. Compiler & Code Execution Sandbox
    path('compiler/execute/', views.execute_compiler_code, name='api_compiler_execute'),

    # 5. Resume Audit & ATS
    path('resume/analyze/', views.analyze_resume, name='api_resume_analyze'),

    # 6. Assessments
    path('assessments/tracks/', views.get_assessment_tracks, name='api_assessment_tracks'),
    path('assessments/submit/', views.submit_assessment, name='api_assessment_submit'),

    # 7. Prep Roadmap
    path('prep-plan/generate/', views.generate_prep_plan, name='api_prep_plan_generate'),

    # 8. Dashboard & Profile
    path('dashboard/summary/', views.get_dashboard_summary, name='api_dashboard_summary'),
    path('profile/', views.user_profile_endpoint, name='api_profile'),
]
