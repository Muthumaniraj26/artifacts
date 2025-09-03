import os
import io
import time
import torch
import torch.nn as nn
import numpy as np
from PIL import Image, UnidentifiedImageError
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from torchvision import models, transforms
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile

# ------------------------------
# Flask Setup
# ------------------------------
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  

# ------------------------------
# Model Settings
# ------------------------------
IMG_SIZE = 224
NUM_CLASSES = 9
CLASS_LABELS = [
    "alloy",
    "Bead Jewellery",
    "Blackstone",
    "Kendi",
    "Thakli",
    "huntingtool",
    "pottery",
    "shell bangle",
    "vatta_sillu"
]

DETAILS_MAP = {
    "huntingtool": {
        "description": "Tools crafted by early humans for hunting, butchering, and processing animals. This category includes a wide range of implements such as stone spearheads, arrowheads, hand axes, and scrapers.",
        "era": "Paleolithic to the Iron Age. The design and material changed significantly over time, reflecting technological advancements.",
        "material": "Commonly made from durable materials like chert, flint, obsidian, and quartzite. Later examples include bone, antler, and eventually bronze or iron.",
        "significance": "These tools are crucial for understanding the subsistence strategies, cognitive abilities, and technological skills of prehistoric societies. They provide direct evidence of human interaction with the environment.",
        "color": "#8B4513"  # SaddleBrown
    },
    "Kendi": {
        "description": "A unique spouted vessel used for drinking or pouring liquids, characterized by its round body, neck, and a mammiform spout without a handle. It is a distinctive artifact of Southeast Asian ceramic traditions.",
        "era": "Prominently from the 9th to the 19th centuries, with forms evolving across different dynasties and kingdoms.",
        "material": "Typically earthenware or stoneware, often glazed. Some high-status examples were made from precious metals like bronze or silver.",
        "significance": "Kendis were important in daily life and ceremonial rituals. Their distribution across Asia provides evidence of extensive maritime trade networks, particularly for ceramics.",
        "color": "#4682B4"  # SteelBlue
    },
    "Thakli": {
        "description": "A traditional spindle used in India for hand-spinning fibers like cotton and wool into thread. It consists of a weighted whorl attached to a shaft.",
        "era": "Ancient to modern times. Its form has remained relatively consistent for centuries.",
        "material": "The whorl is often made of stone, clay, or bone, while the shaft is typically wood or metal.",
        "significance": "The presence of Thakli whorls at an archaeological site is a strong indicator of textile production, a vital economic activity in ancient cultures.",
        "color": "#D2691E"  # Chocolate
    },
    "shell bangle": {
        "description": "Ornaments worn on the wrist, crafted from marine or freshwater shells. They were often made from a single, continuous cross-section of a large shell.",
        "era": "Widespread from the Neolithic period through the Iron Age and into historical periods. Particularly common in Harappan and Gangetic Valley cultures.",
        "material": "Most commonly made from the conch shell (Turbinella pyrum). The species of shell can indicate long-distance trade with coastal regions.",
        "significance": "Shell bangles were not just ornaments but also important cultural markers, indicating social status, marital status, and ritual roles. They are evidence of sophisticated craftsmanship and trade.",
        "color": "#20B2AA"  # LightSeaGreen
    },
    "Bead Jewellery": {
        "description": "Personal adornments such as necklaces, earrings, and pendants incorporating pearls. These were luxury items, often combined with other precious materials.",
        "era": "Ancient Roman, Indian, and Persian empires through to the medieval period. Pearls have been prized as gems for millennia.",
        "material": "Natural pearls harvested from oysters, often drilled and strung with gold, silver, or other beads.",
        "significance": "Represents wealth, high social status, and extensive trade networks. The discovery of pearl jewelry points to connections with marine environments where pearl-bearing mollusks were found.",
        "color": "#9370DB"  # MediumPurple
    },
    "alloy": {
        "description": "An object made from a mixture of metals, created to enhance properties like strength, hardness, or color. Bronze (copper and tin) and brass (copper and zinc) are common archaeological alloys.",
        "era": "The Bronze Age (c. 3300 BCE) onwards. The development of alloys marks a pivotal moment in human technological history.",
        "material": "Bronze, brass, electrum (gold and silver), and various other combinations depending on the culture and available resources.",
        "significance": "The ability to create alloys demonstrates advanced metallurgical knowledge. Alloy artifacts, such as tools, weapons, and statues, are hallmarks of complex societies.",
        "color": "#C0C0C0"  # Silver
    },
    "Blackstone": {
        "description": "Artifacts carved from dark, fine-grained rock like basalt, schist, or steatite. This includes sculptures of deities, architectural elements, and ceremonial tools.",
        "era": "Common in various periods, particularly noted in the sculptures of the Pala and Sena dynasties of Eastern India.",
        "material": "Basalt, schist, or other dense, dark stones that allow for fine carving and a polished finish.",
        "significance": "Often used for creating durable and detailed religious icons and inscriptions. The geological source of the stone can help trace ancient trade and quarrying activities.",
        "color": "#2F4F4F"  # DarkSlateGray
    },
    "vatta_sillu": {
        "description": "A type of circular grinding stone, often with a flat or slightly concave surface, used in conjunction with a smaller rolling stone (a muller) for processing food and other materials.",
        "era": "Common in domestic contexts from the Neolithic period through historical times in South Asia.",
        "material": "Hard, coarse-grained stone like granite or sandstone that provides an effective abrasive surface.",
        "significance": "A fundamental tool for food preparation, indicating a reliance on processed grains, spices, or medicinal herbs. It is a key indicator of sedentary, agricultural lifestyles.",
        "color": "#A9A9A9"  # DarkGray
    },
    "pottery": {
        "description": "Ceramic ware made from fired clay. This is one of the most common types of artifacts found, encompassing everything from simple storage jars and cooking pots to elaborately decorated ceremonial vessels.",
        "era": "From the Neolithic period (c. 10,000 BCE) onwards. It is a defining characteristic of this period.",
        "material": "Fired clay, which may be mixed with tempering agents like sand, shell, or crushed rock to prevent cracking.",
        "significance": "Pottery is invaluable for archaeologists. Its style, shape, and decoration are primary tools for dating sites and identifying different cultural groups. Chemical analysis can even reveal what the pots were used to store.",
        "color": "#CD853F"  # Peru
    }
}

