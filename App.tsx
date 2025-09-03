// App.tsx
import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ScrollView, ActivityIndicator, Alert, Platform } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Camera, useCameraDevices } from 'react-native-vision-camera';
import { launchImageLibrary } from 'react-native-image-picker';

const Stack = createStackNavigator();

// Mock data - replace with your actual model service
const LABELS = [
  { name: "huntingtool", displayName: "Hunting Tool", icon: "⚔️", description: "Prehistoric tools used for hunting animals" },
  { name: "Kendi", displayName: "Kendi Vessel", icon: "🏺", description: "Traditional Southeast Asian drinking vessels" },
  { name: "Thakli", displayName: "Thakli Weight", icon: "⚖️", description: "Ancient weight measures and tools" },
  { name: "shell bangle", displayName: "Shell Bangle", icon: "💍", description: "Ornaments made from shells worn on wrists" },
  { name: "Bead-Jewellery", displayName: "Bead Jewellery", icon: "💎", description: "Ornaments made from beads and precious stones" },
  { name: "alloy", displayName: "Metal Alloy", icon: "🔩", description: "Objects made from mixed metals like bronze or brass" },
  { name: "blackstone", displayName: "Blackstone Artifact", icon: "🪨", description: "Stone artifacts for ritual or functional purposes" },
  { name: "vatta_sillu", displayName: "Vatta Sillu", icon: "⭕", description: "Circular stone artifacts and gaming pieces" },
  { name: "pottery", displayName: "Pottery", icon: "🏺", description: "Ceramic vessels and fragments from various eras" }
];

// Mock classification function - replace with your actual API call
const classifyImage = async (imagePath: string) => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 2000));
  const randomLabel = LABELS[Math.floor(Math.random() * LABELS.length)];
  return {
    prediction: randomLabel.name,
    confidence: Math.random() * 0.5 + 0.5, // Random confidence between 0.5 and 1.0
    details: {
      description: randomLabel.description,
      era: "Various periods",
      material: "Various materials",
      significance: "Archaeological significance"
    }
  };
};

function HomeScreen({ navigation }: any) {
  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Archaeological Classifier</Text>
      <Text style={styles.subtitle}>AI-Powered Artifact Identification</Text>
      
      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('Camera')}>
        <Text style={styles.buttonText}>Live Camera</Text>
      </TouchableOpacity>
      
      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('Upload')}>
        <Text style={styles.buttonText}>Upload Image</Text>
      </TouchableOpacity>
      
      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('Results')}>
        <Text style={styles.buttonText}>View Results</Text>
      </TouchableOpacity>
      
      <TouchableOpacity style={styles.infoButton} onPress={() => navigation.navigate('Labels')}>
        <Text style={styles.infoButtonText}>View Classification Labels</Text>
      </TouchableOpacity>
    </View>
  );
}

function CameraScreen() {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [isActive, setIsActive] = useState(true);
  const [loading, setLoading] = useState(false);
  const camera = useRef<Camera>(null);
  const devices = useCameraDevices();
  const device = devices.back;

  useEffect(() => {
    (async () => {
      const status = await Camera.requestCameraPermission();
      setHasPermission(status === 'authorized');
    })();
  }, []);

  if (hasPermission === null) {
    return <View style={styles.container}><Text>Requesting permission...</Text></View>;
  }

  if (hasPermission === false) {
    return <View style={styles.container}><Text>No access to camera</Text></View>;
  }

  if (device == null) {
    return <View style={styles.container}><Text>Camera device not found</Text></View>;
  }

  const takePhoto = async () => {
    if (camera.current) {
      setLoading(true);
      try {
        const photo = await camera.current.takePhoto({});
        const result = await classifyImage(photo.path);
        Alert.alert(
          'Classification Result', 
          `Object: ${result.prediction}\nConfidence: ${(result.confidence * 100).toFixed(2)}%`
        );
      } catch (error) {
        Alert.alert('Error', 'Failed to take picture');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <View style={styles.cameraContainer}>
      <Camera
        ref={camera}
        style={StyleSheet.absoluteFill}
        device={device}
        isActive={isActive}
        photo={true}
      />
      
      <View style={styles.cameraControls}>
        <TouchableOpacity style={styles.captureButton} onPress={takePhoto}>
          <Text style={styles.captureButtonText}>📸</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.closeButton} onPress={() => setIsActive(false)}>
          <Text style={styles.closeButtonText}>✕</Text>
        </TouchableOpacity>
      </View>
      
      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="white" />
          <Text style={styles.loadingText}>Processing...</Text>
        </View>
      )}
    </View>
  );
}

