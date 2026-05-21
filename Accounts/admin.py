from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = [
        'phonenumber',
        'first_name',
        'last_name'
        ]

    fieldsets = (
        (
            None,
            {
                'fields': ('phonenumber','email', 'first_name', 'surname')
            }
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (
            _('Important Dates'),{'fields':('last_login',)}
        )
    )
    readonly_fields = ['last_login']
    
    add_fieldsets =(
        (
            None,{
                'classes':('wide',),
                'fields':(
                    'phonenumber',
                    'email',
                    'password1',
                    'password2',
                    'first_name',
                    'is_active',
                    'is_staff',
                    'is_superuser',

                )
            }
        ),
    )

    
admin.site.register(get_user_model(), UserAdmin)
