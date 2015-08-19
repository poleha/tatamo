from django.contrib import admin
from polls import models


#class PollAdmin(admin.ModelAdmin):
#    model = models.Poll
#    exclude = ['']

admin.site.register(models.Poll)
admin.site.register(models.Answer)
admin.site.register(models.Vote)
