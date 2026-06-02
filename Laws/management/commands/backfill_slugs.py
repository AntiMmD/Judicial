from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils.text import slugify

from Laws.models import Law


def build_slug(obj):
    title = (obj.title or "")[:50]
    title_slug = slugify(title, allow_unicode=True).strip("-")

    if title_slug:
        return f"{title_slug}"

    return None


class Command(BaseCommand):
    help = "Backfill missing slugs for Law rows."

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite slugs even if already set.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=5000,
            help="How many rows to process per batch.",
        )
        parser.add_argument(
            "--id-prefix-len",
            type=int,
            default=8,
            help="How many chars of id to append when title is present.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without writing to DB.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        overwrite = options["overwrite"]
        batch_size = options["batch_size"]
        id_prefix_len = options["id_prefix_len"]
        dry_run = options["dry_run"]

        qs = Law.objects.only("id", "title", "slug").order_by("id")

        if not overwrite:
            qs = qs.filter(Q(slug__isnull=True) | Q(slug=""))

        updated = 0
        skipped = 0
        to_update = []

        for obj in qs.iterator(chunk_size=batch_size):
            if not overwrite and obj.slug:
                skipped += 1
                continue

            candidate = build_slug(obj)
            if not candidate or obj.slug == candidate:
                skipped += 1
                continue

            if dry_run:
                # self.stdout.write(f"[DRY RUN] {obj.id}: {obj.slug!r} -> {candidate!r}")
                updated += 1
                continue

            obj.slug = candidate
            to_update.append(obj)

            if len(to_update) >= batch_size:
                Law.objects.bulk_update(objs= to_update, fields= ["slug"], batch_size=batch_size)
                updated += len(to_update)
                to_update.clear()

        if not dry_run and to_update:
            Law.objects.bulk_update(to_update, ["slug"], batch_size=batch_size)
            updated += len(to_update)

        self.stdout.write(
            self.style.SUCCESS(f"Done. updated={updated} skipped={skipped}")
        )
