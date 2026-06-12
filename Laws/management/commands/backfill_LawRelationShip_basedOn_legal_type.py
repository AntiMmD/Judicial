import json
from django.core.management.base import BaseCommand
from pymongo import MongoClient

from Laws.models import Law, LawRelationship

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
            
        valid_legal_type = {choice[0] for choice in Law.LegalType.choices}
        def clean_legal_type(c):
            if not c: return None
            formatted = str(c).capitalize()
            return formatted if formatted in valid_legal_type else None

        
        client = MongoClient("mongodb://host.docker.internal:27017/")
        db = client["haqbindb"]
        collection = db["laws"]

        self.stdout.write(self.style.SUCCESS("Connected to MongoDB. Initializing Lazy Loader..."))

        mongo_cursor = collection.find().batch_size(5000)
        created_count = 0
        error_count = 0
        error_ids= []
        laws_for_creating = []

        # self.stdout.write(self.style.SUCCESS("deleting all the records before starting bulk creation... "))
        # LawRelationship.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS("attempting bulk creation... "))
        
        for doc in mongo_cursor:        
            related_laws = []
            
            # related_laws.append(sanitize_json(doc.get("bylaws")))
            # related_laws.append(sanitize_json(doc.get("regulations")))
            # related_laws.append(sanitize_json(doc.get("procedures")))
            # related_laws.append(sanitize_json(doc.get("instructions")))
            # related_laws.append(sanitize_json(doc.get("approvals")))
            # related_laws.append(sanitize_json(doc.get("circulars")))
            # related_laws.append(sanitize_json(doc.get("conventions")))
            # related_laws.append(sanitize_json(doc.get("regulation")))
            
            related_laws.append(sanitize_json(doc.get("relatedLaws")))
            related_laws.append(sanitize_json(doc.get("relatedArticles")))

            try:
                from_law = Law.objects.get(id=str(doc.get("_id")))
            except Law.DoesNotExist:
                raise ValueError(f"From law missing: {doc.get('_id')}")
            
            for related_mongo_law_list in related_laws:
                if related_mongo_law_list:
                    for related_mongo_law in related_mongo_law_list:
                        try:
                            to_law= Law.objects.get(id=str(related_mongo_law.get('_id')))

                        except Law.DoesNotExist:
                            error_count += 1
                            error_ids.append({
                                "from_law": str(doc.get("_id")),
                                "missing_to_law": str(related_mongo_law.get("_id")),
                                "title": related_mongo_law.get("title")
                            })
                            # raise ValueError(f"""
                            #     Related law missing:
                            #     {related_mongo_law.get('_id')} : {related_mongo_law.get('title')}
                            #     """
                            # )
                            continue
                        
                        title= related_mongo_law.get('title')
                        # relation_reason= clean_legal_type(to_law.legal_type)
                        relation_reason = to_law.type
                        if relation_reason:
                            laws_for_creating.append(LawRelationship(
                                from_law= from_law,
                                to_law= to_law,
                                relation_reason=relation_reason,
                                title= title
                            ))
                            continue
                        else:
                            raise ValueError(f'wrong relation reason: {to_law.legal_type}')

                else: continue

            try:
                if len(laws_for_creating) >= 5000:
                    LawRelationship.objects.bulk_create(
                        laws_for_creating,
                        batch_size=5000,
                        ignore_conflicts=True
                    )
                    created_count += len(laws_for_creating)

                    laws_for_creating.clear()


            except Exception as e:
                print(e)
        
        if laws_for_creating:
            LawRelationship.objects.bulk_create(
                laws_for_creating,
                batch_size=5000,
                ignore_conflicts=True
            )
            created_count += len(laws_for_creating)
            laws_for_creating.clear()
            
        client.close()
        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed. Created: {created_count}, Errors: {error_count}\n Error ids: {error_ids}"
            )
        )