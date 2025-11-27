const API_BASE = '/api';

// Tab Navigation
function showTab(tabId) {
    // Hide all dropdowns
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.classList.remove('show');
    });
    document.querySelectorAll('.dropdown-toggle').forEach(btn => {
        btn.classList.remove('active');
    });

    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.nav-tab').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');
}

// Dropdown functionality
function toggleDropdown() {
    const dropdown = document.getElementById('addDataDropdown');
    const toggle = event.target.closest('.dropdown-toggle');

    // Close other dropdowns
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        if (menu !== dropdown) {
            menu.classList.remove('show');
        }
    });

    dropdown.classList.toggle('show');
    toggle.classList.toggle('active');
}

// Show specific add tab
function showAddTab(type) {
    // Hide all dropdowns
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.classList.remove('show');
    });

    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.nav-tab').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show the dropdown toggle as active and keep it active
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    dropdownToggle.classList.add('active');

    // Show the specific add tab
    const tabId = `add-${type}`;
    document.getElementById(tabId).classList.add('active');
}

// Show Response
function showResponse(elementId, data, isError = false) {
    const element = document.getElementById(elementId);
    element.className = 'response-box show ' + (isError ? 'error' : 'success');
    element.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
    element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Add Location
document.getElementById('locationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        location_data: {
            coordinates: {
                latitude: parseFloat(formData.get('latitude')),
                longitude: parseFloat(formData.get('longitude'))
            },
            region: formData.get('region'),
            country: formData.get('country')
        }
    };
    if (formData.get('site_type')) {
        data.location_data.site_type = formData.get('site_type');
    }
    
    try {
        const response = await fetch(`${API_BASE}/locations/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await response.json();
        showResponse('locationResponse', result, !response.ok);
        if (response.ok) e.target.reset();
    } catch (error) {
        showResponse('locationResponse', {error: error.message}, true);
    }
});

// Combined Plant Sample Creation
document.getElementById('combinedSubmitBtn').addEventListener('click', async () => {
    // Collect condition data
    let nutrients = {};
    try {
        const nutrientsValue = document.getElementById('condition_nutrients').value;
        nutrients = nutrientsValue ? JSON.parse(nutrientsValue) : {};
    } catch {
        nutrients = {};
    }

    const conditionData = {
        condition_data: {
            temperature: parseFloat(document.getElementById('condition_temperature').value),
            humidity: parseFloat(document.getElementById('condition_humidity').value),
            altitude: parseFloat(document.getElementById('condition_altitude').value),
            soil_composition: {
                pH: parseFloat(document.getElementById('condition_ph').value),
                type: document.getElementById('condition_soil_type').value,
                nutrients: nutrients
            }
        }
    };

    // Collect sample data
    const sampleData = {
        sample_detail: {
            species: document.getElementById('sample_species').value,
            common_name: document.getElementById('sample_common_name').value,
            sampling_date: document.getElementById('sample_date').value,
            description: document.getElementById('sample_description').value || ''
        },
        location: parseInt(document.getElementById('sample_location').value)
    };

    // Collect researcher link data
    const researcherId = document.getElementById('link_researcher').value;
    const researcherRole = document.getElementById('link_role').value;

    try {
        // Step 1: Create environmental conditions
        const conditionResponse = await fetch(`${API_BASE}/conditions/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(conditionData)
        });

        if (!conditionResponse.ok) {
            const errorResult = await conditionResponse.json();
            showResponse('combinedResponse', {error: 'Failed to create conditions', details: errorResult}, true);
            return;
        }

        const conditionResult = await conditionResponse.json();
        const conditionId = conditionResult.condition_id;

        // Step 2: Create plant sample with the condition ID
        sampleData.condition = conditionId;
        const sampleResponse = await fetch(`${API_BASE}/samples/create/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(sampleData)
        });

        if (!sampleResponse.ok) {
            const errorResult = await sampleResponse.json();
            showResponse('combinedResponse', {error: 'Failed to create sample', details: errorResult}, true);
            return;
        }

        const sampleResult = await sampleResponse.json();
        const sampleId = sampleResult.sample_id;

        // Step 3: Link researcher to sample (if researcher ID provided)
        let linkResult = null;
        if (researcherId) {
            const linkData = {
                sample: sampleId,
                researcher: parseInt(researcherId),
                role: researcherRole || null
            };

            const linkResponse = await fetch(`${API_BASE}/sample-researchers/create/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(linkData)
            });

            if (linkResponse.ok) {
                linkResult = await linkResponse.json();
            } else {
                // Don't fail the whole operation if linking fails
                console.warn('Failed to link researcher, but sample was created successfully');
            }
        }

        // Success response
        const successData = {
            message: 'Plant sample created successfully!',
            condition: conditionResult,
            sample: sampleResult,
            researcher_link: linkResult
        };

        showResponse('combinedResponse', successData, false);

        // Reset all form fields
        document.getElementById('condition_temperature').value = '';
        document.getElementById('condition_humidity').value = '';
        document.getElementById('condition_altitude').value = '';
        document.getElementById('condition_ph').value = '';
        document.getElementById('condition_soil_type').value = '';
        document.getElementById('condition_nutrients').value = '';
        document.getElementById('sample_species').value = '';
        document.getElementById('sample_common_name').value = '';
        document.getElementById('sample_location').value = '';
        document.getElementById('sample_description').value = '';
        document.getElementById('link_researcher').value = '';
        document.getElementById('link_role').value = '';

    } catch (error) {
        showResponse('combinedResponse', {error: error.message}, true);
    }
});

