from django.contrib import admin
from .models import Antique, Wishlist, DailyPick

admin.site.register(Antique)
admin.site.register(Wishlist)

@admin.register(DailyPick)
class DailyPickAdmin(admin.ModelAdmin):
    list_display = ('date', 'created_by')
    filter_horizontal = ('picks',)  # makes picking multiple antiques easier