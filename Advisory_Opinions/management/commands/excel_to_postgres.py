import pandas as pd
from django.core.management.base import BaseCommand
from Advisory_Opinions.models import AdvisoryOpinion


class Command(BaseCommand):
    help = "Import titles from Excel into AdvisoryOpinion"

    def handle(self, *args, **kwargs):
        df = pd.read_excel("/Judicial/nm_analyzed.xlsx")

        opinions_to_update = []

        for _, row in df.iterrows():
            title = None if pd.isna(row["عنوان اختصاصی"]) else row["عنوان اختصاصی"]

            opinions_to_update.append(
                AdvisoryOpinion(
                    id=row["_id"],
                    title=title,
                )
            )

        AdvisoryOpinion.objects.bulk_update(
            opinions_to_update,
            ["title"],
            batch_size=1000
        )

        self.stdout.write(self.style.SUCCESS("Import completed"))
