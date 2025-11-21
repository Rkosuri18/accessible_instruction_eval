from django.core.management.base import BaseCommand
from surveys.models import Question

DIMENSIONS = [
    ("sensory_conversion", "Sensory Conversion", "How effectively do the instructions convey perceptual or visual information in non-visual, accessible terms (touch, sound, smell, or functional equivalents)?"),
    ("procedural_structure", "Procedural Structure", "Are steps logically ordered, single action making it easy to interpret and follow?"),
    ("action_specificity", "Action Specificity", "Do the instructions give enough non-visual spatial/temporal detail to perform each step confidently?"),
    ("verification_recovery", "Verification Feedback & Recovery", "To what extent can a user confirm progress non-visually and recover from common errors using the given instructions?"),
    ("reference_clarity", "Reference Clarity", "Are objects and actions named consistently, with references that are clear without looking?"),
    ("personalization", "Personalization", "Do the instructions adapt to the user’s skill level or prior experiences?"),
    ("cognitive_load", "Cognitive Load", "How mentally demanding is it to interpret and remember each step?"),
]

class Command(BaseCommand):
    help = "Seed the 7 dimension questions"

    def handle(self, *args, **kwargs):
        Question.objects.all().delete()
        for i, (key, _label, text) in enumerate(DIMENSIONS, start=1):
            Question.objects.create(key=key, text=text, order=i, is_active=True)
        self.stdout.write(self.style.SUCCESS("Seeded 7 questions."))
