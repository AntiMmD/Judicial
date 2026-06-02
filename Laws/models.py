from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from bson import ObjectId

def generate_objectid():
    return str(ObjectId())


class Law(models.Model):
    class LegalType(models.TextChoices):
        law = 'Law', 'قانون'
        article = 'Article', 'ماده'
        note = 'Note', 'تبصره'

    id = models.CharField(
        primary_key=True,
        max_length=100,
        editable=False,
        default=generate_objectid,)
    
    slug = models.SlugField(
        max_length=255,
        null=True,
        blank=True,
        allow_unicode=True,
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    type = models.CharField(max_length=10, choices= LegalType.choices)

    # --- Textual Content ---
    title = models.TextField(blank=True, null=True)
    main_content = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    short_summary = models.TextField(blank=True, null=True)
    # max_length is set to 1000 chon dataset ride, fix later 
    approving_authority = models.CharField(max_length=1000, blank=True, null= True)

    # --- Metadata ---
    main_source = models.CharField(max_length=200, blank= True, null=True)
    date = models.CharField(max_length=20, blank=True, null= True)
    scrape_source = models.CharField(max_length=200, blank= True, null=True)

    # --- Technical/Categorical Fields ---
    """ 
    code yani shomare article va ya note. type = law code nadarad (Null).
    shomare article ba yek char mesl : 0,1,2,...,150,... neshan dade mishavad.
    shomare note ba char mesl: 0.1 yani tabsare aval yek tak made _
    _ 5.9 yani tabsare 9 made 5
    """
    code = models.CharField(max_length=700, blank=True, null=True)
    article_no = models.IntegerField(null=True, blank=True) # az fielde code be dast miad
    note_no = models.IntegerField(null=True, blank=True) # az fielde code be dast miad
    priority = models.IntegerField(blank=True, null=True)

    class Category(models.TextChoices):
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

    category = models.CharField(
        max_length=20,
        choices= Category.choices,
        default=None,
        null=True,
        blank=True,
    )

    # only type = law has this field, other types -> article_count = Null
    article_count = models.IntegerField(null=True, blank=True) 
    # only type = article has this field, other types -> notes_count = Null
    notes_count = models.IntegerField(null=True, blank=True)

    views = models.BigIntegerField(default=0)

    # --- Relationships ---
    """contains relatedLaws, relatedArticles and relatedNotes"""
    # This ManyToMany handles all related Laws, Articles, AND Notes
    related_items = models.ManyToManyField(
        'self', 
        through='LawRelationship', 
        symmetrical=False, 
        related_name='referenced_by',
        blank=True,
    )
    # should be cleaned with related_items later:
    bylaws_json = models.JSONField(null=True, blank=True)
    related_articles_json = models.JSONField(null=True, blank=True)
    related_laws_json = models.JSONField(null=True, blank=True)
    circulars_json = models.JSONField(null=True, blank=True)
    regulations_json = models.JSONField(null=True, blank=True)
    approvals_json = models.JSONField(null=True, blank=True)
    procedures_json = models.JSONField(null=True, blank=True)
    conventions_json = models.JSONField(null=True, blank=True)
    instructions_json = models.JSONField(null=True, blank=True)

    #--- Relations to other tables / fix later ---
    attachment_json = models.JSONField(null=True, blank=True)
    # add keywords table
    keywords_json = models.JSONField(null=True, blank=True)
    advisory_opinions_json = models.JSONField(null=True, blank=True)
    judicial_sessions_json = models.JSONField(null=True, blank=True)
    general_assembly_decisions_acj_json = models.JSONField(null=True, blank=True)
    advisory_opinions_acj_json = models.JSONField(null=True, blank=True)
    unification_rulings_acj_json = models.JSONField(null=True, blank=True)
    specialized_boards_rulings_acj_json = models.JSONField(null=True, blank=True)
    unification_rulings_sc_json = models.JSONField(null=True, blank=True)
    case_laws_and_decisions_json = models.JSONField(null=True, blank=True)

    # WTF ARE THESE FIELDS:
    breadcrumb_json=models.JSONField(null=True, blank=True)
    breadcrumbIds_json = models.JSONField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def clean(self):
        super().clean()
        if self.type == self.LegalType.law and self.code:
            raise ValidationError("Laws cannot have a code field.")     
        if self.type in [self.LegalType.article, self.LegalType.note] and not self.code:
            raise ValidationError(f"{self.type} must have a code.")
        
        if (self.type == self.LegalType.article or self.type == self.LegalType.note) and self.article_count is not None:
            raise ValidationError(f"{self.type} cannot have an article_count field.")

        
        if (self.type == self.LegalType.law or self.type == self.LegalType.note) and self.notes_count is not None:
            raise ValidationError(f"{self.type} cannot have a notes_count field.")
        
    def __str__(self):
        return f"{self.type}: {self.title[:30] if self.title else self.id}"
    
    def save(self, *args, **kwargs):
        # auto-generate slug if missing
        if not self.slug:
            title_slug = slugify(self.title[:120] or "", allow_unicode=True).strip("-")
            suffix = self.id
            if title_slug:
                self.slug = f"{title_slug}"
            else:
                self.slug = None

        self.full_clean()
        super().save(*args, **kwargs)



class LawRelationship(models.Model):
    # Who is pointing?
    from_law = models.ForeignKey(Law, on_delete=models.CASCADE, related_name='outgoing_rel')
    # Who is being pointed to?
    to_law = models.ForeignKey(Law, on_delete=models.CASCADE, related_name='incoming_rel')
    
    relation_type = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return f"{self.from_law_id} --({self.relation_type})--> {self.to_law_id}"
    
    class Meta:
        unique_together = ('from_law', 'to_law', 'relation_type')

    