from django.db import models
from django.urls import reverse


class FederalDistrict(models.Model):
    full_name = models.CharField(max_length=100, verbose_name='Федеральный округ')
    short_name = models.CharField(max_length=100, verbose_name='ФО')

    def __str__(self):
        return self.short_name

    class Meta:
        verbose_name_plural = "Федеральные округа"
        verbose_name = "Федеральный округ"
        ordering = ["full_name"]


class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name='Регион')
    federal_district = models.ForeignKey(FederalDistrict, on_delete=models.CASCADE, verbose_name='Федеральный округ')

    def __str__(self):
        return '{} ({})'.format(self.name, self.federal_district)

    class Meta:
        verbose_name_plural = "Регионы"
        verbose_name = "Регион"
        ordering = ["name"]



class Company(models.Model):
    short_name = models.CharField(max_length=100, verbose_name='Короткое название', unique=True)
    full_name = models.CharField(max_length=200, verbose_name='Полное название', unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион')
    is_vuz = models.BooleanField(default=True, verbose_name='Это вуз')

    class Meta:
        verbose_name_plural = "Вузы/Организации"
        verbose_name = "Вуз/Организация"
        ordering = ["full_name"]

    def __str__(self):
        return '{}, {}'.format(self.short_name, self.region)

    def get_absolute_url(self):
        return reverse('company-detail', args=[str(self.id)])

