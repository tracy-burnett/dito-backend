from django.contrib import admin

# Register your models here.



from . import models


# @admin.register(models.Post)
# class AuthorAdmin(admin.ModelAdmin):
#     list_display = ('title', 'id', 'status', 'slug', 'author')
#     prepopulated_fields = {'slug': ('title',), }


admin.site.register(models.Audio)
admin.site.register(models.Language)
admin.site.register(models.Translation)
admin.site.register(models.Story)