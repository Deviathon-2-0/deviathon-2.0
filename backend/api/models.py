from django.db import models
import uuid

class UserProfile(models.Model):
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
    track = models.CharField(max_length=100, default="Tech") # Tech, Management, Intern, Engineering, Analyst, Custom, JD Based
    seniority_level = models.CharField(max_length=100, default="SDE 2")
    interviewer_name = models.CharField(max_length=100, default="Kabir")
    interviewer_accent = models.CharField(max_length=150, default="IN English (North)")
    coding_language = models.CharField(max_length=50, default="python")
    status = models.CharField(max_length=50, default="active") # active, completed
    
    # Quantitative Scores (0 - 100)
    overall_score = models.FloatField(default=0.0)
    score_technical_depth = models.FloatField(default=0.0)
    score_structural_logic = models.FloatField(default=0.0)
    score_speech_clarity = models.FloatField(default=0.0)
    score_body_language = models.FloatField(default=0.0)

    # Rich AI Evaluation Breakdown
    feedback_summary = models.JSONField(default=dict, blank=True)
    concept_breakdown = models.JSONField(default=list, blank=True)
    code_evaluation = models.JSONField(default=dict, blank=True)

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
