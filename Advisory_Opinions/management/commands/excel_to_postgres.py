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
            court_type= None if pd.isna(row["نوع دادگاه"]) else row["نوع دادگاه"]
            category= None if pd.isna(row["دسته‌بندی"]) else row["دسته‌بندی"]

            opinions_to_update.append(
                AdvisoryOpinion(
                    id=row["_id"],
                    title=title,
                    court_type=court_type,
                    category=category,
                )
            )

        AdvisoryOpinion.objects.bulk_update(
            opinions_to_update,
            ['title','court_type','category'],
            batch_size=1000
        )

        self.stdout.write(self.style.SUCCESS("Import completed"))

        categories = set()

        for _, row in df.iterrows():
            category = row["دسته‌بندی"]
            if pd.notna(category):
                categories.add(category)

        with open("opinions_category.txt", "w", encoding="utf-8") as file:
            for c in sorted(categories):
                file.write(f"{c}\n")