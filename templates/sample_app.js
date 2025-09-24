<<<<<<< HEAD
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archaeological Artifact Identification System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #8B4513;
            --secondary-color: #CD853F;
            --accent-color: #D2B48C;
            --light-color: #F5F5DC;
            --dark-color: #4B3621;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }
        
        /* App Container */
        .app-container {
            max-width: 100%;
            margin: 0 auto;
            position: relative;
            min-height: 100vh;
            padding-bottom: 70px; /* Space for bottom nav */
        }
        
        /* Bottom Navigation */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: white;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            z-index: 1000;
        }
        
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 5px 10px;
            color: #777;
            text-decoration: none;
            font-size: 0.8rem;
        }
        
        .nav-item.active {
            color: var(--primary-color);
        }
        
        .nav-icon {
            font-size: 1.2rem;
            margin-bottom: 4px;
        }
        
        /* App Header */
        .app-header {
            background-color: var(--primary-color);
            color: white;
            padding: 15px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .app-header h1 {
            font-size: 1.5rem;
            margin: 0;
            text-align: center;
        }
        
        /* Content Sections */
        .content-section {
            display: none;
            padding: 15px;
            animation: fadeIn 0.3s ease;
        }
        
        .content-section.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Card Styles */
        .card {
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
            margin-bottom: 20px;
            border: none;
        }
        
        .card:hover {
            transform: translateY(-3px);
        }
        
        .card-header {
            background-color: var(--primary-color);
            color: white;
            border-radius: 10px 10px 0 0 !important;
            padding: 12px 15px;
        }
        
        .card-header h5 {
            margin: 0;
            font-size: 1.1rem;
        }
        
        .card-body {
            padding: 15px;
        }
        
        /* Buttons */
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            padding: 10px 15px;
            border-radius: 8px;
        }
        
        .btn-primary:hover {
            background-color: var(--secondary-color);
            border-color: var(--secondary-color);
        }
        
        /* Form Elements */
        .form-control {
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #ddd;
        }
        
        /* Hero Section */
        .hero-section {
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('https://images.unsplash.com/photo-1580651316326-3c2d316521c4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80');
            background-size: cover;
            background-position: center;
            color: white;
            padding: 60px 20px;
            text-align: center;
            border-radius: 0 0 20px 20px;
            margin-bottom: 20px;
        }
        
        .hero-section h1 {
            font-size: 1.8rem;
            margin-bottom: 10px;
        }
        
        .hero-section p {
            font-size: 1rem;
            margin-bottom: 20px;
        }
        
        /* Confidence Bar */
        .confidence-bar {
            height: 25px;
            background-color: #e9ecef;
            border-radius: 5px;
            margin-bottom: 10px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            background-color: var(--primary-color);
            text-align: right;
            padding-right: 10px;
            line-height: 25px;
            color: white;
            font-weight: bold;
            transition: width 1s ease;
        }
        
        /* Image Preview */
        .artifact-image-preview {
            max-width: 100%;
            max-height: 250px;
            border-radius: 8px;
            margin: 15px auto;
            display: block;
        }
        
        /* Timeline */
        .timeline-era {
            border-left: 3px solid var(--primary-color);
            padding-left: 15px;
            margin-bottom: 20px;
            position: relative;
        }
        
        .timeline-era:before {
            content: '';
            position: absolute;
            left: -8px;
            top: 0;
            width: 13px;
            height: 13px;
            border-radius: 50%;
            background-color: var(--primary-color);
        }
        
        /* Loading Spinner */
        #loadingSpinner {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        /* Result Section */
        .result-section {
            display: none;
            margin-top: 20px;
        }
        
        /* PDF Loading */
        .pdf-loading {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            display: none;
        }
        
        .pdf-loading-content {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            max-width: 80%;
        }
        
        /* Section Titles */
        .section-title {
            position: relative;
            padding-bottom: 10px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 1.4rem;
        }
        
        .section-title:after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background-color: var(--primary-color);
        }
        
        /* Footer */
        footer {
            background-color: var(--dark-color);
            color: white;
            padding: 20px 0;
            text-align: center;
            margin-top: 30px;
            border-radius: 20px 20px 0 0;
        }
        
        /* Responsive Adjustments */
        @media (min-width: 768px) {
            .app-container {
                max-width: 600px;
            }
            
            .hero-section {
                padding: 80px 20px;
            }
            
            .hero-section h1 {
                font-size: 2.2rem;
            }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- App Header -->
        <header class="app-header">
            <h1><i class="fas fa-monument me-2"></i>Artifact Identifier</h1>
        </header>

        <!-- Main Content -->
        <main>
            <!-- Home Section -->
            <section id="home-section" class="content-section active">
                <div class="hero-section">
                    <h1>Archaeological Artifact Identification</h1>
                    <p>Advanced AI-powered analysis of archaeological artifacts with historical context and carbon dating</p>
                    <a href="#identification" class="btn btn-primary btn-lg mt-3" onclick="showSection('identification-section')">Get Started</a>
                </div>

                <div class="container mt-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h3>Quick Actions</h3>
                            <div class="row mt-4">
                                <div class="col-6 mb-3">
                                    <div class="card bg-light" onclick="showSection('identification-section')" style="cursor: pointer;">
                                        <div class="card-body">
                                            <i class="fas fa-camera feature-icon"></i>
                                            <h6>Identify Artifact</h6>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-6 mb-3">
                                    <div class="card bg-light" onclick="showSection('dating-section')" style="cursor: pointer;">
                                        <div class="card-body">
                                            <i class="fas fa-clock feature-icon"></i>
                                            <h6>Carbon Dating</h6>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-6 mb-3">
                                    <div class="card bg-light" onclick="showSection('timeline-section')" style="cursor: pointer;">
                                        <div class="card-body">
                                            <i class="fas fa-history feature-icon"></i>
                                            <h6>Timeline</h6>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-6 mb-3">
                                    <div class="card bg-light" onclick="showSection('regional-section')" style="cursor: pointer;">
                                        <div class="card-body">
                                            <i class="fas fa-map-marker-alt feature-icon"></i>
                                            <h6>Regional Finds</h6>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Identification Section -->
            <section id="identification-section" class="content-section">
                <h2 class="section-title">Artifact Identification</h2>
                
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Upload Artifact Image</h5>
                    </div>
                    <div class="card-body">
                        <form id="uploadForm" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="artifactImage" class="form-label">Select an image of your artifact</label>
                                <input class="form-control" type="file" id="artifactImage" accept="image/*" required>
                            </div>
                            <div id="imagePreview" class="text-center mb-3"></div>
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="fas fa-search me-2"></i>Analyze Artifact
                            </button>
                        </form>
                        <div id="loadingSpinner" class="text-center mt-4">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-2">Analyzing artifact...</p>
                        </div>
                    </div>
                </div>

                <div class="card mt-3">
                    <div class="card-header">
                        <h5 class="mb-0">How It Works</h5>
                    </div>
                    <div class="card-body">
                        <ol>
                            <li>Upload a clear image of your archaeological artifact</li>
                            <li>Our AI model will analyze the image and classify the artifact</li>
                            <li>View detailed information about the artifact type</li>
                            <li>Generate a comprehensive PDF report</li>
                        </ol>
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            For best results, use a clear, well-lit image with a neutral background.
                        </div>
                    </div>
                </div>

                <!-- Results Section -->
                <div id="resultSection" class="result-section mt-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Analysis Results</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-12">
                                    <h4>Primary Identification</h4>
                                    <div class="card bg-light mb-4">
                                        <div class="card-body">
                                            <h3 id="primaryClass" class="text-primary"></h3>
                                            <div class="confidence-bar">
                                                <div id="primaryConfidence" class="confidence-fill" style="width: 0%">0%</div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <h5>Detailed Information</h5>
                                    <div id="artifactDetails" class="bg-light p-3 rounded mb-3"></div>
                                    
                                    <h5 class="mt-4">All Predictions</h5>
                                    <div id="allPredictions" class="mb-3"></div>
                                    
                                    <div class="d-grid gap-2 mt-4">
                                        <button id="generatePdfBtn" class="btn btn-primary">
                                            <i class="fas fa-file-pdf me-2"></i>Generate PDF Report
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Carbon Dating Section -->
            <section id="dating-section" class="content-section">
                <h2 class="section-title">Carbon-14 Dating</h2>
                
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Calculate Artifact Age</h5>
                    </div>
                    <div class="card-body">
                        <form id="carbonDatingForm">
                            <div class="mb-3">
                                <label for="c14Percentage" class="form-label">C14 Percentage Remaining</label>
                                <input type="number" class="form-control" id="c14Percentage" 
                                       min="0.1" max="100" step="0.1" required 
                                       placeholder="Enter percentage (0.1 to 100)">
                                <div class="form-text">Percentage of Carbon-14 remaining compared to living organisms</div>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="fas fa-calculator me-2"></i>Calculate Age
                            </button>
                        </form>
                    </div>
                </div>

                <div class="card mt-3">
                    <div class="card-header">
                        <h5 class="mb-0">Dating Results</h5>
                    </div>
                    <div class="card-body">
                        <div id="datingResults" class="text-center">
                            <p class="text-muted">Enter C14 percentage to calculate age</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Timeline Section -->
            <section id="timeline-section" class="content-section">
                <h2 class="section-title">Historical Timeline</h2>
                
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Archaeological Eras</h5>
                    </div>
                    <div class="card-body">
                        <div id="timelineContent"></div>
                    </div>
                </div>
            </section>

            <!-- Regional Finds Section -->
            <section id="regional-section" class="content-section">
                <h2 class="section-title">Regional Sites</h2>
                
                <div class="row" id="regionalFindsContent"></div>
            </section>
        </main>

        <!-- Bottom Navigation -->
        <nav class="bottom-nav">
            <a href="#" class="nav-item active" onclick="showSection('home-section')">
                <i class="fas fa-home nav-icon"></i>
                <span>Home</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('identification-section')">
                <i class="fas fa-camera nav-icon"></i>
                <span>Identify</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('dating-section')">
                <i class="fas fa-clock nav-icon"></i>
                <span>Dating</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('timeline-section')">
                <i class="fas fa-history nav-icon"></i>
                <span>Timeline</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('regional-section')">
                <i class="fas fa-map-marker-alt nav-icon"></i>
                <span>Sites</span>
            </a>
        </nav>

        <!-- Footer -->
        <footer>
            <div class="container">
                <p>&copy; 2023 Archaeological Artifact Identification System</p>
                <p>Advanced AI-powered analysis for historical artifacts</p>
            </div>
        </footer>

        <!-- PDF Loading Indicator -->
        <div class="pdf-loading" id="pdfLoading">
            <div class="pdf-loading-content">
                <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h4>Generating PDF Report</h4>
                <p>Please wait while we prepare your comprehensive artifact report...</p>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Store the current analysis data globally
        let currentAnalysisData = null;
        
        // Function to show/hide sections
        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Show the selected section
            document.getElementById(sectionId).classList.add('active');
            
            // Update bottom nav active state
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Set home as active if we're not on a nav item
            if (sectionId === 'home-section') {
                document.querySelectorAll('.nav-item')[0].classList.add('active');
            }
            
            // Scroll to top
            window.scrollTo(0, 0);
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            // Image preview functionality
            const artifactImage = document.getElementById('artifactImage');
            const imagePreview = document.getElementById('imagePreview');
            
            artifactImage.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        imagePreview.innerHTML = `<img src="${e.target.result}" class="artifact-image-preview" alt="Preview">`;
                    };
                    reader.readAsDataURL(file);
                }
            });
            
            // Form submission for artifact identification
            const uploadForm = document.getElementById('uploadForm');
            const loadingSpinner = document.getElementById('loadingSpinner');
            const resultSection = document.getElementById('resultSection');
            
            uploadForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const fileInput = document.getElementById('artifactImage');
                if (!fileInput.files.length) {
                    alert('Please select an image first');
                    return;
                }
                
                const formData = new FormData();
                formData.append('image', fileInput.files[0]);
                
                loadingSpinner.style.display = 'block';
                
                // Simulate API call with demo data
                setTimeout(() => {
                    loadingSpinner.style.display = 'none';
                    
                    // Demo data for testing
                    const demoData = {
                        top1: {
                            class: "Roman Pottery",
                            probability: 0.87
                        },
                        top_k: [
                            {class: "Roman Pottery", probability: 0.87},
                            {class: "Greek Amphora", probability: 0.09},
                            {class: "Medieval Ceramic", probability: 0.03},
                            {class: "Bronze Age Vessel", probability: 0.01}
                        ],
                        details: {
                            description: "A well-preserved example of Roman terra sigillata pottery, characterized by its distinctive red gloss finish and refined craftsmanship.",
                            era: "Roman Empire (1st-3rd century CE)",
                            material: "Terracotta clay with red slip finish",
                            significance: "Terra sigillata pottery was mass-produced and widely traded throughout the Roman Empire, representing both technological innovation in ceramic production and the extent of Roman trade networks.",
                            cultural_context: "Used primarily as tableware in Roman households, these vessels demonstrate the spread of Roman material culture and dining customs across the Empire.",
                            technological_markers: "Wheel-thrown, distinctive red slip finish, often with stamped manufacturer's marks on the base."
                        },
                        chart_url: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjJmMmYyIi8+PGcgZmlsbD0iIzhiNDUxMyI+PHJlY3QgeD0iNTAiIHk9IjUwIiB3aWR0aD0iODciIGhlaWdodD0iMzAiIC8+PHJlY3QgeD0iNTAiIHk9IjkwIiB3aWR0aD0iOSIgaGVpZ2h0PSIzMCIgLz48cmVjdCB4PSI1MCIgeT0iMTMwIiB3aWR0aD0iMyIgaGVpZ2h0PSIzMCIgLz48cmVjdCB4PSI1MCIgeT0iMTcwIiB3aWR0aD0iMSIgaGVpZ2h0PSIzMCIgLz48L2c+PHRleHQgeD0iMTUwIiB5PSI3MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiBmaWxsPSIjMzMzIj5Sb21hbiBQb3R0ZXJ5ICg4NyUpPC90ZXh0Pjx0ZXh0IHg9IjE1MCIgeT0iMTEwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiMzMzMiPkdyZWVrIEFtcGhvcmEgKDklKTwvdGV4dD48dGV4dCB4PSIxNTAiIHk9IjE1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiBmaWxsPSIjMzMzIj5NZWRpZXZhbCBDZXJhbWljICgzJSk8L3RleHQ+PHRleHQgeD0iMTUwIiB5PSIxOTAiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzMzMyI+QnJvbnplIEFnZSBWZXNzZWwgKDElKTwvdGV4dD48L3N2Zz4="
                    };
                    
                    currentAnalysisData = demoData;
                    
                    // Display results
                    document.getElementById('primaryClass').textContent = demoData.top1.class;
                    document.getElementById('primaryConfidence').style.width = (demoData.top1.probability * 100) + '%';
                    document.getElementById('primaryConfidence').textContent = (demoData.top1.probability * 100).toFixed(2) + '%';
                    
                    // Display details
                    const details = demoData.details;
                    let detailsHtml = `
                        <p><strong>Description:</strong> ${details.description}</p>
                        <p><strong>Historical Era:</strong> ${details.era}</p>
                        <p><strong>Material Composition:</strong> ${details.material}</p>
                        <p><strong>Cultural Significance:</strong> ${details.significance}</p>
                        <p><strong>Cultural Context:</strong> ${details.cultural_context}</p>
                        <p><strong>Technological Markers:</strong> ${details.technological_markers}</p>
                    `;
                    document.getElementById('artifactDetails').innerHTML = detailsHtml;
                    
                    // Display all predictions
                    let predictionsHtml = '';
                    demoData.top_k.forEach(prediction => {
                        predictionsHtml += `
                            <div class="mb-2">
                                <div class="d-flex justify-content-between">
                                    <span>${prediction.class}</span>
                                    <span>${(prediction.probability * 100).toFixed(2)}%</span>
                                </div>
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: ${prediction.probability * 100}%">${(prediction.probability * 100).toFixed(2)}%</div>
                                </div>
                            </div>
                        `;
                    });
                    document.getElementById('allPredictions').innerHTML = predictionsHtml;
                    
                    // Show result section
                    resultSection.style.display = 'block';
                    
                    // Scroll to results
                    resultSection.scrollIntoView({ behavior: 'smooth' });
                }, 2000);
            });
            
            // Carbon dating form submission
            const carbonDatingForm = document.getElementById('carbonDatingForm');
            const datingResults = document.getElementById('datingResults');
            
            carbonDatingForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const percentage = parseFloat(document.getElementById('c14Percentage').value);
                
                if (isNaN(percentage) || percentage <= 0 || percentage > 100) {
                    alert('Please enter a valid percentage between 0.1 and 100');
                    return;
                }
                
                // Calculate using the formula: t = (ln(Nf/No) / ln(0.5)) * halfLife
                // Half-life of C14 is 5730 years
                const halfLife = 5730;
                const age = Math.round((Math.log(percentage / 100) / Math.log(0.5)) * halfLife);
                const calendarYear = 1950 - age;
                
                datingResults.innerHTML = `
                    <h4>Dating Results</h4>
                    <div class="card bg-light mb-3">
                        <div class="card-body">
                            <h5>${age} years BP</h5>
                            <p class="mb-0">Before Present (1950 CE)</p>
                        </div>
                    </div>
                    <div class="card bg-light">
                        <div class="card-body">
                            <h5>Calendar Year: ${Math.abs(calendarYear)} ${calendarYear >= 0 ? 'CE' : 'BCE'}</h5>
                            <p class="mb-0">Approximate calendar year</p>
                        </div>
                    </div>
                `;
            });
            
            // Load timeline data
            const timelineData = [
                {
                    name: "Paleolithic",
                    start: -2500000,
                    end: -10000,
                    description: "The Old Stone Age, characterized by the development of the first stone tools by early humans.",
                    color: "#8B4513"
                },
                {
                    name: "Neolithic",
                    start: -10000,
                    end: -3000,
                    description: "The New Stone Age, marked by the development of agriculture, pottery, and permanent settlements.",
                    color: "#CD853F"
                },
                {
                    name: "Bronze Age",
                    start: -3000,
                    end: -1200,
                    description: "Characterized by the use of bronze tools and weapons, and the development of early writing systems.",
                    color: "#B8860B"
                },
                {
                    name: "Iron Age",
                    start: -1200,
                    end: -500,
                    description: "Marked by the widespread use of iron for tools and weapons, and the development of complex societies.",
                    color: "#D2691E"
                },
                {
                    name: "Classical Antiquity",
                    start: -500,
                    end: 500,
                    description: "The period of cultural history between the 8th century BC and the 6th century AD centered on the Mediterranean Sea.",
                    color: "#A0522D"
                },
                {
                    name: "Medieval Period",
                    start: 500,
                    end: 1500,
                    description: "The Middle Ages, spanning from the fall of the Western Roman Empire to the Renaissance.",
                    color: "#D2B48C"
                }
            ];
            
            let timelineHtml = '';
            timelineData.forEach(era => {
                timelineHtml += `
                    <div class="timeline-era">
                        <h5>${era.name} (${era.start < 0 ? Math.abs(era.start) + ' BCE' : era.start + ' CE'} - ${era.end < 0 ? Math.abs(era.end) + ' BCE' : era.end + ' CE'})</h5>
                        <p>${era.description}</p>
                        <div style="height: 10px; background-color: ${era.color}; width: 100%; border-radius: 5px;"></div>
                    </div>
                `;
            });
            document.getElementById('timelineContent').innerHTML = timelineHtml;
            
            // Load regional finds data
            const regionalData = [
                {
                    site: "Hadrian's Wall",
                    distance: "120km away",
                    significance: "Roman defensive fortification marking the northern boundary of the Roman Empire in Britain.",
                    key_artifacts: "Roman coins, pottery, weapons, and inscriptions",
                    link: "#"
                },
                {
                    site: "Stonehenge",
                    distance: "230km away",
                    significance: "Prehistoric monument dating back to 3000 BC, likely used for ceremonial purposes.",
                    key_artifacts: "Stone tools, animal bones, pottery fragments",
                    link: "#"
                },
                {
                    site: "Vindolanda",
                    distance: "140km away",
                    significance: "Roman auxiliary fort just south of Hadrian's Wall, famous for the Vindolanda tablets.",
                    key_artifacts: "Wooden writing tablets, leather shoes, textiles",
                    link: "#"
                }
            ];
            
            let findsHtml = '';
            regionalData.forEach(site => {
                findsHtml += `
                    <div class="col-12 mb-3">
                        <div class="card site-card h-100">
                            <div class="card-body">
                                <h5 class="card-title">${site.site}</h5>
                                <h6 class="card-subtitle mb-2 text-muted">${site.distance}</h6>
                                <p class="card-text"><strong>Significance:</strong> ${site.significance}</p>
                                <p class="card-text"><strong>Key Artifacts:</strong> ${site.key_artifacts}</p>
                                <a href="${site.link}" target="_blank" class="btn btn-sm btn-outline-primary">Learn More</a>
                            </div>
                        </div>
                    </div>
                `;
            });
            document.getElementById('regionalFindsContent').innerHTML = findsHtml;
            
            // Generate PDF functionality
            document.getElementById('generatePdfBtn').addEventListener('click', function() {
                if (!currentAnalysisData) {
                    alert('Please analyze an artifact first before generating a PDF report.');
                    return;
                }
                
                // Show loading indicator
                document.getElementById('pdfLoading').style.display = 'flex';
                
                // Simulate PDF generation
                setTimeout(() => {
                    // Create a dummy blob for download
                    const blob = new Blob(["Sample PDF content would be here"], { type: 'application/pdf' });
                    
                    // Create a download link for the PDF
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = 'artifact_report.pdf';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    
                    // Hide loading indicator
                    document.getElementById('pdfLoading').style.display = 'none';
                }, 2000);
            });
        });
    </script>
