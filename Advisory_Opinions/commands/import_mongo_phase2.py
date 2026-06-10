import json
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from Laws.models import Law


def sanitize_json(data):
    if data is None: return None
    try: return json.loads(json.dumps(data, default=str))
    except: return None

class Command(BaseCommand):
    help = "Import parent-child relationships using Bulk Update"

    def handle(self, *args, **options):
    
        client = MongoClient("mongodb://host.docker.internal:27017/")
        db = client["haqbindb"]
        collection = db["laws"]

        self.stdout.write(self.style.SUCCESS('Starting Phase 2...'))

        mongo_cursor = collection.find().batch_size(10000)
        
        batch_to_update = []
        parent_count = 0
        error_count = 0
        BATCH_SIZE = 10000

        for doc in mongo_cursor:
            try:
                _id = sanitize_json(doc.get("_id"))
                parentId = sanitize_json(doc.get("parentId"))

                if not parentId:
                    continue

                # 1. Create a "dummy" object with the ID
                # This avoids calling Law.objects.get() (No SELECT query!)
                child_obj = Law(id=_id)
                child_obj.parent_id = parentId
                
                batch_to_update.append(child_obj)
                parent_count += 1

                # 2. When batch is full, push to Postgres
                if len(batch_to_update) >= BATCH_SIZE:
                    Law.objects.bulk_update(batch_to_update, ['parent'])
                    batch_to_update = [] # Clear memory
                    self.stdout.write(f"Updated {parent_count} relationships...")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing ID {doc.get('_id')}: {e}"))
                error_count += 1

        # 3. Final push for remaining records
        if batch_to_update:
            Law.objects.bulk_update(batch_to_update, ['parent'])

        client.close()
        self.stdout.write(self.style.SUCCESS(
            f"\nPhase 2 Finished.\nTotal Linked: {parent_count}\nErrors: {error_count}"
        ))
