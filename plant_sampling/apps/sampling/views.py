from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from django.urls import reverse

from .models import *
from .serializers import *


# ==================== HOME VIEW ====================

def home(request):
    """Render the main interface"""
    return render(request, 'home.html')


# ==================== API ROOT ====================

@api_view(['GET'])
def api_root(request):
    """
    API Root - Shows all available endpoints
    """
    return Response({
        'message': 'Plant Sampling API',
        'endpoints': {
            'locations': {
                'list_create': request.build_absolute_uri('/api/locations/'),
                'detail': '/api/locations/{location_id}/',
            },
            'conditions': {
                'list_create': request.build_absolute_uri('/api/conditions/'),
                'detail': '/api/conditions/{condition_id}/',
            },
            'researchers': {
                'list_create': request.build_absolute_uri('/api/researchers/'),
                'detail': '/api/researchers/{researcher_id}/',
            },
            'samples': {
                'list': request.build_absolute_uri('/api/samples/'),
                'create': request.build_absolute_uri('/api/samples/create/'),
                'detail': '/api/samples/{sample_id}/',
                'update': '/api/samples/{sample_id}/update/',
                'delete': '/api/samples/{sample_id}/delete/',
                'growth_metrics': '/api/samples/{sample_id}/growth-metrics/',
                'audit_logs': '/api/samples/{sample_id}/audit-logs/',
            },
            'sample_researchers': {
                'list': request.build_absolute_uri('/api/sample-researchers/'),
                'create': request.build_absolute_uri('/api/sample-researchers/create/'),
                'detail': '/api/sample-researchers/{id}/',
            },
            'growth_metrics': {
                'list_create': request.build_absolute_uri('/api/growth-metrics/'),
                'detail': '/api/growth-metrics/{growth_id}/',
            },
            'audit_logs': {
                'list': request.build_absolute_uri('/api/audit-logs/'),
            }
        }
    })


# ==================== SAMPLING LOCATION VIEWS ====================

class SamplingLocationListCreateView(generics.ListCreateAPIView):
    """
    GET: List all sampling locations
    POST: Create a new sampling location
    """
    queryset = SamplingLocation.objects.all().order_by('-created_at')
    serializer_class = SamplingLocationSerializer


class SamplingLocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific sampling location
    PUT/PATCH: Update a sampling location
    DELETE: Delete a sampling location
    """
    queryset = SamplingLocation.objects.all()
    serializer_class = SamplingLocationSerializer
    lookup_field = 'location_id'


# ==================== ENVIRONMENTAL CONDITIONS VIEWS ====================

class EnvironmentalConditionsListCreateView(generics.ListCreateAPIView):
    """
    GET: List all environmental conditions
    POST: Create new environmental conditions
    """
    queryset = EnvironmentalConditions.objects.all().order_by('-recorded_at')
    serializer_class = EnvironmentalConditionsSerializer


class EnvironmentalConditionsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve specific environmental conditions
    PUT/PATCH: Update environmental conditions
    DELETE: Delete environmental conditions
    """
    queryset = EnvironmentalConditions.objects.all()
    serializer_class = EnvironmentalConditionsSerializer
    lookup_field = 'condition_id'


# ==================== RESEARCHER INFO VIEWS ====================

class ResearcherInfoListCreateView(generics.ListCreateAPIView):
    """
    GET: List all researchers
    POST: Create a new researcher
    """
    queryset = ResearcherInfo.objects.all().order_by('name')
    serializer_class = ResearcherInfoSerializer


class ResearcherInfoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific researcher
    PUT/PATCH: Update researcher info
    DELETE: Delete a researcher
    """
    queryset = ResearcherInfo.objects.all()
    serializer_class = ResearcherInfoSerializer
    lookup_field = 'researcher_id'


# ==================== PLANT SAMPLE VIEWS (MAIN CRUD) ====================

class PlantSampleListView(generics.ListAPIView):
    """
    GET: List all plant samples (basic info)
    """
    queryset = PlantSample.objects.filter(is_deleted=False).order_by('-created_at')
    serializer_class = PlantSampleListSerializer


class PlantSampleCreateView(APIView):
    """
    POST: Create a new plant sample
    Returns: Complete sample data in JSON format
    """
    
    def post(self, request):
        serializer = PlantSampleCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    sample = serializer.save()
                    
                    # Log the creation
                    SampleAuditLog.objects.create(
                        sample_id=sample.sample_id,
                        action='CREATED',
                        details={
                            'species': sample.sample_detail.get('species'),
                            'location_id': sample.location.location_id
                        }
                    )
                    
                    # Return detailed response
                    detail_serializer = PlantSampleDetailSerializer(sample)
                    return Response(
                        detail_serializer.data,
                        status=status.HTTP_201_CREATED
                    )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlantSampleDetailView(APIView):
    """
    GET: Retrieve plant sample by ID with all related data (location, conditions, researchers)
    DELETE: Soft delete plant sample by ID
    Returns: Complete sample data in JSON format
    """
    
    def get(self, request, sample_id):
        sample = get_object_or_404(PlantSample, sample_id=sample_id)
        
        # If sample is soft deleted, return only a deletion message
        if sample.is_deleted:
            return Response(
                {
                    'message': 'Sample deleted',
                    'sample_id': sample_id,
                    'status': 'deleted'
                },
                status=status.HTTP_200_OK
            )
        
        serializer = PlantSampleDetailSerializer(sample)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, sample_id):
        sample = get_object_or_404(PlantSample, sample_id=sample_id)
        
        # Check if sample is already deleted
        if sample.is_deleted:
            return Response(
                {
                    'message': 'Sample already deleted',
                    'sample_id': sample_id,
                    'status': 'deleted'
                },
                status=status.HTTP_200_OK
            )
        
        try:
            with transaction.atomic():
                species = sample.sample_detail.get('species', 'Unknown')
                
                # Log the deletion
                SampleAuditLog.objects.create(
                    sample_id=sample.sample_id,
                    action='DELETED',
                    details={'species': species}
                )
                
                sample.delete()
                
                return Response(
                    {
                        'message': f'Sample {sample_id} soft deleted successfully',
                        'deleted_sample': {
                            'sample_id': sample_id,
                            'species': species,
                            'status': 'deleted'
                        }
                    },
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PlantSampleUpdateView(APIView):
    """
    PUT/PATCH: Update plant sample by ID
    Returns: Updated sample data in JSON format
    """
    
    def put(self, request, sample_id):
        sample = get_object_or_404(PlantSample, sample_id=sample_id)
        
        if sample.is_deleted:
            return Response(
                {'error': f'Sample {sample_id} is deleted and cannot be updated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PlantSampleUpdateSerializer(sample, data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    old_detail = sample.sample_detail.copy()
                    updated_sample = serializer.save()
                    
                    # Log the update
                    SampleAuditLog.objects.create(
                        sample_id=updated_sample.sample_id,
                        action='UPDATED',
                        details={
                            'old_detail': old_detail,
                            'new_detail': updated_sample.sample_detail
                        }
                    )
                    
                    # Return detailed response
                    detail_serializer = PlantSampleDetailSerializer(updated_sample)
                    return Response(
                        detail_serializer.data,
                        status=status.HTTP_200_OK
                    )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, sample_id):
        sample = get_object_or_404(PlantSample, sample_id=sample_id)
        
        if sample.is_deleted:
            return Response(
                {'error': f'Sample {sample_id} is deleted and cannot be updated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PlantSampleUpdateSerializer(sample, data=request.data, partial=True)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    old_detail = sample.sample_detail.copy()
                    updated_sample = serializer.save()
                    
                    # Log the update
                    SampleAuditLog.objects.create(
                        sample_id=updated_sample.sample_id,
                        action='UPDATED',
                        details={
                            'old_detail': old_detail,
                            'new_detail': updated_sample.sample_detail
                        }
                    )
                    
                    # Return detailed response
                    detail_serializer = PlantSampleDetailSerializer(updated_sample)
                    return Response(
                        detail_serializer.data,
                        status=status.HTTP_200_OK
                    )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlantSampleHardDeleteView(APIView):
    """
    DELETE: Permanently delete plant sample and all related data from database
    This action CANNOT be undone and will remove all data permanently
    """
    
    def delete(self, request, sample_id):
        sample = get_object_or_404(PlantSample, sample_id=sample_id)
        
        try:
            with transaction.atomic():
                species = sample.sample_detail.get('species', 'Unknown')
                
                # Log the hard deletion before removing the data
                SampleAuditLog.objects.create(
                    sample_id=sample.sample_id,
                    action='HARD_DELETED',
                    details={
                        'species': species,
                        'warning': 'PERMANENT DELETION - All data removed from database'
                    }
                )
                
                # Perform hard delete (removes from database)
                sample.hard_delete()
                
                return Response(
                    {
                        'message': f'Sample {sample_id} permanently deleted from database',
                        'deleted_sample': {
                            'sample_id': sample_id,
                            'species': species,
                            'deletion_type': 'permanent'
                        },
                        'warning': 'This action cannot be undone. All data has been permanently removed.'
                    },
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==================== SAMPLE RESEARCHERS VIEWS ====================

class SampleResearchersListView(generics.ListAPIView):
    """
    GET: List all sample-researcher relationships
    """
    queryset = SampleResearchers.objects.all().select_related('sample', 'researcher')
    serializer_class = SampleResearchersSerializer


class SampleResearchersCreateView(APIView):
    """
    POST: Link a researcher to a sample
    """
    
    def post(self, request):
        serializer = SampleResearchersCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                relationship = serializer.save()
                response_serializer = SampleResearchersSerializer(relationship)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SampleResearchersDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific sample-researcher relationship
    PUT/PATCH: Update the relationship
    DELETE: Remove the relationship
    """
    queryset = SampleResearchers.objects.all()
    serializer_class = SampleResearchersSerializer
    lookup_field = 'id'


