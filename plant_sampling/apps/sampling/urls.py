from django.urls import path
from . import views

app_name = 'sampling'

urlpatterns = [
    # ==================== API ROOT ====================
    path('', views.api_root, name='api-root'),
    
    # ==================== SAMPLING LOCATIONS ====================
    path('locations/', views.SamplingLocationListCreateView.as_view(), name='location-list-create'),
    path('locations/<int:location_id>/', views.SamplingLocationDetailView.as_view(), name='location-detail'),
    
    # ==================== ENVIRONMENTAL CONDITIONS ====================
    path('conditions/', views.EnvironmentalConditionsListCreateView.as_view(), name='condition-list-create'),
    path('conditions/<int:condition_id>/', views.EnvironmentalConditionsDetailView.as_view(), name='condition-detail'),
    
    # ==================== RESEARCHERS ====================
    path('researchers/', views.ResearcherInfoListCreateView.as_view(), name='researcher-list-create'),
    path('researchers/<int:researcher_id>/', views.ResearcherInfoDetailView.as_view(), name='researcher-detail'),
    
    # ==================== PLANT SAMPLES (MAIN CRUD) ====================
    path('samples/', views.PlantSampleListView.as_view(), name='sample-list'),
    path('samples/create/', views.PlantSampleCreateView.as_view(), name='sample-create'),
    path('samples/<int:sample_id>/', views.PlantSampleDetailView.as_view(), name='sample-detail'),
    path('samples/<int:sample_id>/update/', views.PlantSampleUpdateView.as_view(), name='sample-update'),
    path('samples/<int:sample_id>/hard-delete/', views.PlantSampleHardDeleteView.as_view(), name='sample-hard-delete'),
    
    # ==================== SAMPLE RESEARCHERS (LINKING) ====================
    path('sample-researchers/', views.SampleResearchersListView.as_view(), name='sample-researchers-list'),
    path('sample-researchers/create/', views.SampleResearchersCreateView.as_view(), name='sample-researchers-create'),
    path('sample-researchers/<int:id>/', views.SampleResearchersDetailView.as_view(), name='sample-researchers-detail'),
    
    # ==================== GROWTH METRICS ====================
    path('growth-metrics/', views.GrowthMetricsListCreateView.as_view(), name='growth-metrics-list-create'),
    path('growth-metrics/<int:growth_id>/', views.GrowthMetricsDetailView.as_view(), name='growth-metrics-detail'),
    path('samples/<int:sample_id>/growth-metrics/', views.GrowthMetricsBySampleView.as_view(), name='growth-metrics-by-sample'),
    path('samples/<int:sample_id>/growth-metrics/add/', views.GrowthMetricsCreateForSampleView.as_view(), name='growth-metrics-add-to-sample'),
    
    # ==================== AUDIT LOGS ====================
    path('audit-logs/', views.SampleAuditLogListView.as_view(), name='audit-log-list'),
    path('samples/<int:sample_id>/audit-logs/', views.SampleAuditLogBySampleView.as_view(), name='audit-log-by-sample'),
]
