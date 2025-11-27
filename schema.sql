-- Enums for standardized values
CREATE TYPE site_type_enum AS ENUM ('forest', 'grassland', 'wetland', 'desert', 'agricultural', 'urban', 'coastal', 'mountain');
CREATE TYPE soil_type_enum AS ENUM ('clay', 'sandy', 'loamy', 'silty', 'peaty', 'chalky', 'saline');
CREATE TYPE health_status_enum AS ENUM ('excellent', 'good', 'fair', 'poor', 'critical');
CREATE TYPE researcher_role_enum AS ENUM ('lead_researcher', 'assistant_researcher', 'field_technician', 'data_analyst', 'supervisor');


-- TABLE: sampling_location

CREATE TABLE sampling_location (
    location_id SERIAL PRIMARY KEY,
    location_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Ensure location_data contains required keys
    CONSTRAINT check_location_data_keys CHECK (
        location_data ? 'coordinates' AND
        location_data ? 'region' AND
        location_data ? 'country' AND
        location_data->'coordinates' ? 'latitude' AND
        location_data->'coordinates' ? 'longitude'
    ),
    
    -- Validate latitude range (-90 to 90)
    CONSTRAINT check_latitude_range CHECK (
        (location_data->'coordinates'->>'latitude')::DECIMAL BETWEEN -90 AND 90
    ),
    
    -- Validate longitude range (-180 to 180)
    CONSTRAINT check_longitude_range CHECK (
        (location_data->'coordinates'->>'longitude')::DECIMAL BETWEEN -180 AND 180
    ),
    
    -- Validate site_type if provided
    CONSTRAINT check_site_type CHECK (
        NOT (location_data ? 'site_type') OR
        location_data->>'site_type' IN ('forest', 'grassland', 'wetland', 'desert', 'agricultural', 'urban', 'coastal', 'mountain')
    )
);

CREATE INDEX idx_location_region ON sampling_location ((location_data->>'region'));
CREATE INDEX idx_location_country ON sampling_location ((location_data->>'country'));
CREATE INDEX idx_location_coordinates ON sampling_location USING GIN (location_data);


-- TABLE: environmental_conditions

CREATE TABLE environmental_conditions (
    condition_id SERIAL PRIMARY KEY,
    condition_data JSONB NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Ensure condition_data contains required keys
    CONSTRAINT check_condition_data_keys CHECK (
        condition_data ? 'soil_composition' AND
        condition_data ? 'temperature' AND
        condition_data ? 'humidity' AND
        condition_data ? 'altitude' AND
        condition_data->'soil_composition' ? 'pH' AND
        condition_data->'soil_composition' ? 'nutrients' AND
        condition_data->'soil_composition' ? 'type'
    ),
    
    -- Validate pH range (0-14)
    CONSTRAINT check_ph_range CHECK (
        (condition_data->'soil_composition'->>'pH')::DECIMAL BETWEEN 0 AND 14
    ),
    
    -- Validate temperature range (-50°C to 60°C)
    CONSTRAINT check_temperature_range CHECK (
        (condition_data->>'temperature')::DECIMAL BETWEEN -50 AND 60
    ),
    
    -- Validate humidity percentage (0-100%)
    CONSTRAINT check_humidity_range CHECK (
        (condition_data->>'humidity')::DECIMAL BETWEEN 0 AND 100
    ),
    
    -- Validate altitude range (-500m to 9000m)
    CONSTRAINT check_altitude_range CHECK (
        (condition_data->>'altitude')::DECIMAL BETWEEN -500 AND 9000
    ),
    
    -- Validate soil type if provided
    CONSTRAINT check_soil_type CHECK (
        condition_data->'soil_composition'->>'type' IN ('clay', 'sandy', 'loamy', 'silty', 'peaty', 'chalky', 'saline')
    )
);

CREATE INDEX idx_condition_temperature ON environmental_conditions ((condition_data->>'temperature'));
CREATE INDEX idx_condition_data ON environmental_conditions USING GIN (condition_data);


-- TABLE: researcher_info

CREATE TABLE researcher_info (
    researcher_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    phone VARCHAR(50),
    affiliation VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Validate email format
    CONSTRAINT check_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    
    -- Ensure name is not empty
    CONSTRAINT check_name_not_empty CHECK (TRIM(name) != '')
);

CREATE INDEX idx_researcher_name ON researcher_info (name);
CREATE INDEX idx_researcher_email ON researcher_info (email);


-- TABLE: plant_sample

