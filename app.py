import os
import io
import time
import math # <-- IMPORTED FOR HAVERSINE CALCULATION
import torch
import torch.nn as nn
import numpy as np
from PIL import Image, UnidentifiedImageError
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from torchvision import models, transforms
from flask import Flask, request, jsonify, render_template
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
import base64

# ------------------------------
# Flask Setup
# ------------------------------
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25MB

# ------------------------------
# Haversine Distance Function
# ------------------------------
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points
    on the earth (specified in decimal degrees) in kilometers.
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371 # Radius of earth in kilometers.
    return c * r

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
    "description": """This category encompasses the entire technological evolution of tools designed for the pursuit, capture, and processing of game, from the most rudimentary sharp flakes to highly specialized projectile systems. The foundational technology began with the Oldowan industry, featuring simple choppers and sharp flakes that could cut through hide and slice meat from bone. This was superseded by the iconic, symmetrical Acheulean hand-axe, a multi-purpose tool for butchering, digging, and smashing bone marrow. The Middle Paleolithic witnessed a shift towards prepared-core techniques, producing specialized points, scrapers, and knives. The Upper Paleolithic revolution introduced composite technology, where microliths were inset into wooden or bone handles to create efficient barbed spears and harpoons, culminating in the invention of the atlatl and bow, which fundamentally changed the dynamics of hunting by increasing range, force, and safety.""",
    "era": """The chronology of hunting technology is a direct narrative of human cognitive and cultural development. The Lower Paleolithic, spanning from approximately 2.6 million years ago to 300,000 years ago, is dominated by the Oldowan and Acheulean traditions, primarily associated with Homo habilis and Homo erectus. The Middle Paleolithic (c. 300,000–40,000 years ago) is defined by the Levallois prepared-core technique and the Mousterian tool complex, strongly linked to both Neanderthals and early Homo sapiens. The Upper Paleolithic (c. 50,000–12,000 years ago) marks an explosion of innovation, with the emergence of blade-based technology, pressure flaking, and the first mechanical weapon systems like the spear-thrower. The Mesolithic period saw the refinement of the bow and arrow and an increased use of microliths, adaptations to a changing post-glacial environment and new prey species.""",
    "material": """Material selection was a critical decision, dictated by availability, workability, and functional requirement. The premier materials for cutting edges were cryptocrystalline stones like flint, chert, and obsidian, which fracture in a predictable conchoidal pattern to produce edges sharper than surgical steel. Softer stones like sandstone and limestone were used as hammerstones and grinding platforms. With the Upper Paleolithic, organic materials became equally important; antler was used for soft hammers in knapping and for points, bone was carved into awls, needles, and spearheads, and wood was essential for shafts, handles, and bows. The development of adhesives, such as birch bark tar, was crucial for hafting stone points to their wooden handles, creating a stronger, more lethal composite tool.""",
    "significance": """Hunting tools are a primary proxy for understanding hominin cognition, subsistence strategies, and social organization. The standardization of tool forms over vast geographical and temporal scales implies advanced cognitive capacities, including mental template planning, complex language for teaching, and cultural transmission. Butchery marks on fossil bones allow archaeologists to distinguish between hunting and scavenging behaviors and to reconstruct Pleistocene food webs. The technological leap to projectile weapons likely influenced social structure, enabling more cooperative hunting strategies and the division of labor. Furthermore, the spread of specific point styles, like the Solutrean points in Europe or the Clovis points in the Americas, provides critical evidence for tracing human migration routes and cultural interaction.""",
    "cultural_context": """Specific toolkits are the cultural fingerprints of different hominin species and populations. The crude Oldowan tools are the signature of Homo habilis, the first major toolmakers. The pervasive Acheulean hand-axe is synonymous with the global migrations of Homo erectus. The sophisticated Mousterian industry, with its Levallois technique, is a hallmark of Neanderthal adaptability and intelligence. The dramatic technological and artistic explosion of the Upper Paleolithic, characterized by blade technology, boneworking, and art, is inextricably linked to Homo sapiens. These tools are not just implements for survival but are embedded in the cultural identity and technological prowess of the groups that made and used them.""",
    "technological_markers": """The manufacturing process, known as knapping or lithic reduction, involves a series of sophisticated techniques. Percussion flaking uses a hammerstone (hard hammer) or a billet of wood or antler (soft hammer) to strike flakes from a core. Pressure flaking, a more advanced and controlled method, uses a pointed tool of bone or antler to press small, precise flakes off a pre-formed edge, allowing for final shaping and sharpening. The Levallois technique represents a cognitive leap, where the core is meticulously prepared so that a single, predeterminated flake of a specific shape can be struck off. Heat treatment of stone to improve its flaking quality is another advanced technological marker. Finally, hafting—the combination of stone, wood, bone, and adhesive—represents the pinnacle of Paleolithic engineering, creating tools far more effective than the sum of their parts."""
},

