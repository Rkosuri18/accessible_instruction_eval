from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from surveys.models import InstructionDoc

class Command(BaseCommand):
    help = "Load all PDFs from media/instructions as InstructionDoc entries"

    def add_arguments(self, parser):
        parser.add_argument("directory", nargs="?", default="media/instructions")

    def handle(self, *args, **opts):
        directory = Path(opts["directory"]).resolve()
        if not directory.exists():
            raise CommandError(f"Directory not found: {directory}")
        count = 0
        for p in directory.glob("*.pdf"):
            obj, created = InstructionDoc.objects.get_or_create(title=p.stem)
            if created or not obj.file:
                with p.open("rb") as fh:
                    obj.file.save(p.name, File(fh), save=True)
            obj.is_active = True
            obj.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Loaded {count} PDFs from {directory}"))