// Add Researcher
document.getElementById('researcherForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone') || null,
        affiliation: formData.get('affiliation') || null
    };
    
    try {
        const response = await fetch(`${API_BASE}/researchers/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await response.json();
        showResponse('researcherResponse', result, !response.ok);
        if (response.ok) e.target.reset();
    } catch (error) {
        showResponse('researcherResponse', {error: error.message}, true);
    }
});

// Query Sample
document.getElementById('queryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const sampleId = formData.get('sample_id');
    
    try {
        const response = await fetch(`${API_BASE}/samples/${sampleId}/`);
        const result = await response.json();
        
        // Show deleted samples in red
        const isDeleted = result.status === 'deleted';
        showResponse('queryResponse', result, !response.ok || isDeleted);
    } catch (error) {
        showResponse('queryResponse', {error: error.message}, true);
    }
});

// Update Type Dropdown Handler
document.getElementById('updateType').addEventListener('change', function(e) {
    const updateType = e.target.value;
    const fullSampleFields = document.getElementById('fullSampleFields');
    const growthMetricsFields = document.getElementById('growthMetricsFields');
    const loadSampleBtn = document.getElementById('loadSampleBtn');
    const updateSampleBtn = document.getElementById('updateSampleBtn');
    
    // Hide all fields first
    fullSampleFields.style.display = 'none';
    growthMetricsFields.style.display = 'none';
    
    // Hide buttons
    loadSampleBtn.style.display = 'none';
    updateSampleBtn.style.display = 'none';
    
    // Remove required attributes
    fullSampleFields.querySelectorAll('input[required], select[required]').forEach(field => {
        field.removeAttribute('required');
    });
    growthMetricsFields.querySelectorAll('input[required], select[required]').forEach(field => {
        field.removeAttribute('required');
    });
    
    // Show selected fields and buttons
    if (updateType === 'full_sample') {
        fullSampleFields.style.display = 'block';
        loadSampleBtn.style.display = 'inline-block';
    } else if (updateType === 'growth_metrics') {
        growthMetricsFields.style.display = 'block';
        loadSampleBtn.style.display = 'inline-block';
    }
});

// Load Sample Button Handler
document.getElementById('loadSampleBtn').addEventListener('click', async () => {
    const sampleId = document.getElementById('updateForm').elements['sample_id'].value;
    const updateType = document.getElementById('updateType').value;
    
    if (!sampleId) {
        showResponse('updateResponse', {error: 'Please enter a Sample ID'}, true);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/samples/${sampleId}/`);
        const result = await response.json();
        
        if (!response.ok) {
            showResponse('updateResponse', result, true);
            return;
        }
        
        // Check if sample is deleted
        if (result.status === 'deleted') {
            showResponse('updateResponse', {error: 'Cannot update a deleted sample'}, true);
            return;
        }
        
        // Populate form fields based on update type
        if (updateType === 'full_sample') {
            // Populate sample fields
            document.getElementById('update_sample_species').value = result.sample_detail.species || '';
            document.getElementById('update_sample_common_name').value = result.sample_detail.common_name || '';
            document.getElementById('update_sample_date').value = result.sample_detail.sampling_date || '';
            document.getElementById('update_sample_location').value = result.location || '';
            document.getElementById('update_sample_description').value = result.sample_detail.description || '';
            
            // Populate condition fields
            if (result.condition_data && result.condition_data.condition_data) {
                const conditionData = result.condition_data.condition_data;
                document.getElementById('update_condition_temperature').value = conditionData.temperature || '';
                document.getElementById('update_condition_humidity').value = conditionData.humidity || '';
                document.getElementById('update_condition_altitude').value = conditionData.altitude || '';
                document.getElementById('update_condition_ph').value = conditionData.soil_composition?.pH || '';
                document.getElementById('update_condition_soil_type').value = conditionData.soil_composition?.type || '';
                document.getElementById('update_condition_nutrients').value = conditionData.soil_composition?.nutrients ? JSON.stringify(conditionData.soil_composition.nutrients, null, 2) : '';
            }
            
            // Populate researcher link fields
            if (result.researchers && result.researchers.length > 0) {
                const researcher = result.researchers[0]; // Take first researcher
                document.getElementById('update_link_researcher').value = researcher.researcher_id || '';
                document.getElementById('update_link_role').value = researcher.role || '';
            }
        } else if (updateType === 'growth_metrics') {
            // Populate growth metrics fields if they exist
            if (result.growth_metrics) {
                document.querySelector('input[name="height"]').value = result.growth_metrics.height || '';
                document.querySelector('input[name="leaf_count"]').value = result.growth_metrics.leaf_count || '';
                document.querySelector('input[name="stem_diameter"]').value = result.growth_metrics.stem_diameter || '';
                document.querySelector('select[name="health_status"]').value = result.growth_metrics.health_status || '';
            }
        }
        
        // Show update button
        document.getElementById('updateSampleBtn').style.display = 'inline-block';
        
        showResponse('updateResponse', {message: 'Sample data loaded successfully. Make your changes and click Update.'}, false);
        
    } catch (error) {
        showResponse('updateResponse', {error: error.message}, true);
    }
});