"Kendi": {
    "description": """A Kendi is a highly distinctive vessel form native to Southeast Asia, characterized by its lack of a handle and its unique two-orifice design: a central neck or opening for filling, and a separate, often mammiform (breast-shaped), spout for pouring. This ingenious design allows liquid to be consumed by pouring it directly into the mouth without the lips touching the vessel itself, promoting hygiene and making it ideal for communal drinking and ceremonial use. The body is typically globular or bulbous, providing a stable base and a large internal volume. The spout is its defining feature, ranging from a simple tapered tube to an elaborately modeled breast form, often symbolizing fertility and abundance. This form is so culturally specific that it serves as an unmistakable indicator of Southeast Asian influence and trade across the ancient world.""",
    "era": """The Kendi's development and proliferation are deeply tied to the rise of maritime trading empires in Southeast Asia. Its precursors appear as early as the first millennium CE, but it became a widespread and highly traded item during the era of the Srivijayan Empire (7th to 13th centuries), which controlled the strategic Straits of Malacca. Its production and artistic refinement peaked during the zenith of the Majapahit Empire in Java (13th to 16th centuries), where it became a common grave good and ritual object. Concurrently, major ceramic centers in Sukhothai and Sawankhalok (Thailand) and in Vietnam began mass-producing Kendis for both domestic use and export. The form remained popular into the early modern period, with Chinese kilns at Jingdezhen producing exquisite blue-and-white porcelain versions specifically for the Southeast Asian market.""",
    "material": """Kendis were produced in a vast range of materials, reflecting their use across all levels of society. For everyday domestic use, they were fashioned from earthenware or local stoneware. The most archaeologically significant are the high-fired stoneware Kendis from Thai and Vietnamese kilns, often coated in beautiful celadon glazes ranging from olive-green to sea-green. Chinese export porcelain Kendis represent the height of luxury, featuring underglaze blue paintings of floral and geometric motifs. For the elite and for temple use, Kendis were crafted from precious metals like silver and gold, or from bronze, demonstrating their high status. The choice of material directly correlates to the wealth of the owner and the ritual importance of the vessel's function.""",
    "significance": """The Kendi is far more than a simple water vessel; it is a key artifact for understanding pre-modern trade and cultural exchange. Its distribution maps the extent of the Maritime Silk Road, with finds from shipwrecks and archaeological sites stretching from Japan and the Philippines to Egypt and Turkey. As a ritual object, it held profound importance in Hindu-Buddhist ceremonies across Southeast Asia, used for storing and pouring holy water (tirta) during purification rites, consecrations, and other religious observances. Its presence in a burial context signifies beliefs in the afterlife, where the deceased would need vessels for ritual purification. The Kendi is thus a symbol of both earthly trade and spiritual devotion.""",
    "cultural_context": """The Kendi is deeply embedded in the cultural and religious fabric of Southeast Asia. It is frequently depicted in the bas-reliefs of ancient temples, such as the famous Borobudur in Java, illustrating its use in daily life and courtly ceremony. In traditional Indonesian and Malay culture, the Kendi was a common feature in households and was used in various life-cycle rituals. Its hygienic principle aligns with cultural practices emphasizing purity. The mammiform spout carries strong associations with fertility and the divine feminine, linking the vessel to ancient animist beliefs that were syncretized with later Hindu-Buddhist traditions. It stands as a powerful cultural icon of the region's innovative artistry and its complex spiritual history.""",
    "technological_markers": """The production of ceramic Kendis required a high degree of technological expertise. Wheel-throwing was the primary forming method, demanding great skill to create the symmetrical body and seamlessly attach the spout and neck. The application of vitreous glazes, particularly the coveted celadon, required precise control of the kiln atmosphere (reduction firing) to achieve the desired color and finish. Firing to stoneware temperatures (often exceeding 1200°C) necessitated the construction of sophisticated updraft or cross-draft kilns, like the massive dragon kilns of Vietnam and China. The production of metal Kendis involved advanced metallurgy, including lost-wax casting for bronze and intricate repoussé and chasing work for silver and gold examples, showcasing the mastery of multiple material technologies."""
},

