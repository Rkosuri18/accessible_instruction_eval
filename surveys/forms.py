# surveys/forms.py
from django import forms
from django.core.exceptions import ValidationError
import re

from .models import Question


_ALPHA_RE = re.compile(r"[A-Za-z]")


class EvaluationForm(forms.Form):
    def __init__(self, *args, questions: list[Question], **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = list(questions or [])

        for idx, q in enumerate(self.questions):
            # Rating (1–7) as a number input
            self.fields[f"rating_{q.id}"] = forms.IntegerField(
                label=f"Rating for {q.get_key_display()} (1–7)",
                min_value=1,
                max_value=7,
                widget=forms.NumberInput(
                    attrs={
                        "class": "rating-input",
                        "inputmode": "numeric",
                        "min": "1",
                        "max": "7",
                        "step": "1",
                        "placeholder": "Type 1–7",
                        "aria-label": f"Rating for {q.get_key_display()} from 1 to 7",
                        "aria-describedby": f"hint_{q.id}",
                        "pattern": "^[1-7]$",
                    }
                ),
                error_messages={
                    "required": "Please enter a rating from 1 to 7.",
                    "min_value": "Minimum rating is 1.",
                    "max_value": "Maximum rating is 7.",
                    "invalid": "Please enter a whole number from 1 to 7.",
                },
            )

            
            self.fields[f"reason_{q.id}"] = forms.CharField(
                label="Reason",
                required=True,
                widget=forms.Textarea(
                    attrs={
                        "rows": 2,
                        "aria-label": f"Reason for {q.get_key_display()} rating",
                    }
                ),
                error_messages={
                    "required": "Please explain why you chose this rating (at least two words).",
                },
            )

           
            self.fields[f"improve_{q.id}"] = forms.CharField(
                label="How to make it better",
                required=True,
                widget=forms.Textarea(
                    attrs={
                        "rows": 2,
                        "aria-label": f"Improvements for {q.get_key_display()}",
                    }
                ),
                error_messages={
                    "required": "Please suggest how these instructions could be improved (at least two words).",
                },
            )

    def _validate_free_text(self, value: str, label: str) -> None:
       
        if not value:
            raise ValidationError(f"{label} is required. Please enter at least two words.")

        text = value.strip()
        if not text:
            raise ValidationError(f"{label} is required. Please enter at least two words.")

        
        if not _ALPHA_RE.search(text):
            raise ValidationError(f"{label} should include letters, not just numbers or symbols.")

        
        words = [w for w in text.split() if _ALPHA_RE.search(w)]
        if len(words) < 2:
            raise ValidationError(f"{label} should be at least two words.")

    def clean(self):
        
        cleaned = super().clean()

        
        for q in self.questions:
            key = f"rating_{q.id}"
            if key in self.data and key not in cleaned:
                raw = (self.data.get(key) or "").strip()
                if raw.isdigit():
                    n = int(raw)
                    if 1 <= n <= 7:
                        cleaned[key] = n

        
        for q in self.questions:
            reason_key = f"reason_{q.id}"
            improve_key = f"improve_{q.id}"

            reason_val = cleaned.get(reason_key)
            improve_val = cleaned.get(improve_key)

            
            try:
                self._validate_free_text(reason_val, "Reason")
            except ValidationError as e:
                self.add_error(reason_key, e)

            
            try:
                self._validate_free_text(improve_val, "How to make it better")
            except ValidationError as e:
                self.add_error(improve_key, e)

        return cleaned


