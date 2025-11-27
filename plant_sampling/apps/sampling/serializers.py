from rest_framework import serializers
from .models import *

# ==================== SAMPLING LOCATION SERIALIZER ====================

class SamplingLocationSerializer(serializers.ModelSerializer):
    """Serializer for SamplingLocation model"""
    created_at_local = serializers.SerializerMethodField()
    
    class Meta:
        model = SamplingLocation
        fields = ['location_id', 'location_data', 'created_at', 'created_at_local']
        read_only_fields = ['location_id', 'created_at', 'created_at_local']
    
    def get_created_at_local(self, obj):
        """Return created_at in local timezone format (UTC+8)"""
        if obj.created_at:
            from datetime import timedelta
            local_time = obj.created_at + timedelta(hours=8)
            return local_time.strftime('%Y-%m-%d %H:%M:%S (UTC+8)')
        return None
    
    def get_updated_at_local(self, obj):
        """Return updated_at in local timezone format (UTC+8)"""
        if obj.updated_at:
            from datetime import timedelta
            local_time = obj.updated_at + timedelta(hours=8)
            return local_time.strftime('%Y-%m-%d %H:%M:%S (UTC+8)')
        return None
    
    def validate_location_data(self, value):
        """Additional validation for location_data"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("location_data must be a JSON object")
        
        # Required keys validation
        required_keys = ['coordinates', 'region', 'country']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"location_data must contain '{key}'")
        
        return value


# ==================== ENVIRONMENTAL CONDITIONS SERIALIZER ====================

class EnvironmentalConditionsSerializer(serializers.ModelSerializer):
    """Serializer for EnvironmentalConditions model"""
    recorded_at_local = serializers.SerializerMethodField()
    
    class Meta:
        model = EnvironmentalConditions
        fields = ['condition_id', 'condition_data', 'recorded_at', 'recorded_at_local']
        read_only_fields = ['condition_id', 'recorded_at', 'recorded_at_local']
    
    def get_recorded_at_local(self, obj):
        """Return recorded_at in local timezone format (UTC+8)"""
        if obj.recorded_at:
            from datetime import timedelta
            local_time = obj.recorded_at + timedelta(hours=8)
            return local_time.strftime('%Y-%m-%d %H:%M:%S (UTC+8)')
        return None
    
    def validate_condition_data(self, value):
        """Additional validation for condition_data"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("condition_data must be a JSON object")
        
        # Required keys validation
        required_keys = ['soil_composition', 'temperature', 'humidity', 'altitude']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"condition_data must contain '{key}'")
        
        return value


# ==================== RESEARCHER INFO SERIALIZER ====================

class ResearcherInfoSerializer(serializers.ModelSerializer):
    """Serializer for ResearcherInfo model"""
    
    class Meta:
        model = ResearcherInfo
        fields = ['researcher_id', 'name', 'email', 'phone', 'affiliation', 'created_at']
        read_only_fields = ['researcher_id', 'created_at']


# ==================== SAMPLE RESEARCHERS SERIALIZER ====================

class SampleResearchersSerializer(serializers.ModelSerializer):
    """Serializer for SampleResearchers junction table"""
    researcher_name = serializers.CharField(source='researcher.name', read_only=True)
    researcher_email = serializers.EmailField(source='researcher.email', read_only=True)
    
    class Meta:
        model = SampleResearchers
        fields = ['id', 'sample', 'researcher', 'researcher_name', 'researcher_email', 'role', 'assigned_at']
        read_only_fields = ['id', 'assigned_at']


class SampleResearchersCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sample-researcher relationships"""
    
    class Meta:
        model = SampleResearchers
        fields = ['sample', 'researcher', 'role']


# ==================== GROWTH METRICS SERIALIZER ====================

class GrowthMetricsSerializer(serializers.ModelSerializer):
    """Serializer for GrowthMetrics model"""
    
    class Meta:
        model = GrowthMetrics
        fields = ['growth_id', 'sample', 'height', 'leaf_count', 'stem_diameter', 'health_status', 'measured_at']
        read_only_fields = ['growth_id', 'measured_at']


# ==================== PLANT SAMPLE SERIALIZERS ====================

class PlantSampleListSerializer(serializers.ModelSerializer):
    """Serializer for listing plant samples (basic info)"""
    species = serializers.SerializerMethodField()
    common_name = serializers.SerializerMethodField()
    sampling_date = serializers.SerializerMethodField()
    
    class Meta:
        model = PlantSample
        fields = ['sample_id', 'species', 'common_name', 'sampling_date', 'created_at', 'updated_at']
        read_only_fields = ['sample_id', 'created_at', 'updated_at']
    
    def get_species(self, obj):
        return obj.sample_detail.get('species', '')
    
    def get_common_name(self, obj):
        return obj.sample_detail.get('common_name', '')
    
    def get_sampling_date(self, obj):
        return obj.sample_detail.get('sampling_date', '')


class PlantSampleDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed plant sample with all related data"""
    location_data = SamplingLocationSerializer(source='location', read_only=True)
    condition_data = EnvironmentalConditionsSerializer(source='condition', read_only=True)
    researchers = serializers.SerializerMethodField()
    growth_measurements = GrowthMetricsSerializer(source='growth_metrics', many=True, read_only=True)
    status = serializers.SerializerMethodField()
    created_at_local = serializers.SerializerMethodField()
    updated_at_local = serializers.SerializerMethodField()
    
    class Meta:
        model = PlantSample
        fields = [
            'sample_id',
            'sample_detail',
            'location',
            'location_data',
            'condition',
            'condition_data',
            'researchers',
            'growth_measurements',
            'status',
            'created_at',
            'created_at_local',
            'updated_at',
            'updated_at_local'
        ]
        read_only_fields = ['sample_id', 'created_at', 'created_at_local', 'updated_at', 'updated_at_local']
    
    def get_researchers(self, obj):
        sample_researchers = SampleResearchers.objects.filter(sample=obj).select_related('researcher')
        return [{
            'researcher_id': sr.researcher.researcher_id,
            'name': sr.researcher.name,
            'email': sr.researcher.email,
            'role': sr.role
        } for sr in sample_researchers]
    
    def get_status(self, obj):
        """Return the status of the sample (active or deleted)"""
        return 'deleted' if obj.is_deleted else 'active'
    
    
    def get_created_at_local(self, obj):
        """Return created_at in local timezone format (UTC+8)"""
        if obj.created_at:
            from django.utils import timezone
            from datetime import timedelta
            # Convert to UTC+8 timezone by adding 8 hours
            local_time = obj.created_at + timedelta(hours=8)
            return local_time.strftime('%Y-%m-%d %H:%M:%S (UTC+8)')
        return None
    
    def get_updated_at_local(self, obj):
        """Return updated_at in local timezone format (UTC+8)"""
        if obj.updated_at:
            from django.utils import timezone
            from datetime import timedelta
            # Convert to UTC+8 timezone by adding 8 hours
            local_time = obj.updated_at + timedelta(hours=8)
            return local_time.strftime('%Y-%m-%d %H:%M:%S (UTC+8)')
        return None
    
    def validate_sample_detail(self, value):
        """Additional validation for sample_detail"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("sample_detail must be a JSON object")
        
        # Required keys validation (sampling_date is now required)
        required_keys = ['sampling_date', 'species', 'common_name']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"sample_detail must contain '{key}'")
        
        return value


class PlantSampleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating plant samples"""
    
    class Meta:
        model = PlantSample
        fields = ['sample_detail', 'location', 'condition']
    
    def validate_sample_detail(self, value):
        """Validation for sample_detail"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("sample_detail must be a JSON object")
        
        required_keys = ['sampling_date', 'species', 'common_name']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"sample_detail must contain '{key}'")
        
        return value


class PlantSampleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating plant samples"""
    
    class Meta:
        model = PlantSample
        fields = ['sample_detail', 'location', 'condition']
    
    def validate_sample_detail(self, value):
        """Validation for sample_detail"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("sample_detail must be a JSON object")
        
        required_keys = ['sampling_date', 'species', 'common_name']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"sample_detail must contain '{key}'")
        
        return value


# ==================== SAMPLE AUDIT LOG SERIALIZER ====================

class SampleAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for SampleAuditLog model"""
    
    class Meta:
        model = SampleAuditLog
        fields = ['log_id', 'sample_id', 'action', 'performed_at', 'details']
        read_only_fields = ['log_id', 'performed_at']
