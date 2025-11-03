import React, { useState, useEffect, useRef } from 'react';
import * as tf from '@tensorflow/tfjs';
import { UploadCloud, Image as ImageIcon, CheckCircle, XCircle, Play, FolderOpen } from 'lucide-react';
import './App.css'; // Import our CSS for button hover effects

const App = () => {
  const [model, setModel] = useState(null);
  const [labels, setLabels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedImages, setSelectedImages] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const imageInputRef = useRef(null);

  // --- CORRECTED MODEL AND LABELS PATHS ---
  // Using absolute paths to ensure proper loading
  const MODEL_URL = './model.json'; // Path to your model.json relative to the public folder
  const LABELS_URL = './labels.txt'; // Path to your labels.txt relative to the public folder
  const IMAGE_SIZE = 224; // Model input size

  useEffect(() => {
    const loadModelAndLabels = async () => {
      try {
        setLoading(true);
        setError(null);

        // Load the TensorFlow.js model
        console.log('Loading model from:', MODEL_URL);
        console.log('Full model URL:', window.location.origin + MODEL_URL);
        const loadedModel = await tf.loadLayersModel(MODEL_URL);
        setModel(loadedModel);
        console.log('Model loaded successfully!');

        // Load the labels
        console.log('Loading labels from:', LABELS_URL);
        console.log('Full labels URL:', window.location.origin + LABELS_URL);
        const labelsResponse = await fetch(LABELS_URL);
        console.log('Labels response status:', labelsResponse.status);
        if (!labelsResponse.ok) {
          throw new Error(`HTTP error! status: ${labelsResponse.status}`);
        }
        const labelsText = await labelsResponse.text();
        console.log('Raw labels text:', labelsText);
        const loadedLabels = labelsText.split('\n').map(label => label.trim()).filter(label => label.length > 0);
        setLabels(loadedLabels);
        console.log('Labels loaded successfully:', loadedLabels);

      } catch (err) {
        console.error('Failed to load model or labels:', err);
        console.error('Error details:', err.message, err.stack);
        
        // Provide more specific error messages
        let errorMessage = `Failed to load model or labels: ${err.message}`;
        
        if (err.message.includes('fetch')) {
          errorMessage = 'Failed to fetch model files. Please check if the files are accessible.';
        } else if (err.message.includes('JSON')) {
          errorMessage = 'Failed to parse model.json. The file may be corrupted.';
        } else if (err.message.includes('weights')) {
          errorMessage = 'Failed to load model weights. Please ensure weights.bin is in the public folder.';
        }
        
        setError(`${errorMessage} Please ensure 'model.json', 'weights.bin', and 'labels.txt' are directly in the 'public/' directory.`);
      } finally {
        setLoading(false);
      }
    };

    loadModelAndLabels();
  }, []);

  const preprocessImage = (imgElement) => {
    const imgTensor = tf.browser.fromPixels(imgElement);
    const resized = tf.image.resizeBilinear(imgTensor, [IMAGE_SIZE, IMAGE_SIZE]);
    const normalized = resized.div(255.0);
    const batched = normalized.expandDims(0);
    return batched;
  };

  const classifyImage = async (imageSrc, imageFile) => {
    if (!model) {
      throw new Error("Model not loaded yet.");
    }

    return new Promise((resolve, reject) => {
      const img = new Image();
      img.src = imageSrc;
      img.onload = async () => {
        try {
          console.log('Starting image classification for:', imageFile.name);
          const preprocessedImage = preprocessImage(img);
          console.log('Image preprocessed, running prediction...');
          const predictions = model.predict(preprocessedImage);
          console.log('Prediction completed, processing results...');
          const scores = predictions.dataSync();

          const maxScoreIndex = scores.indexOf(Math.max(...scores));
          const predictedLabel = labels[maxScoreIndex];
          const confidence = scores[maxScoreIndex] * 100;

          console.log('Classification result:', { predictedLabel, confidence, scores });

          preprocessedImage.dispose();
          predictions.dispose();

          resolve({
            id: imageFile.id,
            file: imageFile,
            src: imageSrc,
            prediction: predictedLabel,
            confidence: confidence,
            error: null
          });

        } catch (err) {
          console.error("Error during classification:", err);
          reject({
            id: imageFile.id,
            file: imageFile,
            src: imageSrc,
            prediction: null,
            confidence: null,
            error: `Classification failed: ${err.message}`
          });
        }
      };
      img.onerror = (err) => {
        console.error("Error loading image for classification:", err);
        reject({
          id: imageFile.id,
          file: imageFile,
          src: imageSrc,
          prediction: null,
          confidence: null,
          error: "Failed to load image for processing."
        });
      };
    });
  };

  const handleImageSelection = (event) => {
    const files = Array.from(event.target.files);
    const imageFiles = files.map(file => ({
      id: Date.now() + Math.random() + Math.random(),
      file: file,
      src: URL.createObjectURL(file)
    }));
    
    setSelectedImages(prevImages => [...prevImages, ...imageFiles]);
  };

  const handleStartProcessing = async () => {
    if (!model) {
      setError("Model not loaded yet. Please wait for the AI model to finish loading.");
      return;
    }

    if (selectedImages.length === 0) {
      setError("Please select some images first.");
      return;
    }

    setProcessing(true);
    setError(null);
    setResults([]);

    try {
      const classificationPromises = selectedImages.map(img => classifyImage(img.src, img));
      const results = await Promise.all(classificationPromises);
      
      // Filter for only WES_ANDERSON images (simple yes/no, no confidence threshold)
      const wesAndersonImages = results.filter(result => 
        result.prediction === "WES_ANDERSON"
      );

      setResults(wesAndersonImages);
      
      if (wesAndersonImages.length === 0) {
        setError("No images were classified as Wes Anderson style.");
      }

    } catch (err) {
      console.error("Error during batch processing:", err);
      setError(`Processing failed: ${err.message}`);
    } finally {
      setProcessing(false);
    }
  };

  const clearAllImages = () => {
    setSelectedImages([]);
    setResults([]);
    setError(null);
  };

  const backgroundImageUrl = `${process.env.PUBLIC_URL || ''}/image1.png`;

  return (
    <div 
      className="wes-anderson-app"
      style={{ backgroundImage: `url(${backgroundImageUrl})` }}
    >
      {/* Background - Orange locker room aesthetic */}
      <div 
        className="background-container"
        style={{ backgroundImage: `url(${backgroundImageUrl})` }}
      >
        <div className="locker-room-background">
          {/* Orange lockers on left */}
          <div className="lockers-left">
            <div className="locker-row">
              {[...Array(6)].map((_, i) => (
                <div key={`left-top-${i}`} className="locker"></div>
              ))}
            </div>
            <div className="locker-row">
              {[...Array(6)].map((_, i) => (
                <div key={`left-bottom-${i}`} className="locker"></div>
              ))}
            </div>
            <div className="bench"></div>
          </div>
          
          {/* Orange lockers on right */}
          <div className="lockers-right">
            <div className="locker-row">
              {[...Array(6)].map((_, i) => (
                <div key={`right-top-${i}`} className="locker"></div>
              ))}
            </div>
            <div className="locker-row">
              {[...Array(6)].map((_, i) => (
                <div key={`right-bottom-${i}`} className="locker"></div>
              ))}
            </div>
            <div className="bench"></div>
          </div>
          
          {/* Central corridor */}
          <div className="central-corridor">
            <div className="ceiling-lights">
              {[...Array(5)].map((_, i) => (
                <div key={`light-${i}`} className="light"></div>
              ))}
            </div>
            <div className="back-wall"></div>
          </div>
        </div>
      </div>

      {/* Main interface overlay */}
      <div className="main-overlay">
        <div className="content-container">
          {/* Branding section */}
          <div className="branding-section">
            <h1 className="wesify-title">WESIFY</h1>
            <p className="tagline">see if your photos are accidentally wes anderson</p>
          </div>

          {/* Status messages */}
          {loading && (
            <div className="status-message loading">
              Loading AI Model...
            </div>
          )}

          {error && (
            <div className="status-message error">
              {error}
            </div>
          )}

          {processing && (
            <div className="status-message processing">
              Analyzing images...
            </div>
          )}

          {/* Interactive buttons */}
          <div className="button-container">
            <button
              onClick={() => imageInputRef.current.click()}
              disabled={!model || processing}
              className="wes-button select-button"
            >
              Select Files
            </button>
            
            <button
              onClick={handleStartProcessing}
              disabled={!model || selectedImages.length === 0 || processing}
              className="wes-button start-button"
            >
              Start
            </button>

            {selectedImages.length > 0 && (
              <button
                onClick={clearAllImages}
                disabled={processing}
                className="wes-button clear-button"
              >
                Clear All
              </button>
            )}
          </div>

          {/* Hidden file input */}
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={handleImageSelection}
            ref={imageInputRef}
            className="hidden-input"
            disabled={!model || processing}
          />

          {/* Image preview area */}
          {selectedImages.length > 0 && (
            <div className="image-preview-section">
              <h3>Selected Images ({selectedImages.length})</h3>
              <div className="image-grid">
                {selectedImages.map(img => (
                  <div key={img.id} className="image-preview">
                    <img src={img.src} alt="Selected" />
                    <p>{img.file.name}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Results section */}
          {results.length > 0 && (
            <div className="results-section">
              <h3>Wes Anderson Style Images ({results.length})</h3>
              <div className="results-grid">
                {results.map(img => (
                  <div key={img.id} className="result-card">
                    <img src={img.src} alt="Wes Anderson Style" />
                    <div className="result-info">
                      <p className="prediction">
                        <span className="label">STYLE MATCH:</span> 
                        <span className="percentage">{img.confidence.toFixed(1)}%</span>
                      </p>
                      <p className="filename">{img.file.name}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No results message */}
          {results.length === 0 && !processing && selectedImages.length > 0 && !error && (
            <div className="no-results">
              <h3>Images Selected!</h3>
              <p>Click "Start" to analyze your images for Wes Anderson style.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