// Update Sample Form Submission
document.getElementById('updateForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const sampleId = formData.get('sample_id');
    const updateType = formData.get('update_type');
    
    let data = {};
    let endpoint = '';
    let method = 'PUT';
    
    if (updateType === 'full_sample') {
        // Collect condition data
        let nutrients = {};
        try {
            const nutrientsValue = document.getElementById('update_condition_nutrients').value;
            nutrients = nutrientsValue ? JSON.parse(nutrientsValue) : {};
        } catch {
            nutrients = {};
        }

        const conditionData = {
            condition_data: {
                temperature: parseFloat(document.getElementById('update_condition_temperature').value),
                humidity: parseFloat(document.getElementById('update_condition_humidity').value),
                altitude: parseFloat(document.getElementById('update_condition_altitude').value),
                soil_composition: {
                    pH: parseFloat(document.getElementById('update_condition_ph').value),
                    type: document.getElementById('update_condition_soil_type').value,
                    nutrients: nutrients
                }
            }
        };

        // Collect sample data
        const sampleData = {
            sample_detail: {
                species: document.getElementById('update_sample_species').value,
                common_name: document.getElementById('update_sample_common_name').value,
                sampling_date: document.getElementById('update_sample_date').value,
                description: document.getElementById('update_sample_description').value || ''
            },
            location: parseInt(document.getElementById('update_sample_location').value)
        };

        // Collect researcher link data
        const researcherId = document.getElementById('update_link_researcher').value;
        const researcherRole = document.getElementById('update_link_role').value;

        try {
            // Step 1: Create new environmental conditions
            const conditionResponse = await fetch(`${API_BASE}/conditions/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(conditionData)
            });

            if (!conditionResponse.ok) {
                const errorResult = await conditionResponse.json();
                showResponse('updateResponse', {error: 'Failed to update conditions', details: errorResult}, true);
                return;
            }

            const conditionResult = await conditionResponse.json();
            const conditionId = conditionResult.condition_id;

            // Step 2: Update plant sample with the new condition ID
            sampleData.condition = conditionId;
            const sampleResponse = await fetch(`${API_BASE}/samples/${sampleId}/update/`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(sampleData)
            });

            if (!sampleResponse.ok) {
                const errorResult = await sampleResponse.json();
                showResponse('updateResponse', {error: 'Failed to update sample', details: errorResult}, true);
                return;
            }

            const sampleResult = await sampleResponse.json();

            // Step 3: Update researcher link (if researcher ID provided)
            let linkResult = null;
            if (researcherId) {
                const linkData = {
                    sample: parseInt(sampleId),
                    researcher: parseInt(researcherId),
                    role: researcherRole || null
                };

                // First, try to find existing link for this sample
                try {
                    const existingLinksResponse = await fetch(`${API_BASE}/sample-researchers/`);
                    if (existingLinksResponse.ok) {
                        const existingLinks = await existingLinksResponse.json();
                        const existingLink = existingLinks.find(link => link.sample === parseInt(sampleId));
                        
                        if (existingLink) {
                            // Update existing link
                            const updateResponse = await fetch(`${API_BASE}/sample-researchers/${existingLink.id}/`, {
                                method: 'PUT',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify(linkData)
                            });
                            if (updateResponse.ok) {
                                linkResult = await updateResponse.json();
                            }
                        } else {
                            // Create new link
                            const createResponse = await fetch(`${API_BASE}/sample-researchers/create/`, {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify(linkData)
                            });
                            if (createResponse.ok) {
                                linkResult = await createResponse.json();
                            }
                        }
                    }
                } catch (linkError) {
                    console.warn('Failed to update researcher link:', linkError);
                }
            }

            // Success response
            const successData = {
                message: 'Sample updated successfully!',
                condition: conditionResult,
                sample: sampleResult,
                researcher_link: linkResult
            };

            showResponse('updateResponse', successData, false);

            // Clear the form after successful update
            document.getElementById('updateForm').reset();
            document.getElementById('updateSampleBtn').style.display = 'none';
            document.getElementById('loadSampleBtn').style.display = 'none';
            document.getElementById('fullSampleFields').style.display = 'none';
            document.getElementById('growthMetricsFields').style.display = 'none';

        } catch (error) {
            showResponse('updateResponse', {error: error.message}, true);
        }
        
    } else if (updateType === 'growth_metrics') {
        data = {};
        
        // Only include fields that have values
        const height = formData.get('height');
        const leafCount = formData.get('leaf_count');
        const stemDiameter = formData.get('stem_diameter');
        const healthStatus = formData.get('health_status');
        
        if (height) data.height = parseFloat(height);
        if (leafCount) data.leaf_count = parseInt(leafCount);
        if (stemDiameter) data.stem_diameter = parseFloat(stemDiameter);
        if (healthStatus) data.health_status = healthStatus;
        
        endpoint = `${API_BASE}/samples/${sampleId}/growth-metrics/add/`;
        method = 'POST';
        
        try {
            const response = await fetch(endpoint, {
                method: method,
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await response.json();
            showResponse('updateResponse', result, !response.ok);
            
            // Clear the form after successful update
            if (response.ok) {
                document.getElementById('updateForm').reset();
                document.getElementById('updateSampleBtn').style.display = 'none';
                document.getElementById('loadSampleBtn').style.display = 'none';
                document.getElementById('fullSampleFields').style.display = 'none';
                document.getElementById('growthMetricsFields').style.display = 'none';
            }
        } catch (error) {
            showResponse('updateResponse', {error: error.message}, true);
        }
    }
});

// Delete Sample
document.getElementById('deleteForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const sampleId = formData.get('sample_id');
    const deleteType = formData.get('delete_type');
    
    try {
        let url, method = 'DELETE';
        
        if (deleteType === 'hard') {
            url = `${API_BASE}/samples/${sampleId}/hard-delete/`;
        } else {
            url = `${API_BASE}/samples/${sampleId}/`;
        }
        
        const response = await fetch(url, { method });
        const result = await response.json();
        
        // Show "already deleted" messages in red
        const isAlreadyDeleted = result.message && result.message.includes('already deleted');
        const isHardDelete = result.deletion_type === 'permanent';
        showResponse('deleteResponse', result, !response.ok || isAlreadyDeleted || isHardDelete);
        if (response.ok) e.target.reset();
    } catch (error) {
        showResponse('deleteResponse', {error: error.message}, true);
    }
});

// Handle delete type radio button changes
document.addEventListener('DOMContentLoaded', function() {
    const deleteTypeRadios = document.querySelectorAll('input[name="delete_type"]');
    const softWarning = document.getElementById('softDeleteWarning');
    const hardWarning = document.getElementById('hardDeleteWarning');
    const deleteButton = document.getElementById('deleteButton');
    
    // Function to update button and warnings
    function updateDeleteUI(deleteType) {
        if (deleteType === 'hard') {
            softWarning.style.display = 'none';
            hardWarning.style.display = 'block';
            deleteButton.textContent = 'Hard Delete Sample';
            deleteButton.className = 'btn btn-danger';
        } else {
            softWarning.style.display = 'block';
            hardWarning.style.display = 'none';
            deleteButton.textContent = 'Soft Delete Sample';
            deleteButton.className = 'btn btn-warning';
        }
    }
    
    // Set initial state for checked radio button
    const checkedRadio = document.querySelector('input[name="delete_type"]:checked');
    if (checkedRadio) {
        updateDeleteUI(checkedRadio.value);
    }
    
    deleteTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateDeleteUI(this.value);
        });
    });
});