# ------------------------------
# Model Definition
# ------------------------------
def create_model(num_classes: int):
    # Match exactly with model_4.py training script
    model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1)
    
    # Modify classifier to match training
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Sequential(
        nn.Linear(in_features, 512),
        nn.GELU(),
        nn.BatchNorm1d(512),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )
    return model

ckpt_path = 'artifact_with_val.pth'
if not os.path.exists(ckpt_path):
    raise FileNotFoundError(f"'{ckpt_path}' not found.")

model = create_model(NUM_CLASSES)

try:
    state = torch.load(ckpt_path, map_location='cpu')
    
    # Remove 'module.' prefix if present (for DataParallel models)
    if any(k.startswith('module.') for k in state.keys()):
        new_state = {k.replace('module.', ''): v for k, v in state.items()}
        state = new_state
    
    model.load_state_dict(state)
    model.eval()
    print("✅ Model loaded successfully")
except RuntimeError as e:
    print(f"⚠️ Model loading failed: {e}")
    print("Using random weights for demo")

# ------------------------------
# Preprocessing
# ------------------------------
image_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def read_image_from_bytes(image_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(image_bytes)).convert('RGB')

def predict_all_probs(image_bytes: bytes):
    img = read_image_from_bytes(image_bytes)
    x = image_transforms(img).unsqueeze(0)
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0]
        return probs.tolist()

def predict_topk(image_bytes: bytes, k: int = 5):
    img = read_image_from_bytes(image_bytes)
    x = image_transforms(img).unsqueeze(0)
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0]
        topk = min(k, probs.shape[0])
        conf, idx = torch.topk(probs, topk)
        conf = conf.tolist()
        idx = idx.tolist()
    return [{"class": CLASS_LABELS[i], "probability": float(c)} for c, i in zip(conf, idx)]

def create_confidence_chart(probs, filename="confidence_chart.png"):
    plt.figure(figsize=(10, 6))
    
    # Create a color for each bar based on the artifact type
    colors = [DETAILS_MAP.get(label, {}).get('color', '#3498db') for label in CLASS_LABELS]
    
    bars = plt.bar(range(len(CLASS_LABELS)), probs, color=colors)
    plt.xlabel('Artifact Classes')
    plt.ylabel('Confidence')
    plt.title('Model Confidence for Each Artifact Class')
    plt.xticks(range(len(CLASS_LABELS)), CLASS_LABELS, rotation=45, ha='right')
    plt.ylim(0, 1)
    
    # Add value labels on top of bars
    for i, v in enumerate(probs):
        if v > 0.05:  # Only label bars with significant probability
            plt.text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    chart_path = os.path.join('static', filename)
    plt.savefig(chart_path, format='png', dpi=100)
    plt.close()
    return chart_path

