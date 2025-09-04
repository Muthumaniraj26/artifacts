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

DETAILS_MAP= {
    "huntingtool": {
        "description": """This category covers a wide range of tools for hunting and processing animals. Early examples include simple Oldowan choppers and all-purpose Acheulean hand-axes for butchering and digging. Later, technology got more specialized, leading to refined points like Mousterian points (Neanderthals) and large, fluted Clovis points used to hunt mammoths. Smaller microliths were often combined to make composite tools like barbed harpoons. Scrapers were essential for cleaning hides, while sharp burins were used to carve bone and antler.""",
        "era": """The timeline for hunting tools spans over 2.5 million years. The Lower Paleolithic is defined by Oldowan and Acheulean tools. The Middle Paleolithic (c. 300,000–40,000 years ago) is known for more advanced toolkits like the Mousterian, made using the prepared-core Levallois technique. The Upper Paleolithic (c. 40,000–10,000 years ago) brought a technological revolution with the atlatl (spear-thrower) and the bow and arrow, which dramatically improved hunting power and range.""",
        "material": """Stone choice was key. Flint, chert, and obsidian were prized for their predictable conchoidal fracture, which creates razor-sharp edges. Obsidian, a volcanic glass, makes an edge sharper than a modern scalpel. Later, bone, ivory, and antler were carved into deadly harpoons and points. The Bronze and Iron Ages introduced durable metal spearheads and arrowheads that could be reshaped.""",
        "significance": """These tools are a direct window into early human diet, intelligence, and behavior. The standardization of complex tools suggests abstract thought and teaching. Tool marks on ancient animal bones help us reconstruct food chains and differentiate between hunting and scavenging. The spread of specific tool types also helps us map early human migrations.""",
        "cultural_context": """Specific toolkits are signatures of different hominin species. Oldowan choppers are linked to Homo habilis, while the Acheulean hand-axe is the hallmark of Homo erectus. The Mousterian industry is famously associated with Neanderthals. The explosion of innovation in the Upper Paleolithic, including blades and bone tools, is tied to the arrival of our species, Homo sapiens.""",
        "technological_markers": """The main process is knapping (stone shaping). Percussion flaking uses a hammerstone to remove large flakes. Pressure flaking, a more precise method, uses a pointed tool to press off small flakes for final shaping. A huge cognitive leap was hafting—attaching a stone point to a wooden shaft using adhesives like birch-bark tar and bindings like animal sinew."""
    },
    "Kendi": {
        "description": """A Kendi is a unique handleless water vessel, defined by its globular body, a neck for filling, and a distinctive mammiform (breast-shaped) spout. This design allows for pouring or drinking without the user's lips touching the spout, a hygienic feature ideal for communal or ritual use.""",
        "era": """The Kendi's prominence grew with the great maritime empires of Southeast Asia. Early forms appear during the Srivijayan Empire (7th-13th centuries), but production and trade peaked during the Majapahit Empire in Indonesia (13th-16th centuries) and in the prolific kilns of Siam (Thailand) and Vietnam.""",
        "material": """Common Kendis were made of earthenware or high-fired stoneware. Vietnamese and Thai kilns were renowned for their exquisite celadon-glazed Kendis. Chinese artisans also produced porcelain Kendis for the Southeast Asian market. For royalty, luxurious Kendis were cast from bronze or crafted from silver.""",
        "significance": """The Kendi is a key index fossil for tracing the ancient Maritime Silk Road. Finding Kendis in archaeological sites from Japan to eastern Africa maps the vast trade networks that connected Southeast Asia to the wider world. Ritually, it was used to pour sacred water in Hindu-Buddhist ceremonies.""",
        "cultural_context": """Deeply embedded in Southeast Asian culture, the Kendi is depicted in temple carvings, such as the famous reliefs at Borobudur in Java. It was a vital object in rites of passage, purification ceremonies, and daily life. Its heartland is Indonesia, Malaysia, and Thailand.""",
        "technological_markers": """High-quality Kendis were wheel-thrown, allowing for precise and elegant forms. The application of glazes, especially celadon, required sophisticated chemical knowledge and precise control of the kiln's atmosphere (a low-oxygen, or 'reduction,' atmosphere). Firing to stoneware temperatures (over 1200°C) required advanced kiln construction."""
    },
    "Thakli": {
        "description": """A Thakli is a type of drop spindle, a simple and ancient tool for spinning fibers like cotton and wool into thread. It consists of a slender shaft and a weighted whorl. The whorl acts as a flywheel, its momentum maintaining the spin as the user drafts fibers, which are twisted into a continuous thread.""",
        "era": """The spindle whorl is a universal indicator of textile production, with examples found in Neolithic sites globally. In India, terracotta whorls are common artifacts at Indus Valley Civilization sites like Harappa (c. 2500 BCE), pointing to a well-established cotton industry. Its efficient design has remained virtually unchanged for millennia.""",
        "material": """The whorl is the most durable part and is what archaeologists typically find. They were commonly made of fired clay (terracotta), carved stone, or bone. The shaft, being made of perishable wood or bamboo, rarely survives in the archaeological record.""",
        "significance": """Finding a spindle whorl is direct evidence of a textile economy. It implies the cultivation of plants like cotton, the herding of sheep for wool, and the existence of looms for weaving cloth. Textiles were a hugely important economic product, and the Thakli represents the fundamental technology that started it all.""",
        "cultural_context": """The Thakli is intrinsically linked to India's long history of cotton textiles. Mahatma Gandhi famously promoted the spinning wheel (Charkha, a more mechanized version of the spindle) as a potent symbol of Swadeshi (self-reliance) and economic freedom from colonial Britain.""",
        "technological_markers": """The technology lies in its elegant physics. The whorl must be well-balanced and have a drilled central hole to spin true without wobbling. Its weight and diameter determine the speed of the spin and the thickness of the thread produced. The shaft must be straight and smooth for even winding."""
    },
    "shell bangle": {
        "description": """These are rigid bracelets masterfully cut from the thick wall of a large marine conch shell. Unlike beaded bracelets, these are typically crafted as a single, solid, continuous ring of shell, which requires immense skill to produce without breaking.""",
        "era": """While shell ornaments are ancient, the large-scale, organized industry of producing bangles from conch shells was a hallmark of the Indus Valley (Harappan) Civilization (c. 2600-1900 BCE).""",
        "material": """The premier material used in the Indian subcontinent was the sacred conch shell, Turbinella pyrum. This robust, thick-walled shell was sourced from the coasts of Gujarat. The presence of these bangles at inland cities like Harappa and Mohenjo-Daro is clear evidence of sophisticated internal trade networks.""",
        "significance": """Shell bangles were powerful status symbols, signifying wealth, social rank, and ritual purity. Specialized workshops have been excavated at coastal sites like Nageshwar and Balakot, containing stockpiles of raw shells, manufacturing waste, and finished bangles, pointing to an organized craft production.""",
        "cultural_context": """The conch shell (Shankha) holds deep religious significance in Hinduism. In modern India, especially in Bengal and Odisha, married women wear white conch shell bangles (Shankha) paired with red coral or lac bangles (Pola) as a symbol of their marital status, a direct cultural echo of ancient traditions.""",
        "technological_markers": """The production process was multi-staged and required great precision. First, a hollow-bladed bronze saw was used to carefully cut a rough circlet from the main body of the conch. The rough ring was then painstakingly ground into its final shape using abrasives and finally polished to a high sheen."""
    },
    "Bead Jewellery": {
        "description": """This category covers all forms of personal adornment made by stringing perforated beads, including necklaces, collars, bracelets, belts, and headdresses. Beads are one of humanity's oldest forms of art and symbolic communication.""",
        "era": """The earliest known beads are over 100,000 years old. The Bronze Age saw the mastery of hardstone working, producing exquisite etched carnelian beads in the Indus Valley and intricate faience (a type of proto-glass) collars in Egypt. The Roman era perfected glass-making.""",
        "material": """The range of materials is vast, including organic materials like shell, bone, and ivory, and common stones like terracotta and soapstone. High-status jewellery used semi-precious stones like deep red carnelian, banded agate, and the brilliant blue lapis lazuli. Precious metals like gold and silver were also used.""",
        "significance": """Beads are treasure troves of information. The technology used to make them reveals a society's sophistication. Most importantly, beads are a primary indicator of long-distance trade. The presence of lapis lazuli, sourced exclusively from Afghanistan, in the tombs of Egyptian Pharaohs is proof of ancient global trade.""",
        "cultural_context": """Beads are a universal cultural phenomenon. The Harappan civilization was famous for its mass-produced, long barrel-shaped carnelian beads. The famous 'Dancing Girl' bronze statue from Mohenjo-Daro is depicted wearing a stack of bangles. In ancient Egypt, the elite were buried with magnificent beaded collars, best exemplified by the treasures in the tomb of Tutankhamun.""",
        "technological_markers": """The critical technology was drilling holes through often very hard materials, accomplished using a bow drill. Polishing was done with fine abrasives to create a lustrous surface. Faceting hard stones and the complex pyrotechnology of glassmaking and faience production were other key markers of advanced societies."""
    },
    "alloy": {
        "description": """An object made from an alloy—a deliberate mixture of two or more metals—to create a new material with enhanced properties like greater hardness or a lower melting point. The most significant archaeological alloys are bronze (copper mixed with tin) and brass (copper mixed with zinc).""",
        "era": """The development of bronze around 3300 BCE was so revolutionary that it gave its name to an entire epoch: the Bronze Age. This period marks a pivotal moment when societies moved beyond stone to create the first high-performance artificial material.""",
        "material": """Bronze was the primary alloy of antiquity. Adding about 10% tin to copper creates a metal that is significantly harder and easier to cast. Arsenical copper was an early form of bronze. Brass became more common in the Roman period. Electrum, a natural alloy of gold and silver, was used for the first coins.""",
        "significance": """The ability to create alloys demonstrates a profound understanding of metallurgy. Bronze enabled the creation of superior tools (stronger axes) and weapons (durable swords) that gave their owners a significant advantage. This technological superiority is a hallmark of complex societies.""",
        "cultural_context": """The Bronze Age revolution was a global phenomenon, occurring independently in the Near East, the Aegean, the Indus Valley, and China. Because the key ingredients, copper and especially tin, are rarely found together, the production of bronze fueled the creation of vast international trade networks.""",
        "technological_markers": """Advanced metallurgical skills were required. Smelting was the process of extracting metal from its ore. Lost-wax casting (cire perdue) was a sophisticated technique for creating complex, hollow shapes. Hammering and annealing (heating and slow cooling) were used to shape and harden the metal."""
    },
    "Blackstone": {
        "description": """This category refers to artifacts carved from dense, dark, fine-grained rocks like basalt, schist, or steatite (soapstone). The fine grain of these stones allows for the carving of incredibly intricate details and a high polish. Artifacts include statues, architectural elements, and inscribed steles like the Rosetta Stone.""",
        "era": """Blackstone was used in many periods but is particularly characteristic of certain powerful dynasties. It was a favored material in Ancient Egypt and for the inscribed law codes of Mesopotamia. The art of blackstone sculpture reached a zenith in Eastern India under the Pala and Sena dynasties (c. 750-1200 AD).""",
        "material": """Basalt and diorite are hard, durable volcanic rocks capable of taking a very high polish. Schist is a metamorphic rock that is slightly softer and easier to carve, making it ideal for extremely detailed sculptures. The choice of dark stone was often symbolic, representing eternity or fertility.""",
        "significance": """The durability of blackstone made it the ideal medium for creating eternal images of deities and for recording permanent laws and histories. The Code of Hammurabi, one of the world's oldest deciphered law codes, is famously carved onto a tall basalt stele. Geochemical analysis of the stone can trace it back to its specific quarry.""",
        "cultural_context": """In Egypt, the color black was associated with Osiris, the god of the afterlife, and the fertile black silt of the Nile River. In Mesopotamia, it conveyed timeless authority. The Pala Empire, centered in Bengal and Bihar, was a major center of Mahayana Buddhism and produced countless intricate sculptures of Buddhas and Bodhisattvas from black schist.""",
        "technological_markers": """The process began with quarrying massive blocks of stone. The intricate details were achieved by carving with hardened metal chisels and drills. The final stage involved laborious abrasive polishing, using sand and water to rub the surface until it achieved a deep, glossy finish."""
    },
    "vatta_sillu": {
        "description": """A vatta sillu or Ammi Kallu is a traditional grinding stone set, fundamental to South Indian and Southeast Asian kitchens. It consists of a large, flat stone slab (ammi) and a smaller, cylindrical rolling pestle (kuzhavi or muller), used to grind ingredients into fine pastes.""",
        "era": """Simple grinding stones (saddle querns) appeared in the Neolithic period with the advent of agriculture. This specific flat-bed form has been a staple in South Asian domestic settings for centuries, representing a long, continuous culinary tradition.""",
        "material": """The stones are made from hard, coarse-grained rock, typically granite or sandstone. The coarse texture is essential as it provides the necessary friction and abrasive surface to efficiently break down ingredients.""",
        "significance": """This tool is a key indicator of culinary traditions based on freshly ground spices and wet batters. Unlike a mortar and pestle (for pounding), the ammi kallu is for grinding, essential for making the smooth masala pastes for many South Indian curries and batters for dishes like dosa and idli.""",
        "cultural_context": """The ammi kallu is the heart of the traditional South Indian kitchen, located here in Tamil Nadu. The rhythmic sound of grinding is an iconic part of domestic life. It also plays a role in rituals, sometimes worshipped as a household deity or used in wedding ceremonies as a symbol of stability.""",
        "technological_markers": """The technology lies in shaping the hard stone. The flat slab's surface was often prepared by pecking it with a harder stone to create a rough, effective grinding surface. This pecking would be repeated periodically as the stone became smooth with use. The muller was shaped to be ergonomic for a comfortable grip."""
    },
    "pottery": {
        "description": """Pottery refers to any object made from clay that has been hardened by firing. As one of the most common and durable artifacts, it includes everything from simple cooking pots and large storage jars to highly decorated ceremonial vessels.""",
        "era": """The invention of pottery is a key feature of the Neolithic period (c. 10,000 BCE). It marks a fundamental shift towards more sedentary lifestyles, as pottery is heavy and fragile, making it unsuitable for nomadic groups.""",
        "material": """The base material is clay. Potters often add a tempering agent (or 'grog') to the clay, such as sand, crushed shell, or even crushed old pottery, to reduce shrinkage and prevent the pot from cracking during the high heat of firing.""",
        "significance": """Pottery is an archaeologist's best friend. Styles of pottery change relatively quickly over time, making ceramic fragments (sherds) a primary tool for dating archaeological sites (a method called seriation). The shape of a pot reveals its function. Chemical residue analysis can reveal what people were eating and drinking.""",
        "cultural_context": """Every culture has its distinctive pottery traditions, from the cord-marked Jōmon pottery of Japan to the narrative scenes on Greek black-figure and red-figure vases. Major technological leaps, like the invention of the potter's wheel and high-temperature kilns, are markers of increasing social complexity.""",
        "technological_markers": """Early pottery was hand-built using techniques like pinching, coiling (building the walls with long ropes of clay), or slab-building. The invention of the potter's wheel revolutionized production. Surface treatments included burnishing (polishing), applying a clay slip (a liquid clay coating), or decorating with paint before firing in a kiln or a simple pit fire."""
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
        "site": "Keezhadi / Keeladi ",
        "distance": "Approx. 95 km from Rajapalayam",
        "significance": "A major Sangam-era (c. 6th century BCE to 1st century CE) urban settlement on the banks of the Vaigai river. The excavations have pushed back the known history of urbanism in Tamil Nadu by several centuries.",
        "key_artifacts": "Tamil-Brahmi inscribed pottery, terracotta figurines, glass beads, shell bangles, brick structures, and evidence of a sophisticated water management system. It showcases a highly literate and advanced society.",
        "link": "https://en.wikipedia.org/wiki/Keeladi_excavation_site"
    },
    {
        "site": "Adichanallur ",
        "distance": "Approx. 120 km from Rajapalayam",
        "significance": "An extensive Iron Age (c. 900 BCE - 200 BCE) urn-burial site. It's one of the most important archaeological sites in Southern India, providing crucial insights into ancient Tamil burial customs and metallurgy.",
        "key_artifacts": "Innumerable pottery urns containing human skeletons, bronze and iron objects (daggers, swords), gold diadems, and pottery with early Tamil-Brahmi script.",
        "link": "https://en.wikipedia.org/wiki/Adichanallur"
    },
    {
        "site": "Sittanavasal Cave ",
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