from django.urls import path

from orcatrex.views import GetJobs, ResultGetter

urlpatterns = [path('get_jobs/', GetJobs.as_view()), path('get_result/', ResultGetter.as_view())]
