document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const removeBtn = document.getElementById('removeBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsSection = document.getElementById('resultsSection');
    const loading = document.getElementById('loading');
    const primaryResult = document.getElementById('primaryResult');
    const confidenceChart = document.getElementById('confidenceChart');
    const detailedInfo = document.getElementById('detailedInfo');
    const allPredictions = document.getElementById('allPredictions');
    const timelineSection = document.getElementById('timelineSection');
    const regionalFinds = document.getElementById('regionalFinds');
    const c14Input = document.getElementById('c14Input');
    const calculateC14 = document.getElementById('calculateC14');
    const ageBP = document.getElementById('ageBP');
    const calendarYear = document.getElementById('calendarYear');
    const generatePdf = document.getElementById('generatePdf');
    
    // Variables
    let currentImageFile = null;
    let c14Data = null;
    
    // Event Listeners
    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            handleImageUpload(e.dataTransfer.files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleImageUpload(e.target.files[0]);
        }
    });
    
    removeBtn.addEventListener('click', removeImage);
    
    analyzeBtn.addEventListener('click', analyzeArtifact);
    
    calculateC14.addEventListener('click', calculateCarbonAge);
    
    generatePdf.addEventListener('click', generatePDFReport);
    
    // Tab functionality for detailed info
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabBtns.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Functions
    function handleImageUpload(file) {
        if (!file.type.match('image.*')) {
            alert('Please upload an image file');
            return;
        }
        
        currentImageFile = file;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            imagePreview.style.display = 'block';
            analyzeBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }
    
    function removeImage() {
        currentImageFile = null;
        previewImg.src = '';
        imagePreview.style.display = 'none';
        fileInput.value = '';
        analyzeBtn.disabled = true;
    }
    
    function calculateCarbonAge() {
        const percentage = parseFloat(c14Input.value);
        
        if (isNaN(percentage) || percentage <= 0 || percentage > 100) {
            alert('Please enter a valid C14 percentage between 0 and 100');
            return;
        }
        
        fetch('/calculate_c14_age', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ c14_percentage: percentage })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            
            ageBP.textContent = `${data.age_bp} years`;
            calendarYear.textContent = data.calendar_year < 0 ? 
                `${Math.abs(data.calendar_year)} BCE` : 
                `${data.calendar_year} CE`;
            
            c14Data = data;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to calculate carbon age');
        });
    }
    
    function analyzeArtifact() {
        if (!currentImageFile) {
            alert('Please upload an image first');
            return;
        }
        
        // Show loading state
        resultsSection.style.display = 'block';
        loading.style.display = 'block';
        primaryResult.style.display = 'none';
        confidenceChart.style.display = 'none';
        detailedInfo.style.display = 'none';
        allPredictions.style.display = 'none';
        timelineSection.style.display = 'none';
        regionalFinds.style.display = 'none';
        document.querySelector('.report-actions').style.display = 'none';
        
        const formData = new FormData();
        formData.append('image', currentImageFile);
        
        if (c14Data) {
            formData.append('c14_data', JSON.stringify(c14Data));
        }
        
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert(`Analysis failed: ${error.message}`);
            loading.style.display = 'none';
        });
    }
    
    function displayResults(data) {
        // Hide loading, show results
        loading.style.display = 'none';
        primaryResult.style.display = 'block';
        confidenceChart.style.display = 'block';
        detailedInfo.style.display = 'block';
        allPredictions.style.display = 'block';
        timelineSection.style.display = 'block';
        regionalFinds.style.display = 'block';
        document.querySelector('.report-actions').style.display = 'block';
        
        // Set result image
        document.getElementById('resultImage').src = previewImg.src;
        
        // Display primary result
        document.getElementById('artifactClass').textContent = data.top1.class;
        const confidencePercent = (data.top1.probability * 100).toFixed(2);
        document.getElementById('confidenceValue').textContent = `${confidencePercent}%`;
        document.getElementById('confidenceFill').style.width = `${confidencePercent}%`;
        
        // Display confidence chart
        document.getElementById('chartImg').src = data.chart_url;
        
        // Display detailed information
        document.getElementById('descriptionText').textContent = data.details.description || 'No description available';
        document.getElementById('eraText').textContent = data.details.era || 'No era information available';
        document.getElementById('materialText').textContent = data.details.material || 'No material information available';
        document.getElementById('significanceText').textContent = data.details.significance || 'No significance information available';
        document.getElementById('contextText').textContent = data.details.cultural_context || 'No cultural context available';
        document.getElementById('technologyText').textContent = data.details.technological_markers || 'No technological markers available';
        
        // Display all predictions
        const predictionsList = document.getElementById('predictionsList');
        predictionsList.innerHTML = '';
        
        data.top_k.forEach(prediction => {
            const predictionItem = document.createElement('div');
            predictionItem.className = 'prediction-item';
            predictionItem.innerHTML = `
                <span class="prediction-class">${prediction.class}</span>
                <span class="prediction-confidence">${(prediction.probability * 100).toFixed(2)}%</span>
            `;
            predictionsList.appendChild(predictionItem);
        });
        
        // Load timeline
        fetchTimelineData();
        
        // Load regional finds
        fetchRegionalFinds();
    }
    
    function fetchTimelineData() {
        fetch('/timeline_eras')
        .then(response => response.json())
        .then(eras => {
            renderTimeline(eras);
        })
        .catch(error => {
            console.error('Error loading timeline:', error);
        });
    }
    
    function renderTimeline(eras) {
        const timeline = document.getElementById('timeline');
        timeline.innerHTML = '';
        
        // Find the overall date range
        const minDate = Math.min(...eras.map(era => era.start));
        const maxDate = Math.max(...eras.map(era => era.end));
        const dateRange = maxDate - minDate;
        
        eras.forEach(era => {
            const startPos = ((era.start - minDate) / dateRange) * 100;
            const width = ((era.end - era.start) / dateRange) * 100;
            
            const eraMarker = document.createElement('div');
            eraMarker.className = 'era-marker';
            eraMarker.style.left = `${startPos}%`;
            eraMarker.style.width = `${width}%`;
            eraMarker.style.backgroundColor = era.color;
            eraMarker.title = `${era.name}: ${era.description}`;
            eraMarker.textContent = era.name;
            
            timeline.appendChild(eraMarker);
        });
    }
    
    function fetchRegionalFinds() {
        fetch('/regional_finds')
        .then(response => response.json())
        .then(sites => {
            renderRegionalFinds(sites);
        })
        .catch(error => {
            console.error('Error loading regional finds:', error);
        });
    }
    
    function renderRegionalFinds(sites) {
        const sitesContainer = document.getElementById('sitesContainer');
        sitesContainer.innerHTML = '';
        
        sites.forEach(site => {
            const siteCard = document.createElement('div');
            siteCard.className = 'site-card';
            siteCard.innerHTML = `
                <h3>${site.site}</h3>
                <p class="site-distance">${site.distance}</p>
                <p class="site-significance"><strong>Significance:</strong> ${site.significance}</p>
                <p class="site-artifacts"><strong>Key Artifacts:</strong> ${site.key_artifacts}</p>
                <a href="${site.link}" target="_blank" class="site-link">Learn more</a>
            `;
            
            sitesContainer.appendChild(siteCard);
        });
    }
    
    function generatePDFReport() {
        fetch('/generate_pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                top1: {
                    class: document.getElementById('artifactClass').textContent,
                    probability: parseFloat(document.getElementById('confidenceValue').textContent) / 100
                },
                top_k: Array.from(document.querySelectorAll('.prediction-item')).map(item => ({
                    class: item.querySelector('.prediction-class').textContent,
                    probability: parseFloat(item.querySelector('.prediction-confidence').textContent) / 100
                })),
                details: {
                    description: document.getElementById('descriptionText').textContent,
                    era: document.getElementById('eraText').textContent,
                    material: document.getElementById('materialText').textContent,
                    significance: document.getElementById('significanceText').textContent,
                    cultural_context: document.getElementById('contextText').textContent,
                    technological_markers: document.getElementById('technologyText').textContent
                },
                chart_url: document.getElementById('chartImg').src,
                c14_data: c14Data
            })
        })
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('PDF generation failed');
        })
        .then(blob => {
            // Create a download link and trigger it
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'artifact_report.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to generate PDF report');
        });
    }
});