# app.py (Flask backend)
import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import io
import base64

# For a real implementation, you would import your actual trained model here
# from your_model_module import load_model, predict

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Mock model class (replace with your actual model)
class ArchaeologicalModel:
    def __init__(self):
        # In a real implementation, you would load your trained model here
        self.labels = ["huntingtool", "Kendi", "Thakli", "shell bangle", "pearl jewellery", 
                       "alloy", "Blackstone", "vatta_sillu", "pottery"]
        
    def predict(self, image):
        # This is a mock prediction - replace with your actual model inference code
        # For demonstration, we'll return random probabilities
        np.random.seed(hash(image.tobytes()) % 10000)  # Seed based on image content for consistency
        probabilities = np.random.dirichlet(np.ones(len(self.labels)), size=1)[0]
        
        # Get top prediction
        max_idx = np.argmax(probabilities)
        predicted_label = self.labels[max_idx]
        confidence = probabilities[max_idx]
        
        # Create detailed response
        details = self.get_object_details(predicted_label)
        
        return {
            "prediction": predicted_label,
            "confidence": float(confidence),
            "probabilities": {label: float(prob) for label, prob in zip(self.labels, probabilities)},
            "details": details
        }
    
    def get_object_details(self, label):
        # --- EXTENDED DETAILS SECTION ---
        details_map = {
            "huntingtool": {
                "description": "Tools crafted by early humans for hunting, butchering, and processing animals. This category includes a wide range of implements such as stone spearheads, arrowheads, hand axes, and scrapers.",
                "era": "Paleolithic to the Iron Age. The design and material changed significantly over time, reflecting technological advancements.",
                "material": "Commonly made from durable materials like chert, flint, obsidian, and quartzite. Later examples include bone, antler, and eventually bronze or iron.",
                "significance": "These tools are crucial for understanding the subsistence strategies, cognitive abilities, and technological skills of prehistoric societies. They provide direct evidence of human interaction with the environment."
            },
            "Kendi": {
                "description": "A unique spouted vessel used for drinking or pouring liquids, characterized by its round body, neck, and a mammiform spout without a handle. It is a distinctive artifact of Southeast Asian ceramic traditions.",
                "era": "Prominently from the 9th to the 19th centuries, with forms evolving across different dynasties and kingdoms.",
                "material": "Typically earthenware or stoneware, often glazed. Some high-status examples were made from precious metals like bronze or silver.",
                "significance": "Kendis were important in daily life and ceremonial rituals. Their distribution across Asia provides evidence of extensive maritime trade networks, particularly for ceramics."
            },
            "Thakli": {
                "description": "A traditional spindle used in India for hand-spinning fibers like cotton and wool into thread. It consists of a weighted whorl attached to a shaft.",
                "era": "Ancient to modern times. Its form has remained relatively consistent for centuries.",
                "material": "The whorl is often made of stone, clay, or bone, while the shaft is typically wood or metal.",
                "significance": "The presence of Thakli whorls at an archaeological site is a strong indicator of textile production, a vital economic activity in ancient cultures."
            },
            "shell bangle": {
                "description": "Ornaments worn on the wrist, crafted from marine or freshwater shells. They were often made from a single, continuous cross-section of a large shell.",
                "era": "Widespread from the Neolithic period through the Iron Age and into historical periods. Particularly common in Harappan and Gangetic Valley cultures.",
                "material": "Most commonly made from the conch shell (Turbinella pyrum). The species of shell can indicate long-distance trade with coastal regions.",
                "significance": "Shell bangles were not just ornaments but also important cultural markers, indicating social status, marital status, and ritual roles. They are evidence of sophisticated craftsmanship and trade."
            },
            "pearl jewellery": {
                "description": "Personal adornments such as necklaces, earrings, and pendants incorporating pearls. These were luxury items, often combined with other precious materials.",
                "era": "Ancient Roman, Indian, and Persian empires through to the medieval period. Pearls have been prized as gems for millennia.",
                "material": "Natural pearls harvested from oysters, often drilled and strung with gold, silver, or other beads.",
                "significance": "Represents wealth, high social status, and extensive trade networks. The discovery of pearl jewelry points to connections with marine environments where pearl-bearing mollusks were found."
            },
            "alloy": {
                "description": "An object made from a mixture of metals, created to enhance properties like strength, hardness, or color. Bronze (copper and tin) and brass (copper and zinc) are common archaeological alloys.",
                "era": "The Bronze Age (c. 3300 BCE) onwards. The development of alloys marks a pivotal moment in human technological history.",
                "material": "Bronze, brass, electrum (gold and silver), and various other combinations depending on the culture and available resources.",
                "significance": "The ability to create alloys demonstrates advanced metallurgical knowledge. Alloy artifacts, such as tools, weapons, and statues, are hallmarks of complex societies."
            },
            "Blackstone": {
                "description": "Artifacts carved from dark, fine-grained rock like basalt, schist, or steatite. This includes sculptures of deities, architectural elements, and ceremonial tools.",
                "era": "Common in various periods, particularly noted in the sculptures of the Pala and Sena dynasties of Eastern India.",
                "material": "Basalt, schist, or other dense, dark stones that allow for fine carving and a polished finish.",
                "significance": "Often used for creating durable and detailed religious icons and inscriptions. The geological source of the stone can help trace ancient trade and quarrying activities."
            },
            "vatta_sillu": {
                "description": "A type of circular grinding stone, often with a flat or slightly concave surface, used in conjunction with a smaller rolling stone (a muller) for processing food and other materials.",
                "era": "Common in domestic contexts from the Neolithic period through historical times in South Asia.",
                "material": "Hard, coarse-grained stone like granite or sandstone that provides an effective abrasive surface.",
                "significance": "A fundamental tool for food preparation, indicating a reliance on processed grains, spices, or medicinal herbs. It is a key indicator of sedentary, agricultural lifestyles."
            },
            "pottery": {
                "description": "Ceramic ware made from fired clay. This is one of the most common types of artifacts found, encompassing everything from simple storage jars and cooking pots to elaborately decorated ceremonial vessels.",
                "era": "From the Neolithic period (c. 10,000 BCE) onwards. It is a defining characteristic of this period.",
                "material": "Fired clay, which may be mixed with tempering agents like sand, shell, or crushed rock to prevent cracking.",
                "significance": "Pottery is invaluable for archaeologists. Its style, shape, and decoration are primary tools for dating sites and identifying different cultural groups. Chemical analysis can even reveal what the pots were used to store."
            }
        }
        
        return details_map.get(label, {
            "description": "No information available",
            "era": "Unknown",
            "material": "Unknown",
            "significance": "Unknown"
        })

# Initialize model
model = ArchaeologicalModel()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files and 'image_data' not in request.form:
            return jsonify({'error': 'No image provided'}), 400
        
        if 'image' in request.files:
            # Handle file upload
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            
            # Save the file temporarily
            filename = str(uuid.uuid4()) + '.jpg'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the image
            image = Image.open(filepath).convert('RGB')
            
        else:
            # Handle base64 image data (from camera)
            image_data = request.form['image_data']
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            image_data = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Make prediction
        result = model.predict(image)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        predictions = data.get('predictions', [])
        
        # Generate a simple report
        report = {
            "total_classifications": len(predictions),
            "objects_identified": {},
            "summary": f"Archaeological Classification Report - {len(predictions)} items analyzed"
        }
        
        for pred in predictions:
            obj_type = pred.get('prediction', 'Unknown')
            if obj_type in report['objects_identified']:
                report['objects_identified'][obj_type] += 1
            else:
                report['objects_identified'][obj_type] = 1
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