def generate_report(data, image_bytes, filename="artifact_report.pdf"):
    """Generate a PDF report of the artifact analysis"""
    # Create a temporary file for the PDF
    report_path = os.path.join('static', filename)
    
    # Create document
    doc = SimpleDocTemplate(report_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#3498db')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['BodyText'],
        fontSize=12,
        spaceAfter=12
    )
    
    # Story to hold flowables
    story = []
    
    # Add title
    story.append(Paragraph("Artifact Classification Report", title_style))
    story.append(Spacer(1, 12))
    
    # Add timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Report generated on: {timestamp}", normal_style))
    story.append(Spacer(1, 20))
    
    # Add classification results
    story.append(Paragraph("Classification Results", heading_style))
    
    # Add top prediction
    top_pred = data['top1']
    story.append(Paragraph(f"<b>Primary Classification:</b> {top_pred['class']} ({top_pred['probability']*100:.2f}% confidence)", normal_style))
    story.append(Spacer(1, 12))
    
    # Add all predictions in a table
    prediction_text = "<b>Top Predictions:</b><br/>"
    for i, pred in enumerate(data['top_k']):
        prediction_text += f"{i+1}. {pred['class']}: {pred['probability']*100:.2f}%<br/>"
    
    story.append(Paragraph(prediction_text, normal_style))
    story.append(Spacer(1, 20))
    
    # Add artifact details if available
    if 'details' in data:
        story.append(Paragraph("Artifact Details", heading_style))
        
        details = data['details']
        if 'description' in details:
            story.append(Paragraph(f"<b>Description:</b> {details['description']}", normal_style))
        if 'era' in details:
            story.append(Paragraph(f"<b>Historical Era:</b> {details['era']}", normal_style))
        if 'material' in details:
            story.append(Paragraph(f"<b>Material:</b> {details['material']}", normal_style))
        if 'significance' in details:
            story.append(Paragraph(f"<b>Significance:</b> {details['significance']}", normal_style))
        
        story.append(Spacer(1, 20))
    
    # Add confidence chart
    story.append(Paragraph("Confidence Distribution", heading_style))
    
    # Save the chart temporarily
    chart_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.figure(figsize=(8, 5))
    
    # Create a color for each bar based on the artifact type
    colors = [DETAILS_MAP.get(label, {}).get('color', '#3498db') for label in CLASS_LABELS]
    
    bars = plt.bar(range(len(CLASS_LABELS)), data['all_probs'], color=colors)
    plt.xlabel('Artifact Classes')
    plt.ylabel('Confidence')
    plt.title('Model Confidence for Each Artifact Class')
    plt.xticks(range(len(CLASS_LABELS)), CLASS_LABELS, rotation=45, ha='right')
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(chart_temp.name, format='png', dpi=100)
    plt.close()
    
    # Add chart to report
    story.append(ReportImage(chart_temp.name, width=6*inch, height=3.5*inch))
    story.append(Spacer(1, 20))
    
    # Add the analyzed image if available
    if image_bytes:
        story.append(Paragraph("Analyzed Image", heading_style))
        
        # Save image temporarily
        img_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        img = Image.open(io.BytesIO(image_bytes))
        img.save(img_temp.name, 'JPEG')
        
        # Add image to report
        story.append(ReportImage(img_temp.name, width=4*inch, height=3*inch))
        
        # Clean up
        os.unlink(img_temp.name)
    
    # Build PDF
    doc.build(story)
    
    # Clean up
    os.unlink(chart_temp.name)
    
    return report_path

# ------------------------------
# Routes
# ------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    if not file or file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        image_bytes = file.read()
        try:
            img = read_image_from_bytes(image_bytes)
        except UnidentifiedImageError:
            return jsonify({"error": "Invalid image file"}), 400

        top_k = predict_topk(image_bytes, k=5)
        all_probs = predict_all_probs(image_bytes)
        chart_filename = f"confidence_chart_{int(time.time())}.png"
        chart_path = create_confidence_chart(all_probs, chart_filename)

        top1 = top_k[0]
        details = DETAILS_MAP.get(top1["class"], {"description": "No details available"})

        # Generate a report
        report_filename = f"artifact_report_{int(time.time())}.pdf"
        report_path = generate_report({
            "top_k": top_k,
            "top1": top1,
            "details": details,
            "all_probs": all_probs
        }, image_bytes, report_filename)

        return jsonify({
            "top_k": top_k,
            "top1": top1,
            "details": details,
            "chart_url": f"/static/{chart_filename}",
            "report_url": f"/static/{report_filename}",
            "text_to_speech": generate_speech_text(top1, details)
        })
    except Exception as e:
        return jsonify({"error": f"Inference error: {str(e)}"}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

def generate_speech_text(top1, details):
    """Generate text for text-to-speech functionality"""
    speech_text = f"The artifact has been classified as {top1['class']} with {top1['probability']*100:.2f}% confidence. "
    
    if 'description' in details:
        speech_text += f"{details['description']} "
    
    if 'era' in details:
        speech_text += f"This artifact is from {details['era']}. "
    
    if 'material' in details:
        speech_text += f"It is typically made from {details['material']}. "
    
    if 'significance' in details:
        speech_text += f"{details['significance']}"
    
    return speech_text

# ------------------------------
if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(host='0.0.0.0', port=3000, debug=True)