"Thakli": {
    "description": """A Thakli, more universally known as a drop spindle, is a deceptively simple tool used for the ancient craft of spinning fibers into yarn or thread. It consists of two basic components: a shaft (spindle stick) and a whorl, a weight attached to the shaft that acts as a flywheel to maintain momentum. The spinner sets the spindle in motion by twisting the shaft and then lets it hang suspended, drafting out fibers with their hands while the rotating spindle imparts the twist, transforming loose fiber into a continuous, strong thread. The finished thread is then wound around the shaft itself for storage. This tool represents one of the most fundamental and transformative inventions in human history, enabling the creation of textile fabrics.""",
    "era": """The spindle whorl is a ubiquitous find in archaeological sites across the globe from the Neolithic period onward, marking the adoption of fiber technology and settled life. In the Indian subcontinent, evidence for spinning is ancient and robust; terracotta spindle whorls have been excavated from major sites of the Indus Valley Civilization, such as Harappa and Mohenjo-daro, dating back to 2500 BCE, indicating a highly developed cotton textile industry. The design of the drop spindle has seen remarkably little change over millennia, a testament to its perfect efficiency. Its use persisted as the primary spinning tool until it was gradually supplemented, though never fully replaced, by the spinning wheel (Charkha) in the medieval period, which increased production speed but required a seated, stationary operator.""",
    "material": """The archaeological record is biased towards durable materials, so while the wooden or bamboo spindle shaft almost never survives, the whorl is commonly found. Whorls were made from a wide variety of materials depending on availability and status. The most common were inexpensive, locally sourced materials like fired clay (terracotta), stone, or bone. These could be easily shaped and were often decorated with incised patterns. More valuable whorls, indicating wealth or special significance, were made from exotic materials, precious metals, or intricately carved ivory. The choice of material for the whorl affected its weight and moment of inertia, which in turn influenced the thickness and twist of the yarn being spun.""",
    "significance": """The discovery of a spindle whorl at an archaeological site is a direct indicator of a complex chain of technological and economic activities. It implies the prior steps of fiber production: either the cultivation of plants like cotton, flax, or hemp, or the domestication and shearing of animals like sheep or goats for their wool. It points forward to the subsequent technology of weaving on looms to produce cloth. Textiles were one of the most important commodities in ancient economies, used for clothing, sailcloth, sacks, and trade. Therefore, the humble Thakli is a key piece of evidence for understanding a society's level of agricultural development, craft specialization, and participation in local and long-distance trade networks.""",
    "cultural_context": """In India, the spindle is deeply intertwined with both ancient economic history and modern political symbolism. The Indus Valley Civilization's prowess in cotton spinning and weaving was legendary and formed a basis for its trade with Mesopotamia. Centuries later, during the Indian independence movement, Mahatma Gandhi revitalized the spinning wheel (Charkha) as a powerful symbol of economic self-sufficiency (Swadeshi) and peaceful resistance to British colonial rule that had crippled India's native textile industries. The act of spinning became a daily ritual for millions, making the tool an icon of national pride and self-reliance. The Thakli thus connects the artisans of the ancient world to the freedom fighters of the modern era.""",
    "technological_markers": """The technology of the drop spindle is a masterclass in applied physics. The whorl must be centrally perforated and perfectly balanced to spin smoothly without wobbling, which would break the thread. The weight and diameter of the whorl are carefully matched to the type of fiber being spun: a heavier whorl provides more inertia for spinning thick, coarse yarns, while a lighter whorl is used for delicate, fine threads like silk. The shaft must be straight, smooth, and tapered to facilitate the winding of the finished yarn. The spinner's skill lies in coordinating the drafting of the fibers with the falling motion and rotation of the spindle, a knowledge passed down through generations."""
},

"shell bangle": {
    "description": """Shell bangles are rigid, ring-shaped bracelets meticulously crafted from the thick, robust whorls of large marine gastropods, primarily the sacred conch shell (Turbinella pyrum). Unlike bracelets made from multiple beads strung together, these are single, continuous circles of shell, requiring immense skill to produce from a brittle material without fracture. The manufacturing process involved cutting a rough ring from the body whorl of the shell and then grinding and polishing it into its final smooth, circular form. These were not mere ornaments but potent symbols of identity, wealth, and ritual status, worn in multiples on the wrist. Their presence far inland is a definitive marker of long-distance trade and cultural value.""",
    "era": """The production of shell bangles on an industrial scale is a defining characteristic of the Indus Valley Civilization (Harappan Culture), which flourished from approximately 2600 to 1900 BCE. While shell ornaments date back to the Paleolithic, the Harappans systematized their production into a specialized, large-scale craft industry. This tradition did not disappear with the decline of the Indus cities; it persisted into later historical periods across the Indian subcontinent. The cultural practice of wearing conch shell bangles, particularly by married women in regions like Bengal and Odisha, continues to this day, representing an unbroken tradition stretching back over 4,000 years, making it one of the world's longest-lasting cultural artifacts.""",
    "material": """The material of choice was almost exclusively the sacred chank or conch shell, Turbinella pyrum, prized for its thick, sturdy walls, pure white color, and deep religious significance. These shells were sourced from the sea, specifically the coasts of modern-day Gujarat, Pakistan, and Sri Lanka. The procurement of the raw material was itself a specialized activity, involving maritime communities. The finished product—the white bangle—was often paired with bangles made from other materials, most notably red-red terracotta, lac, or coral, creating a symbolic contrast of white and red that held profound meaning related to life, marriage, and fertility. The shell's origin from the ocean also connected it to concepts of purity and the source of life.""",
    "significance": """Shell bangles are critical artifacts for understanding Harappan economics, social structure, and trade. The existence of dedicated workshops at coastal sites like Nageshwar and Balakot, complete with unfinished blanks, manufacturing debris, and finished products, indicates craft specialization and organized production for distribution. The transport of these delicate, finished goods to major urban centers hundreds of kilometers inland, such as Mohenjo-daro and Harappa, provides clear evidence of a sophisticated internal trade network. Furthermore, they were clear markers of social status; the quantity and quality of bangles a person wore likely indicated their wealth, ethnicity, or marital status. They are a key diagnostic artifact for identifying the extent of Indus influence and trade.""",
    "cultural_context": """The conch shell (Shankha) holds an exalted position in Hindu mythology and ritual, being one of the primary attributes of the god Vishnu. Its sound is believed to purify the environment and vanquish evil. In this context, bangles made from the shell are imbued with protective and purifying properties. In modern Hindu practice, particularly in eastern India, a married woman's wearing of white conch shell bangles (Shankha) paired with red lac bangles (Pala) is an essential symbol of her suhag (marital bliss) and the long life of her husband. This modern ritual is a direct cultural descendant of the Harappan tradition, seamlessly linking the archaeology of the Indus Valley to the lived practices of contemporary South Asia.""",
    "technological_markers": """The manufacturing process was a complex, multi-stage operation requiring expert knowledge. It began with cutting the apex of the shell to create a flat working surface. Then, using a bronze saw with a likely abrasive slurry (sand and water), craftspeople would carefully cut concentric circles out of the shell's body whorl to create rough, tubular blanks. These rough rings were then ground into a smooth, round shape using stone abraders. The final stage involved polishing the bangle to a high, lustrous shine, probably using a fine abrasive paste or cloth. This process, from a whole shell to a perfect ring, demonstrates a sophisticated understanding of material properties and advanced lapidary skills."""
},

