from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


# ==================== SAMPLING LOCATION ====================

class SamplingLocation(models.Model):
    """Geographic locations where plant samples are collected"""
    
    SITE_TYPE_CHOICES = [
        ('forest', 'Forest'),
        ('grassland', 'Grassland'),
        ('wetland', 'Wetland'),
        ('desert', 'Desert'),
        ('agricultural', 'Agricultural'),
        ('urban', 'Urban'),
        ('coastal', 'Coastal'),
        ('mountain', 'Mountain'),
    ]
    
    location_id = models.AutoField(primary_key=True)
    location_data = models.JSONField(
        help_text="JSON containing coordinates, region, country, site_type"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sampling_location'
        indexes = [
            models.Index(fields=['location_data'], name='idx_location_coordinates'),
        ]
    
    def clean(self):
        """Validate location_data structure and values"""
        if not isinstance(self.location_data, dict):
            raise ValidationError("location_data must be a JSON object")
        
        # Check required keys
        required_keys = ['coordinates', 'region', 'country']
        for key in required_keys:
            if key not in self.location_data:
                raise ValidationError(f"location_data must contain '{key}'")
        
        # Check coordinates structure
        coords = self.location_data.get('coordinates', {})
        if not isinstance(coords, dict):
            raise ValidationError("coordinates must be a JSON object")
        
        if 'latitude' not in coords or 'longitude' not in coords:
            raise ValidationError("coordinates must contain 'latitude' and 'longitude'")
        
        # Validate latitude range (-90 to 90)
        try:
            lat = Decimal(str(coords['latitude']))
            if not (-90 <= lat <= 90):
                raise ValidationError("Latitude must be between -90 and 90")
        except (ValueError, TypeError, KeyError):
            raise ValidationError("Invalid latitude value")
        
        # Validate longitude range (-180 to 180)
        try:
            lon = Decimal(str(coords['longitude']))
            if not (-180 <= lon <= 180):
                raise ValidationError("Longitude must be between -180 and 180")
        except (ValueError, TypeError, KeyError):
            raise ValidationError("Invalid longitude value")
        
        # Validate site_type if provided
        if 'site_type' in self.location_data:
            valid_types = [choice[0] for choice in self.SITE_TYPE_CHOICES]
            if self.location_data['site_type'] not in valid_types:
                raise ValidationError(f"Invalid site_type. Must be one of: {valid_types}")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        region = self.location_data.get('region', 'Unknown')
        country = self.location_data.get('country', 'Unknown')
        return f"{region}, {country}"


# ==================== ENVIRONMENTAL CONDITIONS ====================

class EnvironmentalConditions(models.Model):
    """Environmental parameters recorded during sampling"""
    
    SOIL_TYPE_CHOICES = [
        ('clay', 'Clay'),
        ('sandy', 'Sandy'),
        ('loamy', 'Loamy'),
        ('silty', 'Silty'),
        ('peaty', 'Peaty'),
        ('chalky', 'Chalky'),
        ('saline', 'Saline'),
    ]
    
    condition_id = models.AutoField(primary_key=True)
    condition_data = models.JSONField(
        help_text="JSON containing soil_composition, temperature, humidity, altitude"
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'environmental_conditions'
        indexes = [
            models.Index(fields=['condition_data'], name='idx_condition_data'),
        ]
    
    def clean(self):
        """Validate condition_data structure and values"""
        if not isinstance(self.condition_data, dict):
            raise ValidationError("condition_data must be a JSON object")
        
        # Check required keys
        required_keys = ['soil_composition', 'temperature', 'humidity', 'altitude']
        for key in required_keys:
            if key not in self.condition_data:
                raise ValidationError(f"condition_data must contain '{key}'")
        
        # Check soil_composition structure
        soil = self.condition_data.get('soil_composition', {})
        if not isinstance(soil, dict):
            raise ValidationError("soil_composition must be a JSON object")
        
        soil_required = ['pH', 'nutrients', 'type']
        for key in soil_required:
            if key not in soil:
                raise ValidationError(f"soil_composition must contain '{key}'")
        
        # Validate pH range (0-14)
        try:
            ph = Decimal(str(soil['pH']))
            if not (0 <= ph <= 14):
                raise ValidationError("pH must be between 0 and 14")
        except (ValueError, TypeError, KeyError):
            raise ValidationError("Invalid pH value")
        
        # Validate temperature range (-50°C to 60°C)
        try:
            temp = Decimal(str(self.condition_data['temperature']))
            if not (-50 <= temp <= 60):
                raise ValidationError("Temperature must be between -50 and 60°C")
        except (ValueError, TypeError):
            raise ValidationError("Invalid temperature value")
        
        # Validate humidity percentage (0-100%)
        try:
            humidity = Decimal(str(self.condition_data['humidity']))
            if not (0 <= humidity <= 100):
                raise ValidationError("Humidity must be between 0 and 100%")
        except (ValueError, TypeError):
            raise ValidationError("Invalid humidity value")
        
        # Validate altitude range (-500m to 9000m)
        try:
            altitude = Decimal(str(self.condition_data['altitude']))
            if not (-500 <= altitude <= 9000):
                raise ValidationError("Altitude must be between -500 and 9000 meters")
        except (ValueError, TypeError):
            raise ValidationError("Invalid altitude value")
        
        # Validate soil type
        valid_types = [choice[0] for choice in self.SOIL_TYPE_CHOICES]
        if soil['type'] not in valid_types:
            raise ValidationError(f"Invalid soil type. Must be one of: {valid_types}")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        temp = self.condition_data.get('temperature', 'N/A')
        return f"Conditions (Temp: {temp}°C)"


# ==================== RESEARCHER INFO ====================

class ResearcherInfo(models.Model):
    """Information about researchers involved in sampling"""
    
    researcher_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, unique=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=50, blank=True, null=True)
    affiliation = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'researcher_info'
        indexes = [
            models.Index(fields=['name'], name='idx_researcher_name'),
            models.Index(fields=['email'], name='idx_researcher_email'),
        ]
    
    def clean(self):
        """Validate researcher data"""
        if not self.name or not self.name.strip():
            raise ValidationError("Name cannot be empty")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


# ==================== PLANT SAMPLE ====================

class PlantSample(models.Model):
    """Main table for plant specimen records"""
    
    sample_id = models.AutoField(primary_key=True)
    sample_detail = models.JSONField(
        help_text="JSON containing sampling_date, species, common_name, description"
    )
    location = models.ForeignKey(
        SamplingLocation,
        on_delete=models.RESTRICT,
        related_name='samples',
        db_column='location_id'
    )
    condition = models.ForeignKey(
        EnvironmentalConditions,
        on_delete=models.RESTRICT,
        related_name='samples',
        db_column='condition_id'
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'plant_sample'
        indexes = [
            models.Index(fields=['location'], name='idx_sample_location'),
            models.Index(fields=['condition'], name='idx_sample_condition'),
            models.Index(fields=['sample_detail'], name='idx_sample_detail'),
        ]
    
    def clean(self):
        """Validate sample_detail structure and values"""
        if not isinstance(self.sample_detail, dict):
            raise ValidationError("sample_detail must be a JSON object")
        
        # Check required keys
        required_keys = ['sampling_date', 'species', 'common_name']
        for key in required_keys:
            if key not in self.sample_detail:
                raise ValidationError(f"sample_detail must contain '{key}'")
        
        # Validate species name is not empty
        if not self.sample_detail['species'] or not str(self.sample_detail['species']).strip():
            raise ValidationError("Species name cannot be empty")
        
        # If sampling_date is provided, validate it
        if 'sampling_date' in self.sample_detail:
            try:
                from datetime import datetime, date
                sampling_date_str = self.sample_detail['sampling_date']
                sampling_date = datetime.strptime(sampling_date_str, '%Y-%m-%d').date()
                if sampling_date > date.today():
                    raise ValidationError("Sampling date cannot be in the future")
            except (ValueError, KeyError):
                raise ValidationError("Invalid sampling_date format. Use YYYY-MM-DD")
    
    def save(self, *args, **kwargs):
        # Auto-generate sampling_date if not provided
        if not self.sample_detail.get('sampling_date'):
            from datetime import date
            self.sample_detail['sampling_date'] = date.today().isoformat()
        self.full_clean()
        super().save(*args, **kwargs)
    
    def soft_delete(self):
        """Mark the sample as deleted without actually removing it"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def hard_delete(self):
        """Permanently remove the sample and all related data from the database"""
        # Delete related growth metrics first
        self.growth_metrics.all().delete()
        # Delete related sample-researcher links
        SampleResearchers.objects.filter(sample=self).delete()
        # Finally delete the sample itself
        super().delete()
    
    def delete(self, *args, **kwargs):
        """Override delete to perform soft delete instead"""
        self.soft_delete()
    
    def __str__(self):
        species = self.sample_detail.get('species', 'Unknown')
        return f"Sample {self.sample_id}: {species}"


# ==================== SAMPLE RESEARCHERS ====================

class SampleResearchers(models.Model):
    """Junction table linking samples to researchers"""
    
    ROLE_CHOICES = [
        ('lead_researcher', 'Lead Researcher'),
        ('assistant_researcher', 'Assistant Researcher'),
        ('field_technician', 'Field Technician'),
        ('data_analyst', 'Data Analyst'),
        ('supervisor', 'Supervisor'),
    ]
    
    id = models.AutoField(primary_key=True)
    sample = models.ForeignKey(
        PlantSample,
        on_delete=models.CASCADE,
        related_name='sample_researchers',
        db_column='sample_id'
    )
    researcher = models.ForeignKey(
        ResearcherInfo,
        on_delete=models.CASCADE,
        related_name='sample_assignments',
        db_column='researcher_id'
    )
    role = models.CharField(
        max_length=100,
        choices=ROLE_CHOICES,
        blank=True,
        null=True
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sample_researchers'
        unique_together = [['sample', 'researcher']]
        indexes = [
            models.Index(fields=['sample'], name='idx_sample_res_sample'),
            models.Index(fields=['researcher'], name='idx_sample_res_researcher'),
        ]
    
    def __str__(self):
        return f"{self.researcher.name} - Sample {self.sample.sample_id}"


# ==================== GROWTH METRICS ====================

class GrowthMetrics(models.Model):
    """Time-series data tracking plant growth"""
    
    HEALTH_STATUS_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    ]
    
    growth_id = models.AutoField(primary_key=True)
    sample = models.ForeignKey(
        PlantSample,
        on_delete=models.CASCADE,
        related_name='growth_metrics',
        db_column='sample_id'
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('200'))]
    )
    leaf_count = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100000)]
    )
    stem_diameter = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('50'))]
    )
    health_status = models.CharField(
        max_length=50,
        choices=HEALTH_STATUS_CHOICES,
        blank=True,
        null=True
    )
    measured_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'growth_metrics'
        indexes = [
            models.Index(fields=['sample'], name='idx_growth_metrics_sample'),
            models.Index(fields=['measured_at'], name='idx_growth_metrics_measured_at'),
            models.Index(fields=['health_status'], name='idx_growth_metrics_health'),
        ]
    
    def clean(self):
        """Validate growth metric date is after sample date"""
        if self.sample_id and self.measured_at:
            try:
                sample = PlantSample.objects.get(pk=self.sample_id)
                from datetime import datetime
                sample_date_str = sample.sample_detail.get('sampling_date')
                if sample_date_str:
                    sample_date = datetime.strptime(sample_date_str, '%Y-%m-%d').date()
                    
                    if self.measured_at.date() < sample_date:
                        raise ValidationError("Growth metric date cannot be before sample collection date")
            except (PlantSample.DoesNotExist, ValueError):
                pass
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Growth {self.growth_id} - Sample {self.sample.sample_id}"


# ==================== SAMPLE AUDIT LOG ====================

class SampleAuditLog(models.Model):
    """Audit trail for sample modifications"""
    
    log_id = models.AutoField(primary_key=True)
    sample_id = models.IntegerField(blank=True, null=True)
    action = models.CharField(max_length=50)
    performed_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True)
    
    class Meta:
        db_table = 'sample_audit_log'
    
    def __str__(self):
        return f"{self.action} - Sample {self.sample_id}"