function UploadScreen() {
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    setLoading(true);
    try {
      const result = await launchImageLibrary({
        mediaType: 'photo',
        quality: 0.8,
      });

      if (result.assets && result.assets[0]) {
        const result = await classifyImage(result.assets[0].uri || '');
        Alert.alert(
          'Classification Result', 
          `Object: ${result.prediction}\nConfidence: ${(result.confidence * 100).toFixed(2)}%`
        );
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Upload Image</Text>
      <Text style={styles.subtitle}>Select an image from your gallery</Text>
      
      <TouchableOpacity style={styles.button} onPress={pickImage}>
        <Text style={styles.buttonText}>Choose Image</Text>
      </TouchableOpacity>
      
      <Text style={styles.uploadHint}>
        Supported formats: JPG, PNG, HEIC
      </Text>
      
      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="white" />
          <Text style={styles.loadingText}>Processing...</Text>
        </View>
      )}
    </View>
  );
}

function ResultsScreen() {
  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Results</Text>
      <Text style={styles.comingSoon}>Results history coming soon...</Text>
    </View>
  );
}

function LabelsScreen() {
  return (
    <ScrollView style={styles.screen}>
      <Text style={styles.title}>Classification Labels</Text>
      <Text style={styles.subtitle}>Objects this AI can identify</Text>
      
      {LABELS.map((label, index) => (
        <View key={index} style={styles.labelItem}>
          <Text style={styles.labelIcon}>{label.icon}</Text>
          <View style={styles.labelInfo}>
            <Text style={styles.labelName}>{label.displayName}</Text>
            <Text style={styles.labelDescription}>{label.description}</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen 
          name="Home" 
          component={HomeScreen} 
          options={{ title: 'Archaeological Classifier' }}
        />
        <Stack.Screen 
          name="Camera" 
          component={CameraScreen} 
          options={{ title: 'Live Camera' }}
        />
        <Stack.Screen 
          name="Upload" 
          component={UploadScreen} 
          options={{ title: 'Upload Image' }}
        />
        <Stack.Screen 
          name="Results" 
          component={ResultsScreen} 
          options={{ title: 'Results' }}
        />
        <Stack.Screen 
          name="Labels" 
          component={LabelsScreen} 
          options={{ title: 'Classification Labels' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2c3e50',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#7f8c8d',
    textAlign: 'center',
    marginBottom: 30,
  },
  button: {
    backgroundColor: '#3498db',
    padding: 15,
    borderRadius: 10,
    margin: 10,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  infoButton: {
    backgroundColor: '#95a5a6',
    padding: 15,
    borderRadius: 10,
    margin: 10,
    alignItems: 'center',
  },
  infoButtonText: {
    color: 'white',
    fontSize: 14,
  },
  cameraContainer: {
    flex: 1,
  },
  cameraControls: {
    position: 'absolute',
    bottom: 30,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButton: {
    backgroundColor: 'rgba(255,255,255,0.3)',
    padding: 20,
    borderRadius: 50,
    marginHorizontal: 20,
  },
  captureButtonText: {
    fontSize: 24,
  },
  closeButton: {
    backgroundColor: 'rgba(255,255,255,0.3)',
    padding: 15,
    borderRadius: 25,
  },
  closeButtonText: {
    fontSize: 18,
    color: 'white',
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: 'white',
    marginTop: 10,
  },
  uploadHint: {
    textAlign: 'center',
    color: '#7f8c8d',
    marginTop: 10,
  },
  comingSoon: {
    textAlign: 'center',
    fontSize: 18,
    color: '#7f8c8d',
    marginTop: 20,
  },
  labelItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: 'white',
    margin: 10,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  labelIcon: {
    fontSize: 30,
    marginRight: 15,
  },
  labelInfo: {
    flex: 1,
  },
  labelName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 5,
  },
  labelDescription: {
    fontSize: 14,
    color: '#7f8c8d',
  },
});