CREATE TABLE plant_sample (
    sample_id SERIAL PRIMARY KEY,
    sample_detail JSONB NOT NULL,
    location_id INTEGER NOT NULL,
    condition_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Ensure sample_detail contains required keys
    CONSTRAINT check_sample_detail_keys CHECK (
        sample_detail ? 'sampling_date' AND
        sample_detail ? 'species' AND
        sample_detail ? 'common_name'
    ),
    
    -- Validate sampling_date is not in the future
    CONSTRAINT check_sampling_date_not_future CHECK (
        (sample_detail->>'sampling_date')::DATE <= CURRENT_DATE
    ),
    
    -- Ensure species name is not empty
    CONSTRAINT check_species_not_empty CHECK (
        TRIM(sample_detail->>'species') != ''
    ),
    
    -- Foreign key constraints with cascade protection
    CONSTRAINT fk_sample_location FOREIGN KEY (location_id)
        REFERENCES sampling_location(location_id) ON DELETE RESTRICT,
    
    CONSTRAINT fk_sample_condition FOREIGN KEY (condition_id)
        REFERENCES environmental_conditions(condition_id) ON DELETE RESTRICT
);

CREATE INDEX idx_sample_species ON plant_sample ((sample_detail->>'species'));
CREATE INDEX idx_sample_date ON plant_sample ((sample_detail->>'sampling_date'));
CREATE INDEX idx_sample_location ON plant_sample (location_id);
CREATE INDEX idx_sample_condition ON plant_sample (condition_id);
CREATE INDEX idx_sample_detail ON plant_sample USING GIN (sample_detail);


-- TABLE: sample_researchers

CREATE TABLE sample_researchers (
    id SERIAL PRIMARY KEY,
    sample_id INTEGER NOT NULL,
    researcher_id INTEGER NOT NULL,
    role VARCHAR(100),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Ensure unique researcher per sample
    CONSTRAINT unique_sample_researcher UNIQUE (sample_id, researcher_id),
    
    -- Validate role if provided
    CONSTRAINT check_researcher_role CHECK (
        role IS NULL OR role IN ('lead_researcher', 'assistant_researcher', 'field_technician', 'data_analyst', 'supervisor')
    ),
    
    -- Foreign key constraints
    CONSTRAINT fk_sample_researchers_sample FOREIGN KEY (sample_id)
        REFERENCES plant_sample(sample_id) ON DELETE CASCADE,
    
    CONSTRAINT fk_sample_researchers_researcher FOREIGN KEY (researcher_id)
        REFERENCES researcher_info(researcher_id) ON DELETE CASCADE
);

CREATE INDEX idx_sample_researchers_sample ON sample_researchers (sample_id);
CREATE INDEX idx_sample_researchers_researcher ON sample_researchers (researcher_id);


-- TABLE: growth_metrics

CREATE TABLE growth_metrics (
    growth_id SERIAL PRIMARY KEY,
    sample_id INTEGER NOT NULL,
    height DECIMAL(10, 2),
    leaf_count INTEGER,
    stem_diameter DECIMAL(10, 2),
    health_status VARCHAR(50),
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Validate positive measurements
    CONSTRAINT check_height_positive CHECK (height IS NULL OR height >= 0),
    CONSTRAINT check_leaf_count_positive CHECK (leaf_count IS NULL OR leaf_count >= 0),
    CONSTRAINT check_stem_diameter_positive CHECK (stem_diameter IS NULL OR stem_diameter >= 0),
    
    -- Validate realistic ranges
    CONSTRAINT check_height_realistic CHECK (height IS NULL OR height <= 200), -- max 200m (tallest trees)
    CONSTRAINT check_leaf_count_realistic CHECK (leaf_count IS NULL OR leaf_count <= 100000),
    CONSTRAINT check_stem_diameter_realistic CHECK (stem_diameter IS NULL OR stem_diameter <= 50), -- max 50m diameter
    
    -- Validate health status
    CONSTRAINT check_health_status CHECK (
        health_status IS NULL OR health_status IN ('excellent', 'good', 'fair', 'poor', 'critical')
    ),
    
    -- Foreign key constraint
    CONSTRAINT fk_growth_metrics_sample FOREIGN KEY (sample_id)
        REFERENCES plant_sample(sample_id) ON DELETE CASCADE
);

CREATE INDEX idx_growth_metrics_sample ON growth_metrics (sample_id);
CREATE INDEX idx_growth_metrics_measured_at ON growth_metrics (measured_at);
CREATE INDEX idx_growth_metrics_health ON growth_metrics (health_status);


-- TRIGGERS

-- Trigger: Prevent deletion of location if samples exist
CREATE OR REPLACE FUNCTION prevent_location_deletion()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM plant_sample WHERE location_id = OLD.location_id) THEN
        RAISE EXCEPTION 'Cannot delete location: associated samples exist';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_location_deletion
    BEFORE DELETE ON sampling_location
    FOR EACH ROW
    EXECUTE FUNCTION prevent_location_deletion();

-- Trigger: Prevent deletion of condition if samples exist
CREATE OR REPLACE FUNCTION prevent_condition_deletion()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM plant_sample WHERE condition_id = OLD.condition_id) THEN
        RAISE EXCEPTION 'Cannot delete environmental condition: associated samples exist';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_condition_deletion
    BEFORE DELETE ON environmental_conditions
    FOR EACH ROW
    EXECUTE FUNCTION prevent_condition_deletion();

