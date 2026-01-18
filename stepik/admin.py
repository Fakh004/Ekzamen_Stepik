from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Module)
admin.site.register(Task)
admin.site.register(InputOutput)
admin.site.register(Submission)
