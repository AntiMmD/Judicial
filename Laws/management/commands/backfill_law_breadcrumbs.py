from django.core.management.base import BaseCommand
from Laws.models import Law, Breadcrumb


class Command(BaseCommand):
    help = "Migrate breadcrumb_json and breadcrumbIds_json into Law.breadcrumbs"

    def handle(self, *args, **options):
        linked_count = 0

        laws = Law.objects.only("id", "breadcrumb_json", "breadcrumbIds_json")

        for law in laws:
            breadcrumb_ids = []

            if isinstance(law.breadcrumb_json, list):
                for item in law.breadcrumb_json:
                    if not isinstance(item, dict):
                        print('not a dict!')
                        continue

                    b_id = item.get("_id")
                    title = item.get("title")

                    b_id = str(b_id)

                    Breadcrumb.objects.update_or_create(
                        id=b_id,
                        defaults={"title": title},
                    )

                    breadcrumb_ids.append(b_id)
            
            if isinstance(law.breadcrumbIds_json, list):
                for id in law.breadcrumbIds_json:

                    b_id = id

                    b_id = str(b_id)

                    breadcrumb_ids.append(b_id)

            if breadcrumb_ids:
                breadcrumbs = Breadcrumb.objects.filter(id__in=set(breadcrumb_ids))
                law.breadcrumbs.add(*breadcrumbs)
                linked_count += breadcrumbs.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Linked {linked_count} breadcrumbs to laws."
            )
        )