</body>
=======
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archaeological Artifact Identification System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #8B4513;
            --secondary-color: #CD853F;
            --accent-color: #D2B48C;
            --light-color: #F5F5DC;
            --dark-color: #4B3621;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }
        
        /* App Container */
        .app-container {
            max-width: 100%;
            margin: 0 auto;
            position: relative;
            min-height: 100vh;
            padding-bottom: 70px; /* Space for bottom nav */
        }
        
        /* Bottom Navigation */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: white;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            z-index: 1000;
        }
        
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 5px 10px;
            color: #777;
            text-decoration: none;
            font-size: 0.8rem;
        }
        
        .nav-item.active {
            color: var(--primary-color);
        }
        
        .nav-icon {
            font-size: 1.2rem;
            margin-bottom: 4px;
        }
        
        /* App Header */
        .app-header {
            background-color: var(--primary-color);
            color: white;
            padding: 15px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .app-header h1 {
            font-size: 1.5rem;
            margin: 0;
            text-align: center;
        }
        
        /* Content Sections */
        .content-section {
            display: none;
            padding: 15px;
            animation: fadeIn 0.3s ease;
        }
        
        .content-section.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Card Styles */
        .card {
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
            margin-bottom: 20px;
            border: none;
        }
        
        .card:hover {
            transform: translateY(-3px);
        }
        
        .card-header {
            background-color: var(--primary-color);
            color: white;
            border-radius: 10px 10px 0 0 !important;
            padding: 12px 15px;
        }
        
        .card-header h5 {
            margin: 0;
            font-size: 1.1rem;
        }
        
        .card-body {
            padding: 15px;
        }
        
        /* Buttons */
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            padding: 10px 15px;
            border-radius: 8px;
        }
        
        .btn-primary:hover {
            background-color: var(--secondary-color);
            border-color: var(--secondary-color);
        }
        
        /* Form Elements */
        .form-control {
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #ddd;
        }
        
        /* Hero Section */
        .hero-section {
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('https://images.unsplash.com/photo-1580651316326-3c2d316521c4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80');
            background-size: cover;
            background-position: center;
            color: white;
            padding: 60px 20px;
            text-align: center;
            border-radius: 0 0 20px 20px;
            margin-bottom: 20px;
        }
        
        .hero-section h1 {
            font-size: 1.8rem;
            margin-bottom: 10px;
        }
        
        .hero-section p {
            font-size: 1rem;
            margin-bottom: 20px;
        }
        
        /* Confidence Bar */
        .confidence-bar {
            height: 25px;
            background-color: #e9ecef;
            border-radius: 5px;
            margin-bottom: 10px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            background-color: var(--primary-color);
            text-align: right;
            padding-right: 10px;
            line-height: 25px;
            color: white;
            font-weight: bold;
            transition: width 1s ease;
        }
        
        /* Image Preview */
        .artifact-image-preview {
            max-width: 100%;
            max-height: 250px;
            border-radius: 8px;
            margin: 15px auto;
            display: block;
        }
        
        /* Timeline */
        .timeline-era {
            border-left: 3px solid var(--primary-color);
            padding-left: 15px;
            margin-bottom: 20px;
            position: relative;
        }
        
        .timeline-era:before {
            content: '';
            position: absolute;
            left: -8px;
            top: 0;
            width: 13px;
            height: 13px;
            border-radius: 50%;
            background-color: var(--primary-color);
        }
        
        /* Loading Spinner */
        #loadingSpinner {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        /* Result Section */
        .result-section {
            display: none;
            margin-top: 20px;
        }
        
        /* PDF Loading */
        .pdf-loading {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            display: none;
        }
        
        .pdf-loading-content {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            max-width: 80%;
        }
        
        /* Section Titles */
        .section-title {
            position: relative;
            padding-bottom: 10px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 1.4rem;
        }
        
        .section-title:after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background-color: var(--primary-color);
        }
        
        /* Footer */
        footer {
            background-color: var(--dark-color);
            color: white;
            padding: 20px 0;
            text-align: center;
            margin-top: 30px;
            border-radius: 20px 20px 0 0;
        }
        
        /* Responsive Adjustments */
        @media (min-width: 768px) {
            .app-container {
                max-width: 600px;
            }
            
            .hero-section {
                padding: 80px 20px;
            }
            
            .hero-section h1 {
                font-size: 2.2rem;
            }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- App Header -->
        <header class="app-header">
            <h1><i class="fas fa-monument me-2"></i>Artifact Identifier</h1>
        </header>

        <!-- Main Content -->
        <main>
            <!-- Home Section -->
            <section id="home-section" class="content-section active">
                <div class="hero-section">
                    <h1>Archaeological Artifact Identification</h1>
                    <p>Advanced AI-powered analysis of archaeological artifacts with historical context and carbon dating</p>
                    <a href="#identification" class="btn btn-primary btn-lg mt-3" onclick="showSection('identification-section')">Get Started</a>
                </div>

                <div class="container mt-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h3>Quick Actions</h3>
                            <div class="row mt-4">
                                <div class="col-6 mb-3">
                                    <div class="card bg-light" onclick="showSection('identification-section')" style="cursor: pointer;">
                                        <div class="card-body">
                                            <i class="fas fa-camera feature-icon"></i>
                                            <h6>Identify Artifact</h6>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-6 mb-3">
                                    <div class="card bg-light" onclick="showSection('dating-section')" style="cursor: pointer;">
                                        <div class="card-body">
                                            <i class="fas fa-clock feature-icon"></i>
                                            <h6>Carbon Dating</h6>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-6 mb-3">
                                    <div class="card bg-light" onclick="showSection('timeline-section')" style="cursor: pointer;">
                                        <div class="card-body">
                                            <i class="fas fa-history feature-icon"></i>
                                            <h6>Timeline</h6>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-6 mb-3">
                                    <div class="card bg-light" onclick="showSection('regional-section')" style="cursor: pointer;">
                                        <div class="card-body">
                                            <i class="fas fa-map-marker-alt feature-icon"></i>
                                            <h6>Regional Finds</h6>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Identification Section -->
            <section id="identification-section" class="content-section">
                <h2 class="section-title">Artifact Identification</h2>
                
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Upload Artifact Image</h5>
                    </div>
                    <div class="card-body">
                        <form id="uploadForm" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="artifactImage" class="form-label">Select an image of your artifact</label>
                                <input class="form-control" type="file" id="artifactImage" accept="image/*" required>
                            </div>
                            <div id="imagePreview" class="text-center mb-3"></div>
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="fas fa-search me-2"></i>Analyze Artifact
                            </button>
                        </form>
                        <div id="loadingSpinner" class="text-center mt-4">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-2">Analyzing artifact...</p>
                        </div>
                    </div>
                </div>

                <div class="card mt-3">
                    <div class="card-header">
                        <h5 class="mb-0">How It Works</h5>
                    </div>
                    <div class="card-body">
                        <ol>
                            <li>Upload a clear image of your archaeological artifact</li>
                            <li>Our AI model will analyze the image and classify the artifact</li>
                            <li>View detailed information about the artifact type</li>
                            <li>Generate a comprehensive PDF report</li>
                        </ol>
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            For best results, use a clear, well-lit image with a neutral background.
                        </div>
                    </div>
                </div>

                <!-- Results Section -->
                <div id="resultSection" class="result-section mt-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Analysis Results</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-12">
                                    <h4>Primary Identification</h4>
                                    <div class="card bg-light mb-4">
                                        <div class="card-body">
                                            <h3 id="primaryClass" class="text-primary"></h3>
                                            <div class="confidence-bar">
                                                <div id="primaryConfidence" class="confidence-fill" style="width: 0%">0%</div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <h5>Detailed Information</h5>
                                    <div id="artifactDetails" class="bg-light p-3 rounded mb-3"></div>
                                    
                                    <h5 class="mt-4">All Predictions</h5>
                                    <div id="allPredictions" class="mb-3"></div>
                                    
                                    <div class="d-grid gap-2 mt-4">
                                        <button id="generatePdfBtn" class="btn btn-primary">
                                            <i class="fas fa-file-pdf me-2"></i>Generate PDF Report
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Carbon Dating Section -->
            <section id="dating-section" class="content-section">
                <h2 class="section-title">Carbon-14 Dating</h2>
                
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Calculate Artifact Age</h5>
                    </div>
                    <div class="card-body">
                        <form id="carbonDatingForm">
                            <div class="mb-3">
                                <label for="c14Percentage" class="form-label">C14 Percentage Remaining</label>
                                <input type="number" class="form-control" id="c14Percentage" 
                                       min="0.1" max="100" step="0.1" required 
                                       placeholder="Enter percentage (0.1 to 100)">
                                <div class="form-text">Percentage of Carbon-14 remaining compared to living organisms</div>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="fas fa-calculator me-2"></i>Calculate Age
                            </button>
                        </form>
                    </div>
                </div>

                <div class="card mt-3">
                    <div class="card-header">
                        <h5 class="mb-0">Dating Results</h5>
                    </div>
                    <div class="card-body">
                        <div id="datingResults" class="text-center">
                            <p class="text-muted">Enter C14 percentage to calculate age</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Timeline Section -->
            <section id="timeline-section" class="content-section">
                <h2 class="section-title">Historical Timeline</h2>
                
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Archaeological Eras</h5>
                    </div>
                    <div class="card-body">
                        <div id="timelineContent"></div>
                    </div>
                </div>
            </section>

            <!-- Regional Finds Section -->
            <section id="regional-section" class="content-section">
                <h2 class="section-title">Regional Sites</h2>
                
                <div class="row" id="regionalFindsContent"></div>
            </section>
        </main>

        <!-- Bottom Navigation -->
        <nav class="bottom-nav">
            <a href="#" class="nav-item active" onclick="showSection('home-section')">
                <i class="fas fa-home nav-icon"></i>
                <span>Home</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('identification-section')">
                <i class="fas fa-camera nav-icon"></i>
                <span>Identify</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('dating-section')">
                <i class="fas fa-clock nav-icon"></i>
                <span>Dating</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('timeline-section')">
                <i class="fas fa-history nav-icon"></i>
                <span>Timeline</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('regional-section')">
                <i class="fas fa-map-marker-alt nav-icon"></i>
                <span>Sites</span>
            </a>
        </nav>

        <!-- Footer -->
        <footer>
            <div class="container">
                <p>&copy; 2023 Archaeological Artifact Identification System</p>
                <p>Advanced AI-powered analysis for historical artifacts</p>
            </div>
        </footer>

        <!-- PDF Loading Indicator -->
        <div class="pdf-loading" id="pdfLoading">
            <div class="pdf-loading-content">
                <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h4>Generating PDF Report</h4>
                <p>Please wait while we prepare your comprehensive artifact report...</p>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Store the current analysis data globally
        let currentAnalysisData = null;
        
        // Function to show/hide sections
        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Show the selected section
            document.getElementById(sectionId).classList.add('active');
            
            // Update bottom nav active state
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Set home as active if we're not on a nav item
            if (sectionId === 'home-section') {
                document.querySelectorAll('.nav-item')[0].classList.add('active');
            }
            
            // Scroll to top
            window.scrollTo(0, 0);
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            // Image preview functionality
            const artifactImage = document.getElementById('artifactImage');
            const imagePreview = document.getElementById('imagePreview');
            
            artifactImage.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        imagePreview.innerHTML = `<img src="${e.target.result}" class="artifact-image-preview" alt="Preview">`;
                    };
                    reader.readAsDataURL(file);
                }
            });
            
            // Form submission for artifact identification
            const uploadForm = document.getElementById('uploadForm');
            const loadingSpinner = document.getElementById('loadingSpinner');
            const resultSection = document.getElementById('resultSection');
            
            uploadForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const fileInput = document.getElementById('artifactImage');
                if (!fileInput.files.length) {
                    alert('Please select an image first');
                    return;
                }
                
                const formData = new FormData();
                formData.append('image', fileInput.files[0]);
                
                loadingSpinner.style.display = 'block';
                
                // Simulate API call with demo data
                setTimeout(() => {
                    loadingSpinner.style.display = 'none';
                    
                    // Demo data for testing
                    const demoData = {
                        top1: {
                            class: "Roman Pottery",
                            probability: 0.87
                        },
                        top_k: [
                            {class: "Roman Pottery", probability: 0.87},
                            {class: "Greek Amphora", probability: 0.09},
                            {class: "Medieval Ceramic", probability: 0.03},
                            {class: "Bronze Age Vessel", probability: 0.01}
                        ],
                        details: {
                            description: "A well-preserved example of Roman terra sigillata pottery, characterized by its distinctive red gloss finish and refined craftsmanship.",
                            era: "Roman Empire (1st-3rd century CE)",
                            material: "Terracotta clay with red slip finish",
                            significance: "Terra sigillata pottery was mass-produced and widely traded throughout the Roman Empire, representing both technological innovation in ceramic production and the extent of Roman trade networks.",
                            cultural_context: "Used primarily as tableware in Roman households, these vessels demonstrate the spread of Roman material culture and dining customs across the Empire.",
                            technological_markers: "Wheel-thrown, distinctive red slip finish, often with stamped manufacturer's marks on the base."
                        },
                        chart_url: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjJmMmYyIi8+PGcgZmlsbD0iIzhiNDUxMyI+PHJlY3QgeD0iNTAiIHk9IjUwIiB3aWR0aD0iODciIGhlaWdodD0iMzAiIC8+PHJlY3QgeD0iNTAiIHk9IjkwIiB3aWR0aD0iOSIgaGVpZ2h0PSIzMCIgLz48cmVjdCB4PSI1MCIgeT0iMTMwIiB3aWR0aD0iMyIgaGVpZ2h0PSIzMCIgLz48cmVjdCB4PSI1MCIgeT0iMTcwIiB3aWR0aD0iMSIgaGVpZ2h0PSIzMCIgLz48L2c+PHRleHQgeD0iMTUwIiB5PSI3MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiBmaWxsPSIjMzMzIj5Sb21hbiBQb3R0ZXJ5ICg4NyUpPC90ZXh0Pjx0ZXh0IHg9IjE1MCIgeT0iMTEwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiMzMzMiPkdyZWVrIEFtcGhvcmEgKDklKTwvdGV4dD48dGV4dCB4PSIxNTAiIHk9IjE1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiBmaWxsPSIjMzMzIj5NZWRpZXZhbCBDZXJhbWljICgzJSk8L3RleHQ+PHRleHQgeD0iMTUwIiB5PSIxOTAiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzMzMyI+QnJvbnplIEFnZSBWZXNzZWwgKDElKTwvdGV4dD48L3N2Zz4="
                    };
                    
                    currentAnalysisData = demoData;
                    
                    // Display results
                    document.getElementById('primaryClass').textContent = demoData.top1.class;
                    document.getElementById('primaryConfidence').style.width = (demoData.top1.probability * 100) + '%';
                    document.getElementById('primaryConfidence').textContent = (demoData.top1.probability * 100).toFixed(2) + '%';
                    
                    // Display details
                    const details = demoData.details;
                    let detailsHtml = `
                        <p><strong>Description:</strong> ${details.description}</p>
                        <p><strong>Historical Era:</strong> ${details.era}</p>
                        <p><strong>Material Composition:</strong> ${details.material}</p>
                        <p><strong>Cultural Significance:</strong> ${details.significance}</p>
                        <p><strong>Cultural Context:</strong> ${details.cultural_context}</p>
                        <p><strong>Technological Markers:</strong> ${details.technological_markers}</p>
                    `;
                    document.getElementById('artifactDetails').innerHTML = detailsHtml;
                    
                    // Display all predictions
                    let predictionsHtml = '';
                    demoData.top_k.forEach(prediction => {
                        predictionsHtml += `
                            <div class="mb-2">
                                <div class="d-flex justify-content-between">
                                    <span>${prediction.class}</span>
                                    <span>${(prediction.probability * 100).toFixed(2)}%</span>
                                </div>
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: ${prediction.probability * 100}%">${(prediction.probability * 100).toFixed(2)}%</div>
                                </div>
                            </div>
                        `;
                    });
                    document.getElementById('allPredictions').innerHTML = predictionsHtml;
                    
                    // Show result section
                    resultSection.style.display = 'block';
                    
                    // Scroll to results
                    resultSection.scrollIntoView({ behavior: 'smooth' });
                }, 2000);
            });
            
            // Carbon dating form submission
            const carbonDatingForm = document.getElementById('carbonDatingForm');
            const datingResults = document.getElementById('datingResults');
            
            carbonDatingForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const percentage = parseFloat(document.getElementById('c14Percentage').value);
                
                if (isNaN(percentage) || percentage <= 0 || percentage > 100) {
                    alert('Please enter a valid percentage between 0.1 and 100');
                    return;
                }
                
                // Calculate using the formula: t = (ln(Nf/No) / ln(0.5)) * halfLife
                // Half-life of C14 is 5730 years
                const halfLife = 5730;
                const age = Math.round((Math.log(percentage / 100) / Math.log(0.5)) * halfLife);
                const calendarYear = 1950 - age;
                
                datingResults.innerHTML = `
                    <h4>Dating Results</h4>
                    <div class="card bg-light mb-3">
                        <div class="card-body">
                            <h5>${age} years BP</h5>
                            <p class="mb-0">Before Present (1950 CE)</p>
                        </div>
                    </div>
                    <div class="card bg-light">
                        <div class="card-body">
                            <h5>Calendar Year: ${Math.abs(calendarYear)} ${calendarYear >= 0 ? 'CE' : 'BCE'}</h5>
                            <p class="mb-0">Approximate calendar year</p>
                        </div>
                    </div>
                `;
            });
            
            // Load timeline data
            const timelineData = [
                {
                    name: "Paleolithic",
                    start: -2500000,
                    end: -10000,
                    description: "The Old Stone Age, characterized by the development of the first stone tools by early humans.",
                    color: "#8B4513"
                },
                {
                    name: "Neolithic",
                    start: -10000,
                    end: -3000,
                    description: "The New Stone Age, marked by the development of agriculture, pottery, and permanent settlements.",
                    color: "#CD853F"
                },
                {
                    name: "Bronze Age",
                    start: -3000,
                    end: -1200,
                    description: "Characterized by the use of bronze tools and weapons, and the development of early writing systems.",
                    color: "#B8860B"
                },
                {
                    name: "Iron Age",
                    start: -1200,
                    end: -500,
                    description: "Marked by the widespread use of iron for tools and weapons, and the development of complex societies.",
                    color: "#D2691E"
                },
                {
                    name: "Classical Antiquity",
                    start: -500,
                    end: 500,
                    description: "The period of cultural history between the 8th century BC and the 6th century AD centered on the Mediterranean Sea.",
                    color: "#A0522D"
                },
                {
                    name: "Medieval Period",
                    start: 500,
                    end: 1500,
                    description: "The Middle Ages, spanning from the fall of the Western Roman Empire to the Renaissance.",
                    color: "#D2B48C"
                }
            ];
            
            let timelineHtml = '';
            timelineData.forEach(era => {
                timelineHtml += `
                    <div class="timeline-era">
                        <h5>${era.name} (${era.start < 0 ? Math.abs(era.start) + ' BCE' : era.start + ' CE'} - ${era.end < 0 ? Math.abs(era.end) + ' BCE' : era.end + ' CE'})</h5>
                        <p>${era.description}</p>
                        <div style="height: 10px; background-color: ${era.color}; width: 100%; border-radius: 5px;"></div>
                    </div>
                `;
            });
            document.getElementById('timelineContent').innerHTML = timelineHtml;
            
            // Load regional finds data
            const regionalData = [
                {
                    site: "Hadrian's Wall",
                    distance: "120km away",
                    significance: "Roman defensive fortification marking the northern boundary of the Roman Empire in Britain.",
                    key_artifacts: "Roman coins, pottery, weapons, and inscriptions",
                    link: "#"
                },
                {
                    site: "Stonehenge",
                    distance: "230km away",
                    significance: "Prehistoric monument dating back to 3000 BC, likely used for ceremonial purposes.",
                    key_artifacts: "Stone tools, animal bones, pottery fragments",
                    link: "#"
                },
                {
                    site: "Vindolanda",
                    distance: "140km away",
                    significance: "Roman auxiliary fort just south of Hadrian's Wall, famous for the Vindolanda tablets.",
                    key_artifacts: "Wooden writing tablets, leather shoes, textiles",
                    link: "#"
                }
            ];
            
            let findsHtml = '';
            regionalData.forEach(site => {
                findsHtml += `
                    <div class="col-12 mb-3">
                        <div class="card site-card h-100">
                            <div class="card-body">
                                <h5 class="card-title">${site.site}</h5>
                                <h6 class="card-subtitle mb-2 text-muted">${site.distance}</h6>
                                <p class="card-text"><strong>Significance:</strong> ${site.significance}</p>
                                <p class="card-text"><strong>Key Artifacts:</strong> ${site.key_artifacts}</p>
                                <a href="${site.link}" target="_blank" class="btn btn-sm btn-outline-primary">Learn More</a>
                            </div>
                        </div>
                    </div>
                `;
            });
            document.getElementById('regionalFindsContent').innerHTML = findsHtml;
            
            // Generate PDF functionality
            document.getElementById('generatePdfBtn').addEventListener('click', function() {
                if (!currentAnalysisData) {
                    alert('Please analyze an artifact first before generating a PDF report.');
                    return;
                }
                
                // Show loading indicator
                document.getElementById('pdfLoading').style.display = 'flex';
                
                // Simulate PDF generation
                setTimeout(() => {
                    // Create a dummy blob for download
                    const blob = new Blob(["Sample PDF content would be here"], { type: 'application/pdf' });
                    
                    // Create a download link for the PDF
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = 'artifact_report.pdf';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    
                    // Hide loading indicator
                    document.getElementById('pdfLoading').style.display = 'none';
                }, 2000);
            });
        });
    </script>
</body>
>>>>>>> 0bd2f86 (Initial commit for Flask artifact app)
</html>