# ==================== GROWTH METRICS VIEWS ====================

class GrowthMetricsListCreateView(generics.ListCreateAPIView):
    """
    GET: List all growth metrics
    POST: Create new growth metrics
    """
    queryset = GrowthMetrics.objects.all().order_by('-measured_at')
    serializer_class = GrowthMetricsSerializer


class GrowthMetricsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve specific growth metrics
    PUT/PATCH: Update growth metrics
    DELETE: Delete growth metrics
    """
    queryset = GrowthMetrics.objects.all()
    serializer_class = GrowthMetricsSerializer
    lookup_field = 'growth_id'


class GrowthMetricsBySampleView(generics.ListAPIView):
    """
    GET: List all growth metrics for a specific sample
    """
    serializer_class = GrowthMetricsSerializer
    
    def get_queryset(self):
        sample_id = self.kwargs['sample_id']
        return GrowthMetrics.objects.filter(sample_id=sample_id).order_by('-measured_at')


class GrowthMetricsCreateForSampleView(APIView):
    """
    POST: Create new growth metrics for a specific sample
    Returns: Created growth metrics data
    """
    
    def post(self, request, sample_id):
        # Verify sample exists
        sample = get_object_or_404(PlantSample, sample_id=sample_id)
        
        # Add sample_id to the data
        data = request.data.copy()
        data['sample'] = sample_id
        
        serializer = GrowthMetricsSerializer(data=data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    growth_metrics = serializer.save()
                    
                    # Log the creation
                    SampleAuditLog.objects.create(
                        sample_id=sample_id,
                        action='GROWTH_METRICS_ADDED',
                        details={
                            'growth_id': growth_metrics.growth_id,
                            'height': float(growth_metrics.height) if growth_metrics.height else None,
                            'leaf_count': growth_metrics.leaf_count,
                            'stem_diameter': float(growth_metrics.stem_diameter) if growth_metrics.stem_diameter else None,
                            'health_status': growth_metrics.health_status
                        }
                    )
                    
                    return Response(
                        GrowthMetricsSerializer(growth_metrics).data,
                        status=status.HTTP_201_CREATED
                    )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== AUDIT LOGS VIEWS ====================

class SampleAuditLogListView(generics.ListAPIView):
    """
    GET: List all audit log entries
    """
    queryset = SampleAuditLog.objects.all().order_by('-performed_at')
    serializer_class = SampleAuditLogSerializer


class SampleAuditLogBySampleView(generics.ListAPIView):
    """
    GET: List audit log entries for a specific sample
    """
    serializer_class = SampleAuditLogSerializer
    
    def get_queryset(self):
        sample_id = self.kwargs['sample_id']
        return SampleAuditLog.objects.filter(sample_id=sample_id).order_by('-performed_at')