"Bead Jewellery": {
    "description": """Bead jewellery encompasses all adornments created by stringing together small, perforated objects, forming necklaces, bracelets, anklets, girdles, and elaborate collars. As one of the oldest forms of human expression, beads served functions far beyond decoration, acting as markers of identity, status, wealth, and belief. The technology to create beads evolved from simple stringing of natural objects like shells and seeds to the highly sophisticated working of the hardest stones and the invention of synthetic materials like faience and glass. The variety of forms is immense, including simple spherical beads, long barrels, bicones, discs, and fantastically shaped etched beads. The study of beads provides a microscopic view into trade, technology, and aesthetic values of ancient societies.""",
    "era": """The history of beads is as long as the history of modern humans. The earliest known beads, made from Nassarius snail shells with deliberate perforations, date back over 100,000 years to the Middle Stone Age, associated with early Homo sapiens in Africa and the Near East. The Neolithic period saw an expansion in materials and styles alongside sedentism. The Bronze Age (3rd millennium BCE) represents a golden age of bead making, with the Indus Valley Civilization producing long, barrel-shaped carnelian beads and Egypt crafting intricate faience broadcollars. The Iron Age and Classical periods saw the perfection of glass bead making, particularly by the Romans and later by Venetian artisans, a tradition that continues to the present day.""",
    "material": """The materials used for beads form a hierarchy of value and technological complexity. Common materials included baked clay (terracotta), bone, ivory, and shell. Hardstones were highly valued for their color and durability; these included deep red carnelian, banded agate, green feldspar, brilliant blue lapis lazuli, and deep green turquoise. The most precious materials were metals, particularly gold and silver. Perhaps the most significant technological innovations were the development of synthetic materials: Egyptian faience (a quartz-based glazed ceramic) and glass. Both involved pyrotechnology and chemical knowledge to create vibrant, man-made colors that imitated precious stones.""",
    "significance": """Beads are unparalleled indicators of long-distance trade and cultural interaction. Because raw materials like lapis lazuli (only from Afghanistan), turquoise (from the Sinai Peninsula), and amber (from the Baltic) have highly specific geological sources, their presence in archaeological sites far from their origin provides irrefutable evidence of vast trade networks. The "Treasures of the Queen" in the Royal Cemetery of Ur contained beads from the Indus Valley, demonstrating trade between Mesopotamia and the Indus civilization around 2500 BCE. Residue analysis on beads can reveal the types of stringing materials used (sinew, flax, cotton) and even the presence of perfumes or oils. They are tiny time capsules of economic and social information.""",
    "cultural_context": """Beads are a universal language of adornment, but each culture developed distinct styles. The Harappans were renowned for their exceptionally long carnelian beads, achieved through a complex etching and heat treatment process. The famous 'Dancing Girl' statue from Mohenjo-daro wears a stack of bangles on one arm, showcasing the importance of personal adornment. In ancient Egypt, beaded broadcollars were essential items of funerary equipment, believed to protect the deceased, with Tutankhamun's tomb containing multiple magnificent examples. In many African and Native American cultures, beadwork patterns are a form of communication, denoting tribal affiliation, social status, and personal history. Beads are deeply woven into the social and spiritual fabric of humanity.""",
    "technological_markers": """The production of beads required a suite of advanced technologies. For hardstone beads, the primary technology was drilling. Craftsmen used bow-driven drills tipped with hardened stone (like emery) or copper points, often with an abrasive sand slurry, to perforate incredibly hard materials. Shaping was done by grinding against stone abraders. The etching of white patterns on carnelian beads involved painting a alkali solution onto the stone and then heat-treating it. Faience production involved crushing quartz, molding it, and then firing it with a glaze that would vitrify on the surface. Glassmaking required furnaces capable of reaching very high temperatures to melt silica sand and flux, and the knowledge to add mineral-based colorants. Each material demanded a unique and sophisticated technological knowledge."""
},