-- Trigger: Validate growth metric date is after sample date
CREATE OR REPLACE FUNCTION validate_growth_metric_date()
RETURNS TRIGGER AS $$
DECLARE
    sample_date DATE;
BEGIN
    SELECT (sample_detail->>'sampling_date')::DATE INTO sample_date
    FROM plant_sample WHERE sample_id = NEW.sample_id;
    
    IF NEW.measured_at::DATE < sample_date THEN
        RAISE EXCEPTION 'Growth metric date cannot be before sample collection date';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_growth_metric_date
    BEFORE INSERT OR UPDATE ON growth_metrics
    FOR EACH ROW
    EXECUTE FUNCTION validate_growth_metric_date();

-- Trigger: Log sample creation
CREATE TABLE IF NOT EXISTS sample_audit_log (
    log_id SERIAL PRIMARY KEY,
    sample_id INTEGER,
    action VARCHAR(50),
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);

CREATE OR REPLACE FUNCTION log_sample_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO sample_audit_log (sample_id, action, details)
        VALUES (NEW.sample_id, 'CREATED', jsonb_build_object(
            'species', NEW.sample_detail->>'species',
            'location_id', NEW.location_id
        ));
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO sample_audit_log (sample_id, action, details)
        VALUES (NEW.sample_id, 'UPDATED', jsonb_build_object(
            'old_detail', OLD.sample_detail,
            'new_detail', NEW.sample_detail
        ));
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO sample_audit_log (sample_id, action, details)
        VALUES (OLD.sample_id, 'DELETED', jsonb_build_object(
            'species', OLD.sample_detail->>'species'
        ));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_log_sample_changes
    AFTER INSERT OR UPDATE OR DELETE ON plant_sample
    FOR EACH ROW
    EXECUTE FUNCTION log_sample_changes();

-- Trigger: Auto-update timestamps
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update updated_at for plant_sample
CREATE OR REPLACE FUNCTION update_plant_sample_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_plant_sample_updated_at
    BEFORE UPDATE ON plant_sample
    FOR EACH ROW
    EXECUTE FUNCTION update_plant_sample_updated_at();


-- VIEWS

-- View: Sample summary with location and researcher info
CREATE OR REPLACE VIEW vw_sample_summary AS
SELECT 
    ps.sample_id,
    ps.sample_detail->>'species' AS species,
    ps.sample_detail->>'common_name' AS common_name,
    ps.sample_detail->>'sampling_date' AS sampling_date,
    sl.location_data->>'region' AS region,
    sl.location_data->>'country' AS country,
    ec.condition_data->>'temperature' AS temperature,
    STRING_AGG(ri.name, ', ') AS researchers,
    COUNT(gm.growth_id) AS growth_measurements
FROM plant_sample ps
LEFT JOIN sampling_location sl ON ps.location_id = sl.location_id
LEFT JOIN environmental_conditions ec ON ps.condition_id = ec.condition_id
LEFT JOIN sample_researchers sr ON ps.sample_id = sr.sample_id
LEFT JOIN researcher_info ri ON sr.researcher_id = ri.researcher_id
LEFT JOIN growth_metrics gm ON ps.sample_id = gm.sample_id
GROUP BY ps.sample_id, sl.location_id, ec.condition_id;

-- View: Researcher workload
CREATE OR REPLACE VIEW vw_researcher_workload AS
SELECT 
    ri.researcher_id,
    ri.name,
    ri.email,
    COUNT(DISTINCT sr.sample_id) AS total_samples,
    COUNT(DISTINCT CASE WHEN sr.role = 'lead_researcher' THEN sr.sample_id END) AS lead_samples
FROM researcher_info ri
LEFT JOIN sample_researchers sr ON ri.researcher_id = sr.researcher_id
GROUP BY ri.researcher_id;

-- Comments

COMMENT ON TABLE sampling_location IS 'Geographic locations where plant samples are collected';
COMMENT ON TABLE environmental_conditions IS 'Environmental parameters recorded during sampling';
COMMENT ON TABLE researcher_info IS 'Information about researchers involved in sampling';
COMMENT ON TABLE plant_sample IS 'Main table for plant specimen records';
COMMENT ON TABLE sample_researchers IS 'Junction table linking samples to researchers';
COMMENT ON TABLE growth_metrics IS 'Time-series data tracking plant growth';
COMMENT ON TABLE sample_audit_log IS 'Audit trail for sample modifications';

COMMENT ON COLUMN sampling_location.location_data IS 'JSON containing coordinates, region, country, site_type';
COMMENT ON COLUMN environmental_conditions.condition_data IS 'JSON containing soil_composition, temperature, humidity, altitude';
COMMENT ON COLUMN plant_sample.sample_detail IS 'JSON containing sampling_date, species, common_name, description';