from django.db import models
from django.contrib.auth.models import User
import uuid


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    sector = models.CharField(max_length=150, blank=True, default="Tech")
    focus = models.CharField(max_length=300, blank=True, default="")
    subroles = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sector})"


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=100, default="Tech")
    focus = models.CharField(max_length=300, blank=True, default="")
    levels = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} [{self.category}]"


class CatalogQuestion(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_key = models.CharField(max_length=120, unique=True)
    title = models.CharField(max_length=400)
    category = models.CharField(max_length=100, default="Coding")
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, default='Medium')
    prompt = models.TextField()
    starter_code = models.TextField(blank=True, default="")
    sample_solution = models.TextField(blank=True, default="")
    required_keywords = models.JSONField(default=list, blank=True)
    bonus_keywords = models.JSONField(default=list, blank=True)
    rubric_breakdown = models.JSONField(default=dict, blank=True)
    child_concept_groups = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.difficulty}] {self.question_key}: {self.title[:50]}"


class CodingTestCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(CatalogQuestion, related_name='test_cases', on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=False)
    timeout_seconds = models.FloatField(default=2.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Test for {self.question.question_key} (Hidden={self.is_hidden})"


class CompanyQuestionMapping(models.Model):
    """
    Stores company-specific LeetCode interview question mappings with frequency and timeframes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=200, db_index=True)
    question_slug = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=400)
    difficulty = models.CharField(max_length=50, default="Medium")
    frequency = models.FloatField(default=0.0)
    acceptance_rate = models.FloatField(default=0.0)
    time_window = models.CharField(max_length=50, default="All")
    topics = models.JSONField(default=list, blank=True)
    leetcode_url = models.URLField(max_length=500, blank=True, default="")
    catalog_question = models.ForeignKey(CatalogQuestion, null=True, blank=True, on_delete=models.SET_NULL, related_name="company_mappings")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['company_name', '-frequency']
        indexes = [
            models.Index(fields=['company_name', 'time_window']),
            models.Index(fields=['company_name', 'difficulty']),
            models.Index(fields=['question_slug']),
        ]

    def __str__(self):
        return f"{self.company_name} - {self.title} ({self.difficulty})"


class PhoneticGlossary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    misheard_token = models.CharField(max_length=200, unique=True)
    canonical_token = models.CharField(max_length=200)
    soundex_code = models.CharField(max_length=20, blank=True, default="")
    category = models.CharField(max_length=100, default="technical_term")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Phonetic Glossaries"

    def __str__(self):
        return f"'{self.misheard_token}' -> '{self.canonical_token}'"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='profile')
    name = models.CharField(max_length=150, default="Alex Morgan")
    email = models.EmailField(blank=True, default="alex.morgan@example.com")
    age = models.IntegerField(null=True, blank=True, default=26)
    target_role = models.CharField(max_length=200, default="Software Engineer")
    seniority_level = models.CharField(max_length=100, default="SDE 2")
    bio = models.TextField(blank=True, default="Passionate software engineer focused on distributed systems, high-throughput APIs, and reliable backend engineering.")
    skills = models.JSONField(default=list, blank=True)
    preferred_languages = models.JSONField(default=list, blank=True)
    dialect_preference = models.CharField(max_length=100, default="Neutral Dialect (Acoustic Equivalence)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.target_role})"


class InterviewSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=200, default="Software Engineer")
    company = models.CharField(max_length=200, blank=True, default="Google")
    track = models.CharField(max_length=100, default="Tech")
    seniority_level = models.CharField(max_length=100, default="SDE 2")
    interviewer_name = models.CharField(max_length=100, default="Kabir")
    interviewer_accent = models.CharField(max_length=150, default="IN English (North)")
    coding_language = models.CharField(max_length=50, default="python")
    status = models.CharField(max_length=50, default="active")
    
    # Quantitative Scores (0 - 100)
    overall_score = models.FloatField(default=0.0)
    score_technical_depth = models.FloatField(default=0.0)
    score_structural_logic = models.FloatField(default=0.0)
    score_speech_clarity = models.FloatField(default=0.0)
    score_body_language = models.FloatField(null=True, blank=True, default=None)

    # Rich AI Evaluation Breakdown
    feedback_summary = models.JSONField(default=dict, blank=True)
    concept_breakdown = models.JSONField(default=list, blank=True)
    code_evaluation = models.JSONField(default=dict, blank=True)
    telemetry_matrix = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Session {self.id} - {self.role} @ {self.company} ({self.status})"


class QuestionRecord(models.Model):
    session = models.ForeignKey(InterviewSession, related_name='questions', on_delete=models.CASCADE)
    question_index = models.IntegerField(default=0)
    title = models.CharField(max_length=300)
    text = models.TextField()
    expected_concepts = models.JSONField(default=list)
    starter_code = models.TextField(blank=True, default="")
    candidate_code = models.TextField(blank=True, default="")
    candidate_transcript = models.TextField(blank=True, default="")
    candidate_audio_path = models.CharField(max_length=500, blank=True, default="")
    score = models.FloatField(default=0.0)
    evaluation_details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question_index']

    def __str__(self):
        return f"{self.session.id} - Q{self.question_index + 1}: {self.title}"


class FollowUpDialogue(models.Model):
    """
    Stores dynamic follow-up dialogue exchanges between candidate and interviewer.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(InterviewSession, related_name='follow_up_dialogues', on_delete=models.CASCADE)
    question_index = models.IntegerField(default=0)
    candidate_initial_answer = models.TextField()
    probe_type = models.CharField(max_length=100, default="concept_clarification")  # concept_clarification, code_complexity, edge_case, architecture_tradeoff
    ai_followup_prompt = models.TextField()
    candidate_followup_answer = models.TextField(blank=True, default="")
    score_adjustment = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Follow-up for {self.session.id} Q{self.question_index + 1} ({self.probe_type})"


class CandidateRecording(models.Model):
    """
    Stores physical video and audio recording media paths for interview sessions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(InterviewSession, related_name='recordings', on_delete=models.CASCADE)
    question_index = models.IntegerField(null=True, blank=True)
    media_type = models.CharField(max_length=50, default="video")  # video, audio
    file_path = models.CharField(max_length=500)
    mime_type = models.CharField(max_length=100, default="video/webm")
    duration_seconds = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recording ({self.media_type}) for Session {self.session.id}"


class ResumeAudit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate_name = models.CharField(max_length=200, blank=True, default="")
    email = models.CharField(max_length=200, blank=True, default="")
    extracted_text = models.TextField(blank=True, default="")
    ats_score = models.FloatField(default=0.0)
    key_strengths = models.JSONField(default=list)
    skill_gaps = models.JSONField(default=list)
    extracted_skills = models.JSONField(default=list)
    tailored_questions = models.JSONField(default=list)
    raw_analysis = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume Audit {self.candidate_name or self.id} ({self.ats_score}/100)"


class AssessmentSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    track = models.CharField(max_length=150)
    score = models.FloatField(default=0.0)
    total_questions = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    details = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assessment {self.track}: {self.score}%"


class PrepPlanRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_role = models.CharField(max_length=200)
    target_company = models.CharField(max_length=200)
    duration_days = models.IntegerField(default=14)
    roadmap = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prep Plan: {self.target_role} ({self.duration_days} Days)"
class InterviewQuestion(models.Model):
    source_id = models.CharField(max_length=150, unique=True)

    technology = models.CharField(max_length=100, db_index=True)
    technology_name = models.CharField(max_length=150)

    difficulty = models.IntegerField(db_index=True)
    difficulty_label = models.CharField(max_length=50)

    question_type = models.CharField(max_length=50, db_index=True)

    prompt = models.TextField()
    answer = models.JSONField(default=dict)
    explanation = models.TextField(blank=True, default="")

    tags = models.JSONField(default=list, blank=True)
    source_metadata = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['technology', 'difficulty']

    def __str__(self):
        return f"{self.technology_name}: {self.source_id}"