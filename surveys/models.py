from email.policy import default
from django.db import models
from django.core.validators import FileExtensionValidator
import mimetypes
import os


ALLOWED_EXTS = ("pdf", "mp4", "webm", "ogg")
VIDEO_EXTS = (".mp4", ".webm", ".ogg")
PDF_EXTS = (".pdf",)

def guess_mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path or "")
    return mime or "application/octet-stream"



class InstructionDoc(models.Model):
    title = models.CharField(max_length=200)
    
    file = models.FileField(
        upload_to="instructions/",
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTS)],
    )
    version = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        v = f" (v{self.version})" if self.version else ""
        return f"{self.title}{v}"

    
    @property
    def filename(self) -> str:
        return os.path.basename(self.file.name or "")

    @property
    def ext(self) -> str:
        return os.path.splitext(self.file.name or "")[1].lower()

    @property
    def mime_type(self) -> str:
        return guess_mime(self.file.name)

    @property
    def is_pdf(self) -> bool:
        return (self.ext in PDF_EXTS)

    @property
    def is_video(self) -> bool:
        return (self.ext in VIDEO_EXTS)

    @property
    def media_kind(self) -> str:
        
        if self.is_video:
            return "video"
        return "pdf"


class Question(models.Model):
    DIM_CHOICES = [
        ("sensory_conversion", "Sensory Conversion"),
        ("procedural_structure", "Procedural Structure"),
        ("action_specificity", "Action Specificity"),
        ("verification_recovery", "Verification Feedback & Recovery"),
        ("reference_clarity", "Reference Clarity"),
        ("personalization", "Personalization"),
        ("cognitive_load", "Cognitive Load"),
    ]
    key = models.CharField(max_length=64, choices=DIM_CHOICES, unique=True)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.get_key_display()}"


# surveys/models.py
from django.db import models

class EvaluationRun(models.Model):
    
    user_token = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="Anonymous cookie-based id for the participant."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    total_steps = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        ut = self.user_token or "anonymous"
        return f"Run #{self.pk} ({ut})"


class ResponseSession(models.Model):
    run = models.ForeignKey(
        EvaluationRun,
        on_delete=models.CASCADE,
        related_name="sessions",
        null=True,
        blank=True,
        help_text="Which evaluation run this session belongs to."
    )
    doc = models.ForeignKey(InstructionDoc, on_delete=models.CASCADE)
    user_token = models.CharField(max_length=64, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    consented = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.id} on {self.doc}"


class Answer(models.Model):
    session = models.ForeignKey(
        ResponseSession, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    rating_int = models.IntegerField()  # now from your text input 1..7 (validated in form)
    reason_text = models.TextField(blank=True)
    improvement_text = models.TextField(blank=True)

    class Meta:
        
        constraints = [
            models.UniqueConstraint(
                fields=["session", "question"],
                name="unique_answer_per_session_question",
            )
        ]

    def __str__(self):
        return f"Answer s{self.session_id}/q{self.question_id}={self.rating_int}"

class RunProgress(models.Model):
    user_token = models.CharField(max_length=64, db_index=True)
    run = models.ForeignKey(
        EvaluationRun,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="progress_rows"
    )
    resp_session_ids = models.JSONField()          
    current_step = models.PositiveIntegerField(default=1)   
    total_steps = models.PositiveIntegerField(default=0)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
