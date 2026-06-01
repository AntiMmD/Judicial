import re

from django.core.management.base import BaseCommand
from django.db import transaction

from Laws.models import Law


ARTICLE_RE = re.compile(r"^\d+$")
NOTE_RE = re.compile(r"^(\d+)\.(\d+)$")


class Command(BaseCommand):
    help = "Backfill article_no/note_no from code for Article/Note rows (skips corrupted codes)."

    def add_arguments(self, parser):
        parser.add_argument("--chunk-size", type=int, default=5000)
        parser.add_argument(
            "--max-code-length",
            type=int,
            default=10,
            help="Skip rows where len(code) > this value (treat as corrupted).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and report counts but do not write updates.",
        )
        parser.add_argument(
            "--sample-unmatched",
            type=int,
            default=0,
            help="Print up to N examples of rows skipped due to unmatched code format.",
        )

    def handle(self, *args, **opts):
        chunk_size = opts["chunk_size"]
        max_len = opts["max_code_length"]
        dry_run = opts["dry_run"]
        sample_n = opts["sample_unmatched"]
        unmatched_samples = []

        qs = (
            Law.objects
            .only("id", "type", "code", "article_no", "note_no")
            .filter(type__in=["Article", "Note"])
            # .exclude(code__isnull=True)
            # .exclude(code__exact="")
        )

        total_seen = 0
        total_to_update = 0
        skipped_too_long = 0
        skipped_unmatched = 0

        batch = []

        def flush():
            nonlocal total_to_update, batch
            if not batch:
                return
            if dry_run:
                total_to_update += len(batch)
                batch = []
                return

            # bulk_update does one query per batch
            Law.objects.bulk_update(batch, ["article_no", "note_no"], batch_size=chunk_size)
            total_to_update += len(batch)
            batch = []

        # Iterate in a memory-safe way
        for obj in qs.iterator(chunk_size=chunk_size):
            total_seen += 1
            code = (obj.code or "").strip()

            if len(code) > max_len:
                skipped_too_long += 1
                continue

            new_article_no = None
            new_note_no = None

            if obj.type == "Article":
                if ARTICLE_RE.match(code):
                    new_article_no = int(code)
                    new_note_no = None
                else:
                    skipped_unmatched += 1
                    if sample_n and len(unmatched_samples) < sample_n:
                        unmatched_samples.append(
                            {"id": obj.id, "type": obj.type, "code": obj.code}
                        )
                    continue

            elif obj.type == "Note":
                m = NOTE_RE.match(code)
                if m:
                    new_article_no = int(m.group(1))
                    new_note_no = int(m.group(2))
                else:
                    skipped_unmatched += 1
                    continue

            # Only update if something actually changes (reduces writes)
            if obj.article_no != new_article_no or obj.note_no != new_note_no:
                obj.article_no = new_article_no
                obj.note_no = new_note_no
                batch.append(obj)

            if len(batch) >= chunk_size:
                flush()
                print('successful for {chunk_size} chunks')

        flush()

        self.stdout.write(self.style.SUCCESS("Backfill complete."))
        self.stdout.write(f"Seen: {total_seen}")
        self.stdout.write(f"Updated: {total_to_update}{' (dry-run)' if dry_run else ''}")
        self.stdout.write(f"Skipped (len(code)>{max_len}): {skipped_too_long}")
        self.stdout.write(f"Skipped (unmatched format): {skipped_unmatched}")
        if unmatched_samples:
            self.stdout.write("\nUnmatched samples:")
            for s in unmatched_samples:
                self.stdout.write(f"  id={s['id']} type={s['type']} code={s['code']!r}")