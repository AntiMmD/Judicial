from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()

class Job(models.Model):

    occupation = models.CharField(max_length=225, null=True, blank=True, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.occupation is not None:
            self.occupation = self.occupation.strip().lower()

            if self.occupation == "":
                self.occupation = None

        super().save(*args, **kwargs)
    