"alloy": {
    "description": """An alloy is a material composed of two or more metallic elements, intentionally combined to create a new substance with properties superior to those of its individual components. The most historically significant alloys are bronze (copper and tin) and brass (copper and zinc), whose development revolutionized toolmaking, warfare, and art. The creation of an alloy is a deliberate act of applied chemistry, requiring knowledge of ores, smelting, and the effects of mixing metals. Alloys can be engineered for specific traits: bronze is harder and casts better than pure copper, while brass is more malleable and has a gold-like appearance. The shift from stone to metal alloys marks one of the most significant technological transitions in human history, giving its name to the Bronze Age.""",
    "era": """The development of alloy technology was a pivotal moment in human history. The first steps involved the use of native copper and the simple smelting of copper ores, a process known in the Neolithic period. The true Bronze Age began around 3300 BCE in the Near East (Mesopotamia and Anatolia) when tin was systematically added to copper to create true bronze. This technological revolution spread to the Aegean (by 3000 BCE), the Indus Valley (by 2500 BCE), and China (by 2000 BCE), occurring independently in the Andes. The Iron Age gradually superseded the Bronze Age from around 1200 BCE, not because iron was superior to bronze (initially, it was not), but because iron ore was far more common and widespread than the rare tin required for bronze.""",
    "material": """The primary alloy of antiquity was bronze, typically composed of 90% copper and 10% tin. However, the scarcity of tin led to the use of arsenic to create an earlier, more toxic form known as arsenical bronze. Brass, an alloy of copper and zinc, became more common during the Roman Empire. Other important alloys include pewter (tin and lead), used for tableware, and electrum, a naturally occurring alloy of gold and silver that was used for the first coins in Lydia (modern Turkey). The specific composition of an alloy can be determined through techniques like X-ray fluorescence (XRF) analysis, which can trace the source of the metals and reveal trade connections.""",
    "significance": """The invention of bronze had a transformative impact on society. It enabled the creation of tools that were vastly superior to stone: harder, more durable, and capable of being resharpened and recycled. Bronze weapons—swords, spearheads, and armor—provided military advantages that contributed to the rise of powerful, warrior-led states and empires. The value of bronze and the specialized knowledge required to produce it led to the emergence of a class of full-time metal smiths. Furthermore, because copper and tin sources are geographically limited and rarely found together, the Bronze Age economy was inherently international, fueling complex and extensive trade networks across Europe and Asia that were vulnerable to disruption.""",
    "cultural_context": """The Bronze Age was the first truly globalized era, connecting disparate cultures through the demand for metal. The quest for tin and copper created interdependencies between regions like Mesopotamia, Anatolia, the Aegean, and even distant Britain (a source of tin). This is reflected in the archaeological record through the spread of not only metal objects but also associated technologies, artistic styles, and ideas. The possession of bronze objects became a key signifier of elite status and power. The mythological significance of metalworking is evident in many cultures, where smiths were often accorded a semi-magical status, as seen in the figure of Hephaestus in Greek mythology or Vishwakarma in Hinduism.""",
    "technological_markers": """Alloy production involved a complex chain of sophisticated technologies. It began with mining, often in deep shafts, to extract copper and tin ores. Smelting used furnaces capable of reaching temperatures over 1000°C to reduce the metal from its ore. The purified metals were then melted together in crucibles in precise ratios to create the alloy. The primary method for shaping objects was casting, using single-piece stone molds for simple objects or the highly advanced lost-wax (cire perdue) method for complex, sculptural pieces like the famous "Dancing Girl" from Mohenjo-daro. Subsequent cold-working and annealing (heating and hammering) were used to harden and strengthen the finished object."""
},

"Blackstone": {
    "description": """This category refers to artifacts masterfully carved from dense, fine-grained, dark-colored stones such as basalt, dolerite, schist, and steatite (soapstone). These materials are prized for their ability to hold intricate detail and achieve a deep, lustrous polish that conveys permanence and grandeur. Artifacts range from monumental sculpture and imposing architectural elements to inscribed steles bearing laws and decrees. The choice of a dark, often black, stone was frequently symbolic, associated with eternity, the underworld, or fertile earth. Working these hard stones required exceptional skill, patience, and specialized tools, making such objects statements of power and devotion.""",
    "era": """The use of blackstone for significant artifacts spans millennia and continents. It was employed in Ancient Egypt for statues of pharaohs and gods, such as the famous diorite statue of Khafre. In Mesopotamia, it was the material of choice for recording laws for posterity, exemplified by the Code of Hammurabi (c. 1750 BCE), carved on a tall basalt stele. In the Indian subcontinent, the tradition reached an aesthetic zenith during the Pala and Sena dynasties (c. 8th-12th centuries CE) in the eastern regions of Bengal and Bihar, where black schist and basalt were used to create some of the most refined and exquisite sculptures in Buddhist and Hindu art. The tradition continues in modern times for temple icons and decorative items.""",
    "material": """The specific choice of stone depended on the desired effect and available resources. Basalt and dolerite are extremely hard, igneous rocks that are difficult to work but yield a superb, durable polish, ideal for outdoor monuments. Schist is a metamorphic rock that is softer and more fissile, allowing sculptors to carve incredibly fine details, delicate jewelry, and flowing drapery, but it is less durable outdoors. Steatite, or soapstone, is the softest of these materials, easily carved with even simple tools and often used for smaller objects, seals, and preliminary models for larger works. The color palette ranges from deep black and grey to greenish-black and dark blue, all conveying a sense of solemnity and weight.""",
    "significance": """Blackstone artifacts were intended to last for eternity, serving as permanent records of divine power, royal authority, and legal order. The durability of the material made it ideal for inscribed law codes, like Hammurabi's, which were meant to be immutable and publicly displayed. In a religious context, a polished black stone statue of a deity was believed to be a permanent vessel for the divine presence, aniconic and eternal. For archaeologists and art historians, the geological sourcing of the stone through petrographic analysis can reveal ancient quarrying sites and trade routes. The style and iconography of the carving provide a chronology for artistic development and cultural influence.""",
    "cultural_context": """The cultural meaning of blackstone varied by region but was consistently associated with power and the sacred. In Egypt, the black color was linked to the fertile black silt of the Nile (Kemet, "the black land") and to Osiris, god of the afterlife and resurrection, making it an appropriate material for funerary and divine statues. In Mesopotamia, its use for law steles conveyed the timeless and unwavering nature of the king's justice. In the Pala Empire, a major center of Mahayana Buddhism, the use of black schist for sculptures of compassionate Bodhisattvas like Avalokiteshvara and Tara created a striking visual contrast between the dark stone and the serene, gentle expressions of the deities, enhancing their spiritual impact. This cultural context elevates these objects from mere stone to embodiments of belief and power.""",
    "technological_markers": """Creating a finished blackstone sculpture was a labor-intensive process involving multiple stages and high levels of expertise. It began at the quarry, where large blocks were extracted using stone hammers, wood wedges, and water. The initial roughing out of the shape was done by skilled craftsmen using pointed and chisel-ended tools made of a metal harder than the stone (e.g., bronze or iron chisels for softer stones, hardened steel for basalt). The intricate detailing was achieved with finer tools and drills. The final and most time-consuming stage was polishing, achieved by rubbing the surface with progressively finer abrasives (e.g., sand, emery powder, leather) often with water, until the stone achieved a mirror-like, reflective gloss that brought out its color and depth."""
},

