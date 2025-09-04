import os
import io
import time
import math
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
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import json
from PIL import Image as PILImage, UnidentifiedImageError
# ------------------------------
# Flask Setup
# ------------------------------
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25MB

# ------------------------------
# Model Settings & Data
# ------------------------------
IMG_SIZE = 224
NUM_CLASSES = 9
CLASS_LABELS = [
    "alloy", "Bead Jewellery", "Blackstone", "Kendi", "Thakli",
    "huntingtool", "pottery", "shell bangle", "vatta_sillu"
]

DETAILS_MAP = {
    "huntingtool": {
        "description": "Tools crafted for hunting, butchering, and processing animals. This category includes implements like spearheads (e.g., Clovis points), arrowheads, hand axes (e.g., Acheulean), and scrapers.",
        "era": "Paleolithic to the Iron Age. The design and material reflect significant technological advancements over millennia.",
        "material": "Primarily durable stone like chert, flint, obsidian, and quartzite. Later examples include bone, antler, and eventually metals like bronze or iron.",
        "significance": "These tools are crucial for understanding the subsistence strategies, cognitive abilities, and technological skills of early societies. They provide direct evidence of human interaction with their environment.",
        "cultural_context": "Found globally. Specific types like Acheulean hand-axes are associated with Homo erectus, while Mousterian points are linked to Neanderthals. The development of the atlatl (spear-thrower) and the bow marked major leaps in hunting efficiency.",
        "technological_markers": "Percussion and pressure flaking (knapping), hafting techniques to attach points to shafts, use of burins for engraving."
    },
    "Kendi": {
        "description": "A unique spouted vessel for drinking or pouring, characterized by its round body and a mammiform spout without a handle. It is a distinctive artifact of Southeast Asian ceramic traditions.",
        "era": "Prominently from the 9th to the 19th centuries, with forms evolving across different dynasties and kingdoms like the Srivijaya and Majapahit empires.",
        "material": "Typically earthenware or stoneware, often with ash or celadon glazes. High-status examples were made from bronze or silver.",
        "significance": "Kendis were vital in daily life and ceremonial Hindu-Buddhist rituals. Their distribution across Asia provides evidence of extensive maritime trade networks (the 'Maritime Silk Road').",
        "cultural_context": "Strongly associated with Southeast Asia (Indonesia, Malaysia, Thailand, Vietnam) but also found in China and the Philippines. They were a major export commodity.",
        "technological_markers": "Wheel-throwing, application of glazes (celadon, ash), high-temperature kiln firing."
    },
    "Thakli": {
        "description": "A traditional, compact spindle used in India for hand-spinning fibers like cotton into thread. It consists of a weighted whorl, often at the top of the shaft.",
        "era": "Ancient to modern times. Its basic, efficient form has remained relatively consistent for centuries, found in archaeological contexts from the Indus Valley Civilization onwards.",
        "material": "The whorl is often made of stone, terracotta, or bone, while the shaft is typically wood, bamboo, or metal.",
        "significance": "The presence of Thakli whorls at a site is a strong indicator of textile production, a vital economic activity. It connects directly to the long history of cotton cultivation in the Indian subcontinent.",
        "cultural_context": "Primarily associated with India. It was famously promoted by Mahatma Gandhi as a symbol of self-reliance (Swadeshi) during the independence movement.",
        "technological_markers": "Carving/shaping of whorl material, drilling of central hole, attachment to a straight shaft."
    },
    "shell bangle": {
        "description": "Ornaments for the wrist, crafted from marine or freshwater shells, often as a single, continuous cross-section of a large conch shell.",
        "era": "Widespread from the Neolithic period through the Iron Age and into historical periods. Particularly prominent in the Indus Valley (Harappan) Civilization.",
        "material": "Most commonly made from the conch shell (Turbinella pyrum), which indicates long-distance trade between coastal regions and inland settlements like Harappa and Mohenjo-Daro.",
        "significance": "Shell bangles were important cultural markers of social status, marital status (chura), and ritual purity. Workshops for their production have been excavated, indicating organized craft industries.",
        "cultural_context": "Strongly associated with the Indian subcontinent. In modern Hinduism, shell bangles (Shankha) are worn by married women in regions like Bengal and Odisha as a sign of matrimony.",
        "technological_markers": "Sawing the conch shell using bronze or stone tools, grinding to shape, polishing for a smooth finish."
    },
    "Bead Jewellery": {
        "description": "Personal adornments like necklaces, earrings, and pendants made from drilled beads. These were often luxury items, reflecting the aesthetic values and technological skills of a culture.",
        "era": "Found from the Upper Paleolithic period onwards. Specific materials and techniques are hallmarks of different eras, such as faience beads in ancient Egypt or carnelian beads in the Indus Valley.",
        "material": "A vast range of materials including stone (carnelian, agate, lapis lazuli), shell, bone, terracotta, faience, glass, and precious metals.",
        "significance": "Represents wealth, social status, and extensive trade networks. The origin of materials like lapis lazuli (from modern Afghanistan) found in Mesopotamia or Egypt highlights ancient global trade.",
        "cultural_context": "A universal human artifact. The 'dancing girl' statue from Mohenjo-Daro is famously adorned with bangles, and Egyptian pharaohs like Tutankhamun were buried with elaborate beaded collars.",
        "technological_markers": "Drilling (using bow drills), polishing, faceting of hard stones, glassmaking (faience), stringing."
    },
    "alloy": {
        "description": "An object made from a mixture of metals, created to enhance properties like strength, hardness, or color. Bronze (copper and tin) and brass (copper and zinc) are the most common archaeological alloys.",
        "era": "The Bronze Age (c. 3300 BCE) onwards. The development of alloys marks a pivotal moment in human technological history, ending the Stone Age.",
        "material": "Bronze, brass, electrum (gold and silver), and arsenical copper. The specific 'recipe' for an alloy can be a cultural or regional signature.",
        "significance": "The ability to create alloys demonstrates advanced metallurgical knowledge. Alloy artifacts, such as tools, weapons (e.g., the Luristan bronzes), and statues (e.g., the Greek Riace bronzes), are hallmarks of complex societies.",
        "cultural_context": "The Bronze Age revolution occurred independently in multiple regions, including the Near East, the Aegean, China, and the Indus Valley. The control of tin and copper resources often drove conflict and trade.",
        "technological_markers": "Smelting of ores, lost-wax casting (cire perdue) for complex shapes, hammering (annealing), riveting."
    },
    "Blackstone": {
        "description": "Artifacts carved from dark, fine-grained rock like basalt, schist, or steatite. This includes sculptures of deities, architectural elements, and ceremonial items like the Rosetta Stone.",
        "era": "Common in various periods, particularly noted in the sculptures of the Pala and Sena dynasties of Eastern India (c. 750-1200 AD) and in ancient Egypt.",
        "material": "Basalt, schist, diorite, or other dense, dark stones that allow for fine carving and a high polish. The choice of stone was often symbolic.",
        "significance": "Used for creating durable and detailed religious icons and important inscriptions. The Code of Hammurabi is famously inscribed on a basalt stele. The geological source of the stone can help trace ancient quarrying and trade.",
        "cultural_context": "Prominent in Egyptian statuary (for its association with Osiris and the fertile black land of the Nile), Mesopotamian steles, and the intricate temple sculptures of the Pala Empire in Bengal and Bihar.",
        "technological_markers": "Quarrying large stone blocks, intricate carving with metal chisels and drills, abrasive polishing for a glossy finish."
    },
    "vatta_sillu": {
        "description": "A type of circular or rectangular grinding stone slab, used with a smaller rolling stone (a muller) for processing food and other materials. Known locally in Tamil Nadu as 'Ammi Kallu'.",
        "era": "Common in domestic contexts from the Neolithic period through historical times, especially in South Asia and Southeast Asia.",
        "material": "Hard, coarse-grained stone like granite or sandstone that provides an effective abrasive surface for grinding.",
        "significance": "A fundamental tool for food preparation, indicating a reliance on processed grains, spices, or medicinal herbs. It is a key indicator of sedentary, agricultural lifestyles and specific culinary traditions.",
        "cultural_context": "A cornerstone of traditional South Indian and Southeast Asian kitchens for grinding spice pastes (masalas) and wet batters. Its presence signifies a specific type of food culture.",
        "technological_markers": "Pecking and grinding stone to create a flat or concave surface, shaping the muller for an ergonomic grip."
    },
    "pottery": {
        "description": "Ceramic ware made from fired clay. It is one of the most common archaeological artifacts, encompassing everything from simple storage jars to elaborately decorated ceremonial vessels.",
        "era": "From the Neolithic period (c. 10,000 BCE) onwards. The invention of pottery is a defining characteristic of this period, signifying a shift to more sedentary lifestyles.",
        "material": "Fired clay, which may be mixed with tempering agents like sand, shell, or crushed rock (grog) to prevent cracking during firing.",
        "significance": "Pottery is invaluable for archaeologists. Its style (e.g., Greek black-figure vs. red-figure), shape, and decoration are primary tools for dating sites and identifying different cultural groups. Residue analysis can reveal what the pots stored.",
        "cultural_context": "Every culture develops distinctive pottery styles, from the Jōmon pottery of Japan to the Mimbres pottery of the American Southwest. The invention of the potter's wheel and high-temperature kilns were major technological innovations.",
        "technological_markers": "Coiling, pinching, or wheel-throwing techniques; surface treatments like burnishing or applying slips; kiln or pit firing."
    }
}

