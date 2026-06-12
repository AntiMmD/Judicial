from django.db import models
from django.utils.text import slugify

from bson import ObjectId

from Laws.models import Law

def generate_objectid():
    return str(ObjectId())

class AdvisoryOpinion(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=24,
        editable=False,
        default=generate_objectid,)
    
    slug = models.SlugField(
        max_length=255,
        null=True,
        blank=True,
        allow_unicode=True,
    )

    # --- Textual Content ---
    title= models.CharField(max_length=300, blank=True, null=True)
    base_content= models.TextField(blank=True, null=True)
    main_content = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    
    # wtf does this field mean?
    code = models.CharField(max_length=700, blank=True, null=True)

    # --- Metadata ---
    main_source = models.CharField(max_length=200, blank= True, null=True)
    date = models.CharField(max_length=20, blank=True, null= True)
    scrape_source = models.CharField(max_length=200, blank= True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    views = models.BigIntegerField(default=0)

    related_opinions= models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='referenced_by_opinions'
    )
    
    related_laws= models.ManyToManyField(
        Law,
        through='RelatedLaws',
        blank=True,
        related_name='related_opinions',
    )

    #json for now:
    instructions_json= models.JSONField(null=True, blank=True)
    unification_rulings_acj_json= models.JSONField(null=True, blank=True)
    judicial_sessions_json= models.JSONField(null=True, blank=True)
    regulations_json= models.JSONField(null=True, blank=True)
    general_assembly_decisions_acj_json= models.JSONField(null=True, blank=True)
    bylaws_json = models.JSONField(null=True, blank=True)
    procedures_json = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.summary:
            self.slug= slugify(self.summary[:60])
        elif self.base_content:
            self.slug = slugify(self.base_content[:60])
        elif self.main_content:
            self.slug= slugify(self.main_content[:60])
        else: self.slug= None

        super().save(*args, **kwargs)
        


class RelatedLaws(models.Model):

    class ValidRelations(models.TextChoices):
        law = 'Law', 'قانون'
        article = 'Article', 'ماده'

    class LegalTypes(models.TextChoices):
        law = 'Law'
        agreement = 'Agreement'
        approval = 'Approval'
        bylaw = 'Bylaw'
        charter = 'Charter'
        circular = 'Circular'
        convention = 'Convention'
        instruction = 'Instruction'
        procedure = 'Procedure'
        regulation = 'Regulation'
        statutes = 'Statutes'

    # Who is pointing?
    from_opinion = models.ForeignKey(
        AdvisoryOpinion,
        on_delete=models.CASCADE,)
    
    # Who is being pointed to?
    to_law = models.ForeignKey(
        Law,
        on_delete=models.CASCADE,)
    
    # if relation_type = law, then relatedLaws of an opinion has  relation_type = law
    relation_reason = models.CharField(
        max_length=30,
        choices=ValidRelations.choices + LegalTypes.choices,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return f"{self.from_opinion_id} --({self.relation_type})--> {self.to_law_id}"
    
    class Meta:
        unique_together = ('from_opinion', 'to_law', 'relation_reason')