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

    phonenumber = models.CharField(max_length= 15, unique=True,verbose_name='شماره همراه')
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True , verbose_name='ایمیل')
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="users"
    )

    first_name = models.CharField(max_length=150, blank=True , verbose_name='نام')
    last_name  = models.CharField(max_length=150, blank=True , verbose_name='نام خانوادگی')
    is_active = models.BooleanField(default=True , verbose_name='فعال')
    is_staff = models.BooleanField(default=False , verbose_name='کارمند')
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='ساخته شده در')
    updated_at = models.DateTimeField(auto_now=True , verbose_name='به روز رسانی شده در')
    
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
    
    class Meta:
        verbose_name='کاربر'
        verbose_name_plural ='کاربران'