TIMELINE_ERAS = [
    {"name": "Neolithic", "start": -10000, "end": -4500, "color": "#a3be8c", "description": "The 'New Stone Age', marked by the dawn of agriculture and permanent settlements.", "events": [{"year": -9000, "event": "Domestication of wheat and barley in the Fertile Crescent."}]},
    {"name": "Chalcolithic", "start": -4500, "end": -3300, "color": "#d08770", "description": "The 'Copper Age', a transitional period where copper metallurgy was first developed alongside stone tools.", "events": [{"year": -4000, "event": "Development of early copper smelting in the Balkans and Near East."}]},
    {"name": "Bronze Age", "start": -3300, "end": -1200, "color": "#b48ead", "description": "Characterized by the use of bronze, the development of writing, and the rise of early cities.", "events": [{"year": -2560, "event": "Completion of the Great Pyramid of Giza in Egypt."}]},
    {"name": "Iron Age", "start": -1200, "end": -550, "color": "#4c566a", "description": "Widespread adoption of iron metallurgy, leading to more advanced tools and larger empires.", "events": [{"year": -776, "event": "First recorded Olympic Games in Greece."}]},
    {"name": "Ancient Egypt", "start": -3100, "end": -30, "color": "#ebcb8b", "description": "A major civilization in North Africa, known for pyramids, pharaohs, and hieroglyphs.", "events": [{"year": -1332, "event": "Tutankhamun reigns as Pharaoh."}]},
    {"name": "Indus Valley Civ.", "start": -3300, "end": -1300, "color": "#bf616a", "description": "A Bronze Age civilization in South Asia with advanced urban planning and trade networks.", "events": [{"year": -2600, "event": "Mature Harappan phase begins; cities like Mohenjo-Daro thrive."}]},
    {"name": "Norte Chico Civ.", "start": -3500, "end": -1800, "color": "#81a1c1", "description": "The oldest known civilization in the Americas, located in modern-day Peru, notable for its large-scale architecture.", "events": [{"year": -3000, "event": "Construction of major ceremonial pyramids at Caral."}]},
    {"name": "Kingdom of Kush (Africa)", "start": -1070, "end": 350, "color": "#d08770", "description": "An ancient kingdom in Nubia (modern Sudan) that controlled vast trade routes and even conquered Egypt to rule as its 25th Dynasty.", "events": [{"year": -728, "event": "Kushite King Piye conquers Egypt."}]},
    {"name": "Olmec Civ. (Mesoamerica)", "start": -1500, "end": -400, "color": "#a3be8c", "description": "The first major Mesoamerican civilization, known for their colossal carved stone heads.", "events": [{"year": -1200, "event": "Major Olmec center of San Lorenzo flourishes."}]},
    {"name": "Archaic/Classical Greece", "start": -800, "end": -323, "color": "#81a1c1", "description": "A period of immense cultural achievement in philosophy, art, and politics that formed the foundation of Western civilization.", "events": [{"year": -431, "event": "Start of the Peloponnesian War between Athens and Sparta."}]},
    {"name": "Roman Republic/Empire", "start": -509, "end": 476, "color": "#a3be8c", "description": "Grew from a city-state into a vast empire dominating the Mediterranean.", "events": [{"year": -44, "event": "Assassination of Julius Caesar."}]},
    {"name": "Mauryan Empire (India)", "start": -322, "end": -185, "color": "#ebcb8b", "description": "The first large-scale empire in India, reaching its peak under Ashoka the Great.", "events": [{"year": -261, "event": "The Kalinga War, after which Ashoka converts to Buddhism."}]},
    {"name": "Qin/Han Dynasty (China)", "start": -221, "end": 220, "color": "#bf616a", "description": "The unification of China under the Qin and the long-lasting cultural and political foundation laid by the Han.", "events": [{"year": -210, "event": "Construction of the Terracotta Army for Emperor Qin Shi Huang."}]},
    {"name": "Classical Maya", "start": 250, "end": 900, "color": "#d08770", "description": "A flourishing period for the Maya civilization, with major advancements in writing, mathematics, and astronomy in Mesoamerica.", "events": [{"year": 750, "event": "Peak of urbanism with cities like Tikal and Calakmul."}]},
    {"name": "Gupta Empire (India)", "start": 320, "end": 550, "color": "#ebcb8b", "description": "Considered the 'Golden Age' of India, with significant achievements in science, mathematics (including the concept of zero), and art.", "events": [{"year": 499, "event": "Mathematician Aryabhata writes the Aryabhatiya."}]},
    {"name": "Byzantine Empire", "start": 330, "end": 1453, "color": "#b48ead", "description": "The Eastern Roman Empire, which preserved Greco-Roman culture for a thousand years after the fall of Rome.", "events": [{"year": 537, "event": "Completion of the Hagia Sophia in Constantinople."}]},
    {"name": "Islamic Golden Age", "start": 750, "end": 1258, "color": "#a3be8c", "description": "A period of cultural, economic, and scientific flourishing in the history of Islam.", "events": [{"year": 830, "event": "The House of Wisdom is established in Baghdad."}]},
    {"name": "Chola Dynasty (S. India)", "start": 848, "end": 1279, "color": "#d08770", "description": "A powerful South Indian dynasty renowned for its maritime trade and magnificent temples.", "events": [{"year": 1010, "event": "Completion of the Brihadisvara Temple in Thanjavur."}]},
    {"name": "Mongol Empire", "start": 1206, "end": 1368, "color": "#4c566a", "description": "The largest contiguous land empire in history, founded by Genghis Khan.", "events": [{"year": 1279, "event": "Kublai Khan completes the conquest of China."}]},
    {"name": "Renaissance (Europe)", "start": 1300, "end": 1600, "color": "#bf616a", "description": "A fervent period of European cultural, artistic, political and economic 'rebirth' following the Middle Ages.", "events": [{"year": 1503, "event": "Leonardo da Vinci begins painting the Mona Lisa."}]},
    {"name": "Inca Empire", "start": 1438, "end": 1533, "color": "#81a1c1", "description": "The largest empire in pre-Columbian America, centered in the Andes mountains.", "events": [{"year": 1450, "event": "Construction of Machu Picchu begins."}]},
    {"name": "Ottoman Empire", "start": 1299, "end": 1922, "color": "#b48ead", "description": "A Turkish empire that controlled much of Southeast Europe, Western Asia, and North Africa.", "events": [{"year": 1453, "event": "Mehmed the Conqueror captures Constantinople."}]},
    {"name": "Mughal Empire (India)", "start": 1526, "end": 1857, "color": "#8fbcbb", "description": "An empire that ruled most of the Indian subcontinent, known for its rich art and architecture.", "events": [{"year": 1653, "event": "Completion of the Taj Mahal in Agra."}]},
    {"name": "Industrial Revolution", "start": 1760, "end": 1900, "color": "#5e81ac", "description": "A period of major technological and socioeconomic change that began in Great Britain.", "events": [{"year": 1769, "event": "James Watt patents his improved steam engine."}]},
]

REGIONAL_FINDS = [
    {
        "site": "Keezhadi / Keeladi (கீழடி)",
        "distance": "Approx. 95 km from Rajapalayam",
        "significance": "A major Sangam-era (c. 6th century BCE to 1st century CE) urban settlement on the banks of the Vaigai river. The excavations have pushed back the known history of urbanism in Tamil Nadu by several centuries.",
        "key_artifacts": "Tamil-Brahmi inscribed pottery, terracotta figurines, glass beads, shell bangles, brick structures, and evidence of a sophisticated water management system. It showcases a highly literate and advanced society.",
        "link": "https://en.wikipedia.org/wiki/Keeladi_excavation_site"
    },
    {
        "site": "Adichanallur (ஆதிச்சநல்லூர்)",
        "distance": "Approx. 120 km from Rajapalayam",
        "significance": "An extensive Iron Age (c. 900 BCE - 200 BCE) urn-burial site. It's one of the most important archaeological sites in Southern India, providing crucial insights into ancient Tamil burial customs and metallurgy.",
        "key_artifacts": "Innumerable pottery urns containing human skeletons, bronze and iron objects (daggers, swords), gold diadems, and pottery with early Tamil-Brahmi script.",
        "link": "https://en.wikipedia.org/wiki/Adichanallur"
    },
    {
        "site": "Sittanavasal Cave (சித்தன்னவாசல்)",
        "distance": "Approx. 160 km from Rajapalayam",
        "significance": "A 2nd-century Jain complex of caves. It's famous for its stunning fresco paintings, which are among the most important examples of early Indian mural art, second only to the Ajanta Caves.",
        "key_artifacts": "The cave temple (Arivar Kovil) features beautiful paintings of a lotus pond, dancers, and celestial figures, reflecting the artistic achievements of the Pandyan kingdom.",
        "link": "https://en.wikipedia.org/wiki/Sittanavasal_Cave"
    }
]

# ------------------------------
# Model Definition & Loading
# ------------------------------
def create_model(num_classes: int):
    model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1)
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
    if any(k.startswith('module.') for k in state.keys()):
        state = {k.replace('module.', ''): v for k, v in state.items()}
    model.load_state_dict(state)
    model.eval()
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"⚠️ Model loading failed: {e}. Using random weights for demo.")

# ------------------------------
# Preprocessing & Prediction Functions
# ------------------------------
image_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])
def read_image_from_bytes(image_bytes: bytes) -> PILImage.Image:
    return PILImage.open(io.BytesIO(image_bytes)).convert('RGB')

def predict_topk(image_bytes: bytes, k: int = 5):
    img = read_image_from_bytes(image_bytes)
    x = image_transforms(img).unsqueeze(0)
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0]
        topk = min(k, probs.shape[0])
        conf, idx = torch.topk(probs, topk)
        return [{"class": CLASS_LABELS[i], "probability": float(c)} for c, i in zip(conf.tolist(), idx.tolist())]

def create_confidence_chart(probs, filename="confidence_chart.png"):
    plt.figure(figsize=(10, 6))
    colors = plt.cm.Blues(np.array(probs) * 0.8 + 0.2)
    plt.bar(range(len(CLASS_LABELS)), probs, color=colors)
    plt.xlabel('Artifact Classes')
    plt.ylabel('Confidence')
    plt.title('Model Confidence for Each Artifact Class')
    plt.xticks(range(len(CLASS_LABELS)), CLASS_LABELS, rotation=45, ha='right')
    plt.ylim(0, 1)
    for i, v in enumerate(probs):
        plt.text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom', fontsize=8)
    plt.tight_layout()
    chart_path = os.path.join('static', filename)
    plt.savefig(chart_path, format='png', dpi=100)
    plt.close()
    return chart_path

def predict_all_probs(image_bytes: bytes):
    img = read_image_from_bytes(image_bytes)
    x = image_transforms(img).unsqueeze(0)
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0]
        return probs.tolist()

# ------------------------------
# Routes
# ------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST', 'HEAD'])
def predict():
    if request.method == 'HEAD':
        return '', 200

    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    if not file or file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        image_bytes = file.read()
        try:
            read_image_from_bytes(image_bytes)
        except UnidentifiedImageError:
            return jsonify({"error": "Invalid image file"}), 400

        top_k = predict_topk(image_bytes, k=5)
        all_probs = predict_all_probs(image_bytes)

        chart_filename = f"confidence_chart_{int(time.time())}.png"
        create_confidence_chart(all_probs, chart_filename)

        top1 = top_k[0]
        details = DETAILS_MAP.get(top1["class"], {"description": "No details available"})

        # Add carbon dating data if available
        c14_data = request.form.get('c14_data')
        if c14_data:
            try:
                c14_data = json.loads(c14_data)
            except:
                c14_data = None

        return jsonify({
            "top_k": top_k,
            "top1": top1,
            "details": details,
            "chart_url": f"/static/{chart_filename}",
            "c14_data": c14_data
        })
    except Exception as e:
        return jsonify({"error": f"Inference error: {str(e)}"}), 500

