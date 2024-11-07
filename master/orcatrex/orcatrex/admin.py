from django.contrib import admin
from orcatrex.models import Jobs, Slave


class SlaveAdmin(admin.ModelAdmin):
  pass


class JobsAdmin(admin.ModelAdmin):
  pass


admin.site.register(Slave, SlaveAdmin)
admin.site.register(Jobs, JobsAdmin)
