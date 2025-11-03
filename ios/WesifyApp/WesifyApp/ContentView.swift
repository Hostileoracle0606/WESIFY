//
//  ContentView.swift
//  WesifyApp
//
//  Main view for Wes Anderson Image Classifier
//

import SwiftUI
import PhotosUI

struct ContentView: View {
    @StateObject private var modelManager = ModelManager()
    @State private var selectedItems: [PhotosPickerItem] = []
    @State private var selectedImages: [UIImage] = []
    @State private var showingImagePicker = false
    @State private var showingCamera = false
    @State private var isProcessing = false
    @State private var results: [ClassificationResult] = []
    @State private var errorMessage: String?
    
    var body: some View {
        ZStack {
            // Background gradient - Wes Anderson inspired pastel colors
            LinearGradient(
                colors: [
                    Color(red: 1.0, green: 0.85, blue: 0.7),  // Peach
                    Color(red: 0.95, green: 0.9, blue: 0.85),   // Cream
                    Color(red: 0.9, green: 0.95, blue: 1.0)      // Soft blue
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 24) {
                    // Header
                    VStack(spacing: 8) {
                        Text("WESIFY")
                            .font(.system(size: 48, weight: .bold, design: .rounded))
                            .foregroundColor(.primary)
                        
                        Text("see if your photos are accidentally wes anderson")
                            .font(.system(size: 14, weight: .light))
                            .foregroundColor(.secondary)
                            .textCase(.lowercase)
                    }
                    .padding(.top, 40)
                    
                    // Model Status
                    if modelManager.isLoading {
                        HStack {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle())
                            Text("Loading AI Model...")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                        .padding()
                        .background(Color.white.opacity(0.3))
                        .cornerRadius(12)
                    } else if let error = modelManager.loadError {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Model Error")
                                .font(.headline)
                            Text(error)
                                .font(.caption)
                        }
                        .padding()
                        .background(Color.red.opacity(0.2))
                        .cornerRadius(12)
                    } else if modelManager.isModelReady {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                            Text("Model Ready")
                                .font(.subheadline)
                        }
                        .padding()
                        .background(Color.green.opacity(0.2))
                        .cornerRadius(12)
                    }
                    
                    // Action Buttons
                    HStack(spacing: 16) {
                        Button(action: {
                            showingImagePicker = true
                        }) {
                            HStack {
                                Image(systemName: "photo.on.rectangle")
                                Text("Select Photos")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                        }
                        .disabled(isProcessing || !modelManager.isModelReady)
                        
                        Button(action: {
                            showingCamera = true
                        }) {
                            HStack {
                                Image(systemName: "camera")
                                Text("Camera")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                        }
                        .disabled(isProcessing || !modelManager.isModelReady)
                    }
                    .padding(.horizontal)
                    
                    // Selected Images Preview
                    if !selectedImages.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                Text("Selected Images (\(selectedImages.count))")
                                    .font(.headline)
                                Spacer()
                                Button("Clear") {
                                    selectedImages.removeAll()
                                    results.removeAll()
                                    errorMessage = nil
                                }
                                .foregroundColor(.red)
                            }
                            
                            ScrollView(.horizontal, showsIndicators: false) {
                                HStack(spacing: 12) {
                                    ForEach(Array(selectedImages.enumerated()), id: \.offset) { index, image in
                                        Image(uiImage: image)
                                            .resizable()
                                            .scaledToFill()
                                            .frame(width: 100, height: 100)
                                            .clipped()
                                            .cornerRadius(8)
                                    }
                                }
                            }
                            
                            if !isProcessing {
                                Button(action: {
                                    processImages()
                                }) {
                                    HStack {
                                        Image(systemName: "play.fill")
                                        Text("Start Analysis")
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.orange)
                                    .foregroundColor(.white)
                                    .cornerRadius(12)
                                }
                            } else {
                                HStack {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle())
                                    Text("Analyzing images...")
                                        .font(.subheadline)
                                }
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.white.opacity(0.3))
                                .cornerRadius(12)
                            }
                        }
                        .padding()
                        .background(Color.white.opacity(0.3))
                        .cornerRadius(16)
                    }
                    
                    // Error Message
                    if let error = errorMessage {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Error")
                                .font(.headline)
                            Text(error)
                                .font(.caption)
                        }
                        .padding()
                        .background(Color.red.opacity(0.2))
                        .cornerRadius(12)
                    }
                    
                    // Results
                    if !results.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Wes Anderson Style Images (\(results.count))")
                                .font(.headline)
                            
                            LazyVGrid(columns: [
                                GridItem(.flexible()),
                                GridItem(.flexible())
                            ], spacing: 16) {
                                ForEach(Array(results.enumerated()), id: \.offset) { index, result in
                                    ResultCard(result: result)
                                }
                            }
                        }
                        .padding()
                        .background(Color.white.opacity(0.3))
                        .cornerRadius(16)
                    }
                    
                    // No results message
                    if results.isEmpty && !selectedImages.isEmpty && !isProcessing && errorMessage == nil {
                        VStack(spacing: 8) {
                            Image(systemName: "photo.badge.plus")
                                .font(.system(size: 40))
                                .foregroundColor(.secondary)
                            Text("Images Selected")
                                .font(.headline)
                            Text("Tap 'Start Analysis' to classify your images")
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)
                        }
                        .padding()
                        .background(Color.white.opacity(0.3))
                        .cornerRadius(16)
                    }
                }
                .padding()
            }
        }
        .photosPicker(
            isPresented: $showingImagePicker,
            selection: $selectedItems,
            maxSelectionCount: 50,
            matching: .images
        )
        .onChange(of: selectedItems) { newItems in
            loadSelectedPhotos(items: newItems)
        }
        .sheet(isPresented: $showingCamera) {
            CameraView { image in
                selectedImages.append(image)
            }
        }
    }
    
    private func loadSelectedPhotos(items: [PhotosPickerItem]) {
        Task {
            var loadedImages: [UIImage] = []
            
            for item in items {
                if let data = try? await item.loadTransferable(type: Data.self),
                   let image = UIImage(data: data) {
                    loadedImages.append(image)
                }
            }
            
            await MainActor.run {
                selectedImages.append(contentsOf: loadedImages)
            }
        }
    }
    
    private func processImages() {
        guard modelManager.isModelReady else {
            errorMessage = "Model is not ready yet. Please wait."
            return
        }
        
        guard !selectedImages.isEmpty else {
            errorMessage = "Please select some images first."
            return
        }
        
        isProcessing = true
        errorMessage = nil
        results.removeAll()
        
        Task {
            var wesAndersonImages: [ClassificationResult] = []
            
            for image in selectedImages {
                if let result = await modelManager.classify(image: image) {
                    // Only show images with >= 95% confidence for WES_ANDERSON
                    if result.label == "WES_ANDERSON" && result.confidence >= 95.0 {
                        wesAndersonImages.append(result)
                    }
                }
            }
            
            await MainActor.run {
                results = wesAndersonImages
                isProcessing = false
                
                if wesAndersonImages.isEmpty {
                    errorMessage = "No images were classified as Wes Anderson style with 95% or higher confidence."
                }
            }
        }
    }
}

struct ResultCard: View {
    let result: ClassificationResult
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(uiImage: result.image)
                .resizable()
                .scaledToFill()
                .frame(height: 150)
                .clipped()
                .cornerRadius(12)
            
            VStack(alignment: .leading, spacing: 4) {
                Text("WES ANDERSON STYLE")
                    .font(.caption)
                    .fontWeight(.bold)
                    .foregroundColor(.secondary)
                
                Text("\(Int(result.confidence))% match")
                    .font(.headline)
                    .foregroundColor(.primary)
            }
            .padding(.horizontal, 8)
            .padding(.bottom, 8)
        }
        .background(Color.white.opacity(0.5))
        .cornerRadius(12)
    }
}

struct CameraView: UIViewControllerRepresentable {
    let onImageSelected: (UIImage) -> Void
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.delegate = context.coordinator
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(onImageSelected: onImageSelected)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let onImageSelected: (UIImage) -> Void
        
        init(onImageSelected: @escaping (UIImage) -> Void) {
            self.onImageSelected = onImageSelected
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let image = info[.originalImage] as? UIImage {
                onImageSelected(image)
            }
            picker.dismiss(animated: true)
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            picker.dismiss(animated: true)
        }
    }
}

#Preview {
    ContentView()
}