@app.route('/calculate_c14_age', methods=['POST'])
def calculate_c14_age():
    data = request.get_json()
    c14_percentage = data.get('c14_percentage')

    if c14_percentage is None or not (0 < c14_percentage <= 100):
        return jsonify({"error": "Invalid C14 percentage. Must be > 0 and <= 100."}), 400
    
    try:
        C14_CONSTANT = 8267
        age_bp = -C14_CONSTANT * math.log(c14_percentage / 100.0)
        calendar_year = 1950 - age_bp
        
        return jsonify({
            'age_bp': round(age_bp),
            'calendar_year': round(calendar_year),
            'original_percentage': c14_percentage
        })
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500

@app.route('/timeline_eras', methods=['GET'])
def get_timeline_eras():
    sorted_eras = sorted(TIMELINE_ERAS, key=lambda x: x['start'])
    return jsonify(sorted_eras)

@app.route('/regional_finds', methods=['GET'])
def get_regional_finds():
    return jsonify(REGIONAL_FINDS)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Create a PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['BodyText'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        small_style = ParagraphStyle(
            'CustomSmall',
            parent=styles['BodyText'],
            fontSize=9,
            spaceAfter=4
        )
        
        # Story to hold content
        story = []
        
        # Title
        story.append(Paragraph("Archaeological Artifact Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Top Prediction
        top1 = data.get('top1', {})
        if top1:
            story.append(Paragraph(f"Primary Identification: <b>{top1.get('class', 'Unknown')}</b>", heading_style))
            story.append(Paragraph(f"Confidence: {top1.get('probability', 0)*100:.2f}%", normal_style))
            story.append(Spacer(1, 10))
        
        # Confidence Chart
        chart_url = data.get('chart_url', '')
        if chart_url:
            try:
                chart_path = os.path.join(app.static_folder, chart_url.split('/')[-1])
                if os.path.exists(chart_path):
                    img = Image(chart_path, width=6*inch, height=4*inch)
                    story.append(img)
                    story.append(Spacer(1, 15))
            except:
                pass
        
        # Detailed Information
        details = data.get('details', {})
        if details:
            story.append(Paragraph("Detailed Artifact Information", heading_style))
            
            detail_items = [
                ("Description", details.get('description', 'N/A')),
                ("Historical Era", details.get('era', 'N/A')),
                ("Material Composition", details.get('material', 'N/A')),
                ("Cultural Significance", details.get('significance', 'N/A')),
                ("Cultural Context", details.get('cultural_context', 'N/A')),
                ("Technological Markers", details.get('technological_markers', 'N/A'))
            ]
            
            for title, content in detail_items:
                if content != 'N/A':
                    story.append(Paragraph(f"<b>{title}:</b>", normal_style))
                    story.append(Paragraph(content, small_style))
                    story.append(Spacer(1, 8))
        
        # All Predictions Table
        top_k = data.get('top_k', [])
        if top_k:
            story.append(PageBreak())
            story.append(Paragraph("Complete Classification Results", heading_style))
            
            # Create table data
            table_data = [['Rank', 'Artifact Type', 'Confidence']]
            for i, prediction in enumerate(top_k, 1):
                table_data.append([
                    str(i),
                    prediction.get('class', 'Unknown'),
                    f"{prediction.get('probability', 0)*100:.2f}%"
                ])
            
            # Create table
            table = Table(table_data, colWidths=[1*inch, 3*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Finds Near Me Section
        story.append(Paragraph("Archaeological Sites Near Rajapalayam, Tamil Nadu", heading_style))
        story.append(Paragraph("Explore these significant archaeological sites in the region:", normal_style))
        story.append(Spacer(1, 10))
        
        for i, site in enumerate(REGIONAL_FINDS, 1):
            story.append(Paragraph(f"<b>{i}. {site['site']}</b>", normal_style))
            story.append(Paragraph(f"<i>Distance: {site['distance']}</i>", small_style))
            story.append(Paragraph(f"<b>Significance:</b> {site['significance']}", small_style))
            story.append(Paragraph(f"<b>Key Artifacts:</b> {site['key_artifacts']}", small_style))
            story.append(Spacer(1, 12))
        
        # Carbon Dating Results (if available)
        c14_data = data.get('c14_data')
        if c14_data:
            story.append(PageBreak())
            story.append(Paragraph("Carbon-14 Dating Analysis", heading_style))
            story.append(Paragraph(f"Original C14 Percentage: {c14_data.get('original_percentage', 'N/A')}%", normal_style))
            story.append(Paragraph(f"Calculated Age (BP): {c14_data.get('age_bp', 'N/A')} years", normal_style))
            story.append(Paragraph(f"Calendar Year: {c14_data.get('calendar_year', 'N/A')} CE/BCE", normal_style))
            story.append(Spacer(1, 10))
            
            # Add timeline context
            story.append(Paragraph("Historical Context:", heading_style))
            story.append(Paragraph("This date places your artifact within the following historical periods:", normal_style))
        
        # Footer with timestamp
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Report generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}", small_style))
        story.append(Paragraph("Generated by Archaeological Artifact Identification System", small_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Return as response
        response = app.response_class(
            response=pdf_content,
            status=200,
            mimetype='application/pdf'
        )
        response.headers['Content-Disposition'] = 'attachment; filename=artifact_report.pdf'
        return response
        
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

# ------------------------------
# Main Execution
# ------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)