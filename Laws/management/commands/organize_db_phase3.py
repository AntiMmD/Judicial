import json
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from Laws.models import Law
import bson 

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

        doc = collection.find_one({"parentId": {"$exists":'true'}})
        parentId= doc.get("parentId")
        print(type(parentId))
