from django.urls import path
from orcatrex import views

urlpatterns = [path('send_job', views.GetJobs.as_view()), path('add_slave', views.SlaveAdder.as_view())]
