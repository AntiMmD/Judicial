from django.db import models
from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from job.models import Job

class UserManager(BaseUserManager):
    def create_user(self,phonenumber, password=None,**extra_fields):
        if not phonenumber:
            raise ValueError("Users must have a phone number")

        email = extra_fields.pop('email', None)

        if email:
            email = self.normalize_email(email).lower()

        user = self.model(
            phonenumber=phonenumber,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using= self._db)

        return user

    def create_superuser(self,phonenumber , password,**extra_fields):
        user = self.create_user(phonenumber, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        AGENT = "agent", "مشاور حقوقی"
        User = "User", "کاربر"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        verbose_name="نقش کاربر",
        blank=True
    )

    phonenumber = models.CharField(max_length= 15, unique=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="users"
    )

    first_name = models.CharField(max_length=150, blank=True)
    last_name  = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'phonenumber'

    objects = UserManager()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f'{self.full_name}: {self.phonenumber}'
    
    def save(self, *args, **kwargs):
        self.phonenumber = self.phonenumber.strip()

        if self.phonenumber.startswith('+98'):
            self.phonenumber = '0' + self.phonenumber[3:]

        if self.email is not None:
            self.email = self.email.strip().lower()

            if self.email == "":
                self.email = None

        super().save(*args, **kwargs)