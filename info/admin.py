from django.contrib import admin
from .models import FederalDistrict, \
    Region, Company

from import_export.admin import ImportExportActionModelAdmin


class RegionInstanceInline(admin.TabularInline):
    model = Region


@admin.register(FederalDistrict)
class FederalDistrictAdmin(ImportExportActionModelAdmin):
    list_per_page = 15
    list_display = ('id', 'full_name', 'short_name')
    list_display_links = ('full_name',)
    fields = ['full_name', 'short_name', ]
    inlines = [RegionInstanceInline]
    ordering = ('id',)


# Define the admin class
@admin.register(Region)
class RegionAdmin(ImportExportActionModelAdmin):
    list_per_page = 15
    list_display = ('id', 'name', 'federal_district')
    list_display_links = ('name',)
    fields = ['name', 'federal_district']
    ordering = ('id',)


@admin.register(Company)
class CompanyAdmin(ImportExportActionModelAdmin):
    list_per_page = 15
    list_display = ('id', 'short_name', 'full_name', 'region', 'is_vuz')
    list_display_links = ('short_name',)
    fields = ['short_name', 'full_name', 'region', 'is_vuz']
    ordering = ('short_name',)
    search_fields = ['short_name', 'full_name', ]