"vatta_sillu": {
    "description": """The Vatta Sillu, more commonly known as an Ammi Kallu or grinding stone, is a fundamental dual-piece tool central to traditional South Indian and Sri Lankan domestic life. It consists of a large, flat, rectangular or oval stone slab (the Ammi) which serves as the base, and a smaller, cylindrical stone roller (the Kuzhavi or Muller) used to crush, grind, and pulverize ingredients. Unlike a Western mortar and pestle which is used for pounding, the Ammi Kallu is designed for a back-and-forth grinding motion, which is essential for creating the smooth, wet pastes and batters that are the foundation of the region's cuisine. It is the undisputed heart of the traditional kitchen, a tool of daily ritual and immense practical importance.""",
    "era": """The basic technology of the grinding slab is Neolithic in origin, appearing with the advent of agriculture for processing grains. The saddle quern, a concave base stone with a rocking handstone, was a common prehistoric form. The specific flat-bed design of the South Indian Ammi Kallu represents a regional evolution of this ancient technology, perfected over centuries to suit the particular culinary needs of the region. Its use is documented over many centuries and it remains in use in countless households and traditional food preparation units today, representing a living archaeological tradition that connects the present directly to the ancient past.""",
    "material": """The tool is almost exclusively made from stone, chosen for its hardness and abrasive quality. The most common material is granite, due to its widespread availability, incredible durability, and coarse-grained texture which provides the necessary friction for efficient grinding. Sandstone is also used, particularly in regions where it is more readily available. The choice of stone is crucial; it must be hard enough to not wear away too quickly, but have a grain structure that acts as a natural abrasive. The stone is always left unglazed and untreated, as its rough, porous surface is essential to its function.""",
    "significance": """The Ammi Kallu is a key technological indicator of a specific culinary tradition based on freshly ground spices and fermented batters. Its presence signifies a cuisine that requires fine pastes for curries (e.g., wet masalas) and smooth, aerated batters for staples like dosa, idli, and adai. This is in contrast to cuisines that use dry spices or pounding techniques. Archaeologically, finding a stone with a worn, smooth surface from years of grinding provides direct evidence of food preparation activities at a site. It represents a technology that is entirely mechanical, requiring no power source other than human energy, and embodies a slow, rhythmic method of cooking that is deeply connected to cultural identity.""",
    "cultural_context": """In a South Indian context, particularly in Tamil Nadu, the Ammi Kallu is more than a tool; it is a cultural icon. The rhythmic sound of grinding is a classic and comforting sound of home and domestic life. Its importance is reflected in its role in rituals; it is sometimes personified and worshipped as a household deity. In Tamil Brahmin weddings, the groom is often shown the Ammi by the bride's family as a symbol of the grinding away of life's difficulties and the stability of the household. This deep cultural embedding makes it a powerful symbol of tradition, family, and the enduring nature of regional culinary practices in the face of modern appliances like electric grinders.""",
    "technological_markers": """The technology lies in the quarrying, shaping, and maintenance of the stone. The large slab was likely shaped by pecking—repeatedly striking it with a harder hammerstone to fracture and remove small pieces until a flat surface was achieved. The roller was shaped into a comfortable, ergonomic cylinder. The critical technological process is the preparation and maintenance of the grinding surface. Over time, the surface becomes smooth and less effective. To restore its abrasive quality, users periodically re-peck the surface of the Ammi with a pointed tool, creating a fresh, rough texture. This cycle of use, wear, and re-pecking is the fundamental technological marker of this tool's long lifecycle."""
},

