from django.contrib import admin

# Register your models here.



from . import models




admin.site.register(models.Audio)
admin.site.register(models.Interpretations)
admin.site.register(models.Interpretation_History)
admin.site.register(models.Language)
admin.site.register(models.Translation)
admin.site.register(models.Story)