// modelService.ts
// Mock archaeological classification service

export interface ClassificationResult {
    prediction: string;
    confidence: number;
    probabilities: Record<string, number>;
    details: ObjectDetails;
  }
  
  export interface ObjectDetails {
    description: string;
    era: string;
    material: string;
    significance: string;
  }
  
  const ARCHAEOLOGY_LABELS = [
    "huntingtool", "Kendi", "Thakli", "shell bangle", "pearl jewellery", 
    "alloy", "Blackstone", "vatta_sillu", "pottery"
  ];
  
  const OBJECT_DETAILS: Record<string, ObjectDetails> = {
    "huntingtool": {
      "description": "Prehistoric tool used for hunting animals",
      "era": "Paleolithic to Neolithic periods",
      "material": "Stone, bone, or wood",
      "significance": "Shows early human technological advancement"
    },
    "Kendi": {
      "description": "Traditional Southeast Asian drinking vessel",
      "era": "Various periods, from ancient to colonial times",
      "material": "Ceramic or pottery",
      "significance": "Used in cultural rituals and daily life"
    },
    "Thakli": {
      "description": "Ancient weight measure or tool",
      "era": "Historical periods across Southeast Asia",
      "material": "Stone or metal",
      "significance": "Evidence of trade and measurement systems"
    },
    "shell bangle": {
      "description": "Ornament made from shell worn on wrists",
      "era": "Prehistoric to historic periods",
      "material": "Shell, often from conch or other mollusks",
      "significance": "Indicates early personal adornment practices"
    },
    "pearl jewellery": {
      "description": "Ornaments made from pearls",
      "era": "Various historical periods",
      "material": "Pearls, often with metal settings",
      "significance": "Status symbol and trade commodity"
    },
    "alloy": {
      "description": "Metal object made from mixed metals",
      "era": "Bronze Age onwards",
      "material": "Mixed metals like bronze or brass",
      "significance": "Shows metallurgical knowledge"
    },
    "Blackstone": {
      "description": "Stone artifact, possibly ritual or functional",
      "era": "Varies by region and culture",
      "material": "Stone, often basalt or similar",
      "significance": "Ritual or utilitarian purposes"
    },
    "vatta_sillu": {
      "description": "Circular stone artifact",
      "era": "Ancient periods",
      "material": "Stone",
      "significance": "Possible gaming piece or ritual object"
    },
    "pottery": {
      "description": "Ceramic vessels or fragments",
      "era": "Neolithic period onwards",
      "material": "Fired clay",
      "significance": "Key artifact for dating archaeological sites"
    }
  };
  
  // Mock classification function - in a real app, this would use a trained model
  export const classifyImage = async (imageUri: string): Promise<ClassificationResult> => {
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Generate random probabilities for demonstration
    const randomProbs = Array.from({length: ARCHAEOLOGY_LABELS.length}, () => Math.random());
    const total = randomProbs.reduce((sum, val) => sum + val, 0);
    const probabilities = randomProbs.map(p => p / total);
    
    const maxIndex = probabilities.indexOf(Math.max(...probabilities));
    const prediction = ARCHAEOLOGY_LABELS[maxIndex];
    
    return {
      prediction,
      confidence: probabilities[maxIndex],
      probabilities: ARCHAEOLOGY_LABELS.reduce((obj, label, idx) => {
        obj[label] = probabilities[idx];
        return obj;
      }, {} as Record<string, number>),
      details: OBJECT_DETAILS[prediction] || {
        description: "No information available",
        era: "Unknown",
        material: "Unknown",
        significance: "Unknown"
      }
    };
  };
  
  export const getLabelInfo = () => {
    return ARCHAEOLOGY_LABELS.map(label => ({
      name: label,
      displayName: label.charAt(0).toUpperCase() + label.slice(1),
      icon: getIconForLabel(label),
      description: OBJECT_DETAILS[label]?.description || "No description available"
    }));
  };
  
  const getIconForLabel = (label: string): string => {
    const iconMap: Record<string, string> = {
      "huntingtool": "⚔️",
      "Kendi": "🏺",
      "Thakli": "⚖️",
      "shell bangle": "📿",
      "pearl jewellery": "💎",
      "alloy": "🔩",
      "Blackstone": "🪨",
      "vatta_sillu": "⭕",
      "pottery": "🏺"
    };
    return iconMap[label] || "🔍";
  };