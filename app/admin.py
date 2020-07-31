from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import F

from userexpert.models import Expert, CustomGroup
from app.models import Direction, Application, RelationExpertApplication
from import_export.admin import ImportExportActionModelAdmin


@admin.register(Direction)
class DirectionAdmin(ImportExportActionModelAdmin):
    list_per_page = 15
    list_display = ('id', 'name', 'commission',)
    list_display_links = ('name',)
    fields = ['name', 'commission', ]
    search_fields = ['name', 'commission__name']
    ordering = ('name',)
    # TODO поиск не работает


@admin.register(Application)
class ApplicationAdmin(ImportExportActionModelAdmin):
    list_display = ('id', 'name', 'vuz')
    list_per_page = 15
    list_display_links = ('name',)
    # fields = ['name', 'vuz', 'link_archiv', 'experts']
    fieldsets = (
        (None, {'fields': ('name', 'vuz', 'link_archiv',)}),
        # ('Эксперты', {'fields': ('experts', )})
    )
    # filter_horizontal = ['experts']
    search_fields = ['name__name', 'vuz__full_name', 'vuz__short_name', ]
    ordering = ('name__name',)


from django import forms
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _


class RelationExpertGroupForm(forms.ModelForm):
    class Meta:
        model = RelationExpertApplication
        fields = ('expert', 'application')

        widgets = {'expert': forms.Select,
                   'application': forms.Select}

    def __init__(self, *args, **kwargs):
        super(RelationExpertGroupForm, self).__init__(*args, **kwargs)
        # self.fields['expert'].queryset = Expert.objects.filter(commission=F('commission'))


@admin.register(RelationExpertApplication)
class RelationExpertAppAdmin(ImportExportActionModelAdmin):
    form = RelationExpertGroupForm
    list_per_page = 15
    list_display = ('id', 'expert', 'application', 'common_commission', 'is_active')
    list_display_links = ('expert',)
    fields = ('expert', 'application', 'is_active')
    search_fields = ['expert__first_name', 'expert__last_name', 'expert__middle_name',
                     'application__name__name', 'application__vuz__full_name', 'application__vuz__short_name']
    ordering = ('id',)

    list_filter = ['is_active', 'common_commission', ]
