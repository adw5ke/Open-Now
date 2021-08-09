from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Business)
admin.site.register(Forum)
admin.site.register(Discussion)
admin.site.register(Review)
admin.site.register(OpeningHours)
admin.site.register(Location)
admin.site.register(Search)