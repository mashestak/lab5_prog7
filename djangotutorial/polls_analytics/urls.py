from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.PollStatisticsAPIView.as_view(), name='poll_stats'),
    path('filter/', views.PollFilterSortAPIView.as_view(), name='poll_filter_sort'),
    path('graph/', views.PollGraphAPIView.as_view(), name='poll_graph'),
    path('export/', views.PollExportAPIView.as_view(), name='poll_export'),
    path('api/analytics/', include('polls_analytics.urls')),
]
