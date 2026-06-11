import json
from django.core.management.base import BaseCommand
from pymongo import MongoClient

from Advisory_Opinions.models import AdvisoryOpinion, RelatedLaws
from Laws.models import Law

class Command(BaseCommand):
    help = "Import advisory opinions from local MongoDB using lazy loading"

    def handle(self, *args, **options):

        def sanitize_json(data):
            if data is None:
                return None
            try:
                return json.loads(json.dumps(data, default=str))
            except Exception:
                return None
            
        valid_categories = {choice[0] for choice in RelatedLaws.LegalTypes.choices}
        def clean_category(c):
            if not c: return None
            formatted = str(c).capitalize()
            return formatted if formatted in valid_categories else None

        
        client = MongoClient("mongodb://host.docker.internal:27017/")
        db = client["haqbindb"]
        collection = db["advisoryopinions"]

        self.stdout.write(self.style.SUCCESS("Connected to MongoDB. Initializing Lazy Loader..."))

        mongo_cursor = collection.find().batch_size(5000)
        created_count = 0
        error_count = 0
        
        for doc in mongo_cursor:
            
            laws = []
            laws.append(sanitize_json(doc.get("bylaws")))
            laws.append(sanitize_json(doc.get("regulations")))
            laws.append(sanitize_json(doc.get("procedures")))
            laws.append(sanitize_json(doc.get("instructions")))

            opinion = AdvisoryOpinion.objects.get(id=str(doc.get("_id")))
            
            for law in laws:
                if law:
                    try:
                        related_law= Law.objects.get(id=law[0].get('_id'))
                        relation_reason= clean_category(related_law.category)
                        if relation_reason:
                            RelatedLaws.objects.get_or_create(
                                from_opinion=opinion,
                                to_law=related_law,
                                relation_reason=relation_reason
                            )
                        else:
                            raise ValueError('wrong relation reason: {related_law.category}')

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(f"Error on doc {doc.get('_id')}: {e}"))
                        return
                else: continue

            created_count+=1
            
        client.close()
        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed. Created: {created_count}, Errors: {error_count}"
            )
        )