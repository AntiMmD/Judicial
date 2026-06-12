import json
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from Laws.models import Law
from django.utils import timezone


class Command(BaseCommand):
    help = "Import laws from local MongoDB using lazy loading"

    def handle(self, *args, **options):
        # 1. Establish Connection
        client = MongoClient("mongodb://host.docker.internal:27017/")
        db = client["haqbindb"]
        collection = db["laws"]

        self.stdout.write(self.style.SUCCESS('Connected to MongoDB. Initializing Lazy Loader...'))

        # Clear existing data
        self.stdout.write("Clearing existing Law records...")
        Law.objects.all().delete()

        mongo_cursor = collection.find().batch_size(5000)
        total = collection.count_documents({})
        
        created_count = 0
        error_count = 0

        # Helpers
        def map_type(t):
            if not t:return None 
            mapping = {"law": "Law", "article": "Article", "note": "Note"}
            return mapping.get(str(t).lower(), None)

        valid_legal_types = {choice[0] for choice in Law.LegalType.choices}
        def clean_legal_types(c):
            if not c: return None
            formatted = str(c).capitalize()
            return formatted if formatted in valid_legal_types else None

        def sanitize_json(data):
            if data is None:
                return None
            try:
                return json.loads(json.dumps(data, default=str))
            except:
                return None

        # 3. Iteration
        for doc in mongo_cursor:
            try:
                # Map MongoDB fields to Django Model
                law = Law(
                    id=str(doc["_id"]),
                    type=map_type(doc.get("type")),
                    
                    # Content
                    title=doc.get("title"),
                    main_content=doc.get("mainContent"),
                    summary=doc.get("summary"),
                    short_summary=doc.get("shortSummary"),
                    approving_authority=doc.get("approvingAuthority"),

                    # Metadata
                    main_source=doc.get("mainSource"),
                    date=doc.get("date"),
                    scrape_source=doc.get("scrapeSource"),

                    # Technical
                    code=doc.get("code"),
                    priority=doc.get("priority"),
                    legal_type=clean_legal_types(doc.get("category")),
                    article_count=doc.get("articlesCount"),
                    notes_count=doc.get("notesCount"),
                    views=doc.get("views", 0),

                    # JSON Fields (Sanitized)
                    attachment_json=sanitize_json(doc.get("attachment")),
                    keywords_json=sanitize_json(doc.get("keywords")),
                    advisory_opinions_json=sanitize_json(doc.get("advisoryOpinions")),
                    judicial_sessions_json=sanitize_json(doc.get("judicialSessions")),
                    general_assembly_decisions_acj_json=sanitize_json(doc.get("generalAssemblyDecisionsACJ")),
                    advisory_opinions_acj_json=sanitize_json(doc.get("advisoryOpinionsACJ")),
                    unification_rulings_acj_json=sanitize_json(doc.get("unificationRulingsACJ")),
                    specialized_boards_rulings_acj_json=sanitize_json(doc.get("specializedBoardsRulingsACJ")),
                    unification_rulings_sc_json=sanitize_json(doc.get("unificationRulingsSC")),
                    case_laws_and_decisions_json=sanitize_json(doc.get("caseLawsAndDecisions")),
                    breadcrumb_json=sanitize_json(doc.get("breadcrumb") if isinstance(doc.get("breadcrumb"), list) else None),
                    breadcrumbIds_json=sanitize_json(doc.get("breadcrumbIds") if isinstance(doc.get("breadcrumbIds"), list) else None),

                    # NEW: Mapping the relationship arrays to JSON fields
                    bylaws_json=sanitize_json(doc.get("bylaws")),
                    related_articles_json=sanitize_json(doc.get("relatedArticles")),
                    related_laws_json=sanitize_json(doc.get("relatedLaws")),
                    circulars_json=sanitize_json(doc.get("circulars")),
                    regulations_json=sanitize_json(doc.get("regulations")),
                    approvals_json=sanitize_json(doc.get("approvals")),
                    procedures_json=sanitize_json(doc.get("procedures")),
                    conventions_json=sanitize_json(doc.get("conventions")),
                    instructions_json=sanitize_json(doc.get("instructions")),

                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )

                law.save_base(raw=True)
                created_count += 1
                
                if created_count % 5000 == 0:
                    self.stdout.write(f"Successfully migrated: {created_count} / {total}...")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\n[ERROR] ID {doc.get('_id')}: {e}"))
                
                # --- CULPRIT DETECTOR ---
                for field in Law._meta.fields:
                    val = getattr(law, field.name)
                    # Check if it's a string field with a max_length limit
                    if isinstance(val, str) and hasattr(field, 'max_length') and field.max_length is not None:
                        if len(val) > field.max_length:
                            self.stdout.write(self.style.WARNING(
                                f"   🔎 CULPRIT FOUND: Field '{field.name}' has limit {field.max_length} but data length is {len(val)}"
                            ))
                            self.stdout.write(f"   📝 DATA: {val[:100]}...") # Print first 100 chars
                # -------------------------
                
                error_count += 1

        client.close()
        self.stdout.write(self.style.SUCCESS(
            f"\nPhase 1 Finished.\nCreated: {created_count}\nErrors: {error_count}"
        ))
