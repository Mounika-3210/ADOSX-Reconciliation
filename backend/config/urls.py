from django.urls import path
from reconcile.views import discrepancies, import_csv, orgs
urlpatterns = [
    path('api/discrepancies/', discrepancies),
    path('api/orgs/', orgs),
    path('api/import/', import_csv),
]