"pottery": {
    "description": """Pottery refers to objects—primarily vessels—formed from clay and hardened by heat. It is one of the most common and informative classes of artifacts found by archaeologists. The category encompasses a vast range of items, from simple, undecorated cooking pots and bulky storage jars to finely made, elaborately painted tableware and ritual vessels. The invention of pottery represents a fundamental shift in human technology, enabling the efficient storage, cooking, and transport of food and liquids. Its fragility and weight make it strongly associated with sedentary, rather than nomadic, lifestyles. The study of pottery (ceramic analysis) is a cornerstone of archaeology.""",
    "era": """The development of pottery is a hallmark of the Neolithic period, beginning around 10,000 BCE in East Asia (Japan's Jomon culture) and later appearing independently in the Near East, Africa, and the Americas. The earliest forms were simple, hand-built vessels fired in open bonfires. The invention of the potter's wheel in Mesopotamia around 3500 BCE was a major revolution, enabling faster, more standardized production. The subsequent development of kilns capable of reaching higher and more controlled temperatures led to advanced ceramics like stoneware and, eventually, porcelain in China. Pottery styles change rapidly, making them the primary tool for archaeologists to date sites (seriation) and trace cultural interactions.""",
    "material": """The primary material is clay, a naturally occurring alumina-silicate that becomes plastic when wet and hard when fired. Potters rarely use pure clay; they add non-plastic materials called temper (or grit) to the clay body to prevent excessive shrinkage and cracking during drying and firing. Common tempering materials include sand, crushed shell, crushed rock, and even crushed pottery (grog). The choice of clay and temper is often locally specific. The surface could be left plain, smoothed (burnished), or covered with a slip (a fine clay suspension) for color and smoothness. Glazes, a glassy coating, were a later invention requiring knowledge of chemistry and high-temperature firing.""",
    "significance": """Pottery is invaluable to archaeologists. Its ubiquity and breakability mean it is found in enormous quantities. Because styles of decoration, form, and manufacture change frequently, pottery provides a sensitive relative chronology for dating archaeological layers (a method called seriation). The shape of a pot reveals its function (cooking, storage, serving). Chemical and residue analysis of pottery sherds can detect traces of ancient foods, drinks, and oils, providing direct evidence of diet and trade. The distribution of certain pottery types can map trade routes and cultural influence zones. It is, quite simply, the most important diagnostic tool for understanding past human behavior.""",
    "cultural_context": """Pottery is a universal technology, but every culture developed distinct styles that serve as ethnic markers. The cord-marked Jomon pots of Japan, the painted black-on-white ware of the Ancestral Puebloans, the narrative scenes on Greek vases, and the exquisite blue-and-white porcelain of China are all instantly recognizable cultural signatures. Pottery was deeply integrated into all aspects of life, from the most mundane cooking pot to the most elaborate funerary urn. It reflects aesthetic values, religious beliefs, and social customs. The level of pottery technology—from hand-building to wheel-throwing to glazing—is also a key indicator of a society's technological complexity and specialization of labor.""",
    "technological_markers": """The manufacturing process involves several key stages and techniques. Forming methods include hand-building: pinching, coiling (building pots from long ropes of clay), or slab construction. The potter's wheel allowed for faster, symmetrical throwing. Surface treatments include impressing (with cords or stamps), incising (cutting designs into the clay), painting (with iron-based or mineral pigments), and applying slips. The final and most crucial stage is firing. Early firing was done in simple open bonfires. The development of the kiln—an enclosed firing chamber—allowed for control of temperature (reaching over 1000°C), atmosphere (oxidizing for red clays, reducing for grey clays), and the production of advanced ceramics like stoneware and porcelain."""
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

# --- MODIFIED: Added coordinates to REGIONAL_FINDS and removed hardcoded distance ---
REGIONAL_FINDS = [
    {
        "site": "Keezhadi / Keeladi",
        "lat": 9.845, "lon": 78.221,
        "significance": "A major Sangam-era (c. 6th century BCE to 1st century CE) urban settlement on the banks of the Vaigai river. The excavations have pushed back the known history of urbanism in Tamil Nadu by several centuries.",
        "key_artifacts": "Tamil-Brahmi inscribed pottery, terracotta figurines, glass beads, shell bangles, brick structures, and evidence of a sophisticated water management system. It showcases a highly literate and advanced society.",
        "link": "https://en.wikipedia.org/wiki/Keeladi_excavation_site"
    },
    {
        "site": "Adichanallur",
        "lat": 8.618, "lon": 77.876,
        "significance": "An extensive Iron Age (c. 900 BCE - 200 BCE) urn-burial site. It's one of the most important archaeological sites in Southern India, providing crucial insights into ancient Tamil burial customs and metallurgy.",
        "key_artifacts": "Innumerable pottery urns containing human skeletons, bronze and iron objects (daggers, swords), gold diadems, and pottery with early Tamil-Brahmi script.",
        "link": "https://en.wikipedia.org/wiki/Adichanallur"
    },
    {
        "site": "Sittanavasal Cave",
        "lat": 10.463, "lon": 78.736,
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
    return render_template('index_new.html')

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

        print("Image successfully read")

        top_k = predict_topk(image_bytes, k=5)
        all_probs = predict_all_probs(image_bytes)

        

        chart_filename = f"confidence_chart_{int(time.time())}.png"
        create_confidence_chart(all_probs, chart_filename)

        top1 = top_k[0]
        details = DETAILS_MAP.get(top1["class"], {"description": "No details available"})

        

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
        print("Error during prediction:", str(e))
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

# --- MODIFIED: The /regional_finds route to handle location data ---
@app.route('/regional_finds', methods=['GET'])
def get_regional_finds():
    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)

    if user_lat and user_lon:
        sites_with_distance = []
        for site in REGIONAL_FINDS:
            distance = haversine(user_lat, user_lon, site['lat'], site['lon'])
            
            site_copy = site.copy()
            site_copy['distance'] = f"Approx. {round(distance)} km away"
            sites_with_distance.append(site_copy)
        
        sorted_sites = sorted(sites_with_distance, key=lambda item: round(haversine(user_lat, user_lon, item['lat'], item['lon'])))
        return jsonify(sorted_sites)
    else:
        default_sites = []
        for site in REGIONAL_FINDS:
            site_copy = site.copy()
            site_copy['distance'] = "Distance not calculated"
            default_sites.append(site_copy)
        return jsonify(default_sites)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

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

        story = []

        story.append(Paragraph("Archaeological Artifact Analysis Report", title_style))
        story.append(Spacer(1, 20))

        image_data = data.get('image_data')
        if image_data:
            try:
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                img_data = base64.b66decode(image_data)
                
                temp_img_path = os.path.join(app.static_folder, f"temp_artifact_{int(time.time())}.png")
                with open(temp_img_path, 'wb') as f:
                    f.write(img_data)
                
                story.append(Paragraph("Uploaded Artifact Image", heading_style))
                story.append(Spacer(1, 10))
                story.append(Image(temp_img_path, width=4*inch, height=3*inch))
                story.append(Spacer(1, 20))

                import atexit
                atexit.register(lambda: os.remove(temp_img_path) if os.path.exists(temp_img_path) else None)
                
            except Exception as e:
                print(f"Error processing image: {e}")

        top1 = data.get('top1', {})
        if top1:
            story.append(Paragraph(f"Primary Identification: <b>{top1.get('class', 'Unknown')}</b>", heading_style))
            story.append(Paragraph(f"Confidence: {top1.get('probability', 0)*100:.2f}%", normal_style))
            story.append(Spacer(1, 10))

        chart_url = data.get('chart_url', '')
        if chart_url:
            try:
                chart_path = os.path.join(app.static_folder, chart_url.split('/')[-1])
                if os.path.exists(chart_path):
                    img = Image(chart_path, width=6*inch, height=4*inch)
                    story.append(img)
                    story.append(Spacer(1, 15))
            except Exception as e:
                print(f"Error adding chart: {e}")

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

        top_k = data.get('top_k', [])
        if top_k:
            story.append(PageBreak())
            story.append(Paragraph("Complete Classification Results", heading_style))
            
            table_data = [['Rank', 'Artifact Type', 'Confidence']]
            for i, prediction in enumerate(top_k, 1):
                table_data.append([
                    str(i),
                    prediction.get('class', 'Unknown'),
                    f"{prediction.get('probability', 0)*100:.2f}%"
                ])
            
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

        story.append(Paragraph("Archaeological Sites Near Rajapalayam, Tamil Nadu", heading_style))
        story.append(Paragraph("Explore these significant archaeological sites in the region:", normal_style))
        story.append(Spacer(1, 10))

        for i, site in enumerate(REGIONAL_FINDS, 1):
            story.append(Paragraph(f"<b>{i}. {site['site']}</b>", normal_style))
            story.append(Paragraph(f"<i>Distance: {site.get('distance', 'N/A')}</i>", small_style))
            story.append(Paragraph(f"<b>Significance:</b> {site['significance']}", small_style))
            story.append(Paragraph(f"<b>Key Artifacts:</b> {site['key_artifacts']}", small_style))
            story.append(Spacer(1, 12))

        c14_data = data.get('c14_data')
        if c14_data:
            story.append(PageBreak())
            story.append(Paragraph("Carbon-14 Dating Analysis", heading_style))
            story.append(Paragraph(f"Original C14 Percentage: {c14_data.get('original_percentage', 'N/A')}%", normal_style))
            story.append(Paragraph(f"Calculated Age (BP): {c14_data.get('age_bp', 'N/A')} years", normal_style))
            story.append(Paragraph(f"Calendar Year: {c14_data.get('calendar_year', 'N/A')} CE/BCE", normal_style))
            story.append(Spacer(1, 10))

            story.append(Paragraph("Historical Context:", heading_style))
            story.append(Paragraph("This date places your artifact within the following historical periods:", normal_style))

        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Report generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}", small_style))
        story.append(Paragraph("Generated by Archaeological Artifact Identification System", small_style))
        
        doc.build(story)
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        response = app.response_class(
            response=pdf_content,
            status=200,
            mimetype='application/pdf'
        )
        response.headers['Content-Disposition'] = 'attachment; filename=artifact_report.pdf'
        return response
        
    except Exception as e:
        if 'temp_img_path' in locals() and os.path.exists(temp_img_path):
            os.remove(temp_img_path)
        
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

# ------------------------------
# Main Execution
# ------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

>>>>>>> 0bd2f86 (Initial commit for Flask artifact app)
