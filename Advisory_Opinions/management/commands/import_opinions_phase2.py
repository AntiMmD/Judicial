import json
from django.core.management.base import BaseCommand
from pymongo import MongoClient

from Advisory_Opinions.models import AdvisoryOpinion


class Command(BaseCommand):
    help = "Import advisory opinions from local MongoDB using lazy loading"

    def handle(self, *args, **options):
        client = MongoClient("mongodb://host.docker.internal:27017/")
        db = client["haqbindb"]
        collection = db["advisoryopinions"]

        self.stdout.write(self.style.SUCCESS("Connected to MongoDB. Initializing Lazy Loader..."))

        mongo_cursor = collection.find().batch_size(5000)
        created_count = 0
        error_count = 0
        
        for doc in mongo_cursor:
            related_opinions = doc.get("advisoryOpinions") or []
            opinion = AdvisoryOpinion.objects.get(id=str(doc.get("_id")))

            for item in related_opinions:
                related_id = item.get("_id")

                try:
                    related = AdvisoryOpinion.objects.get(id=str(related_id))
                    opinion.related_opinions.add(related)

                except Exception as e:
                    print(related_id)
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f"Error on doc {doc.get('_id')}: {e}"))
                    return

            created_count+=1
            
        client.close()
        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed. Created: {created_count}, Errors: {error_count}"
            )
        )