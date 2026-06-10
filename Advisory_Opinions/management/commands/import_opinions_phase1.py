import json
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from django.utils import timezone

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

        client = MongoClient("mongodb://host.docker.internal:27017/")
        db = client["haqbindb"]
        collection = db["advisoryopinions"]

        self.stdout.write(self.style.SUCCESS("Connected to MongoDB. Initializing Lazy Loader..."))

        AdvisoryOpinion.objects.all().delete()

        mongo_cursor = collection.find().batch_size(5000)

        created_count = 0
        error_count = 0

        for doc in mongo_cursor:
            try:
                opinion = AdvisoryOpinion(
                    id=str(doc["_id"]),
                    base_content= doc.get("baseContent"),
                    main_content=doc.get("mainContent"),
                    summary=doc.get("summary"),
                    code=doc.get("code"),
                    main_source=doc.get("mainSource"),
                    date=doc.get("date"),
                    scrape_source=doc.get("scrapeSource"),
                    views=doc.get("views", 0),

                    judicial_sessions_json=sanitize_json(doc.get("judicialSessions")),
                    general_assembly_decisions_acj_json=sanitize_json(doc.get("generalAssemblyDecisionsACJ")),
                    bylaws_json=sanitize_json(doc.get("bylaws")),
                    regulations_json=sanitize_json(doc.get("regulations")),
                    procedures_json=sanitize_json(doc.get("procedures")),
                    instructions_json=sanitize_json(doc.get("instructions")),
                    unification_rulings_acj_json=sanitize_json(doc.get("unificationRulingsACJ")),

                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )

                opinion.save()
                created_count += 1

                laws = doc.get("relatedLaws") or []

                for item in laws:
                    law_id = item.get("_id")
                    relation_reason = RelatedLaws.ValidRelations.law

                    law = Law.objects.filter(id=str(law_id)).first()
                    if not law:
                        continue

                    obj, created= RelatedLaws.objects.get_or_create(
                        from_opinion=opinion,
                        to_law=law,
                        relation_reason=relation_reason,
                    )
                    if created:
                        pass

                articles = doc.get("relatedArticles") or []

                for item in articles:
                    law_id = item.get("_id")
                    relation_reason = RelatedLaws.ValidRelations.article

                    article = Law.objects.filter(id=str(law_id)).first()
                    if not article or article.type != Law.LegalType.article:
                        print(article.type)

                    obj, created= RelatedLaws.objects.get_or_create(
                        from_opinion=opinion,
                        to_law=article,
                        relation_reason=relation_reason,
                    )
                    if created:
                        pass    

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"Error on doc {doc.get('_id')}: {e}"))
                return

        client.close()
        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed. Created: {created_count}, Errors: {error_count}"
            )
        )