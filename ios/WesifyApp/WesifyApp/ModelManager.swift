//
//  ModelManager.swift
//  WesifyApp
//
//  Manages TensorFlow Lite model loading and inference
//
//  Note: This uses TensorFlow Lite iOS APIs. If you encounter compilation errors,
//  you may need to adjust the API calls based on your TensorFlow Lite version.
//

import UIKit
import TensorFlowLite

struct ClassificationResult {
    let image: UIImage
    let label: String
    let confidence: Float
}

@MainActor
class ModelManager: ObservableObject {
    @Published var isModelReady = false
    @Published var isLoading = true
    @Published var loadError: String?
    
    private var interpreter: Interpreter?
    private let labels = ["WES_ANDERSON", "NOT_WES_ANDERSON", "OTHER"]
    private let imageSize: Int = 224
    
    init() {
        Task {
            await loadModel()
        }
    }
    
    private func loadModel() async {
        isLoading = true
        loadError = nil
        
        guard let modelPath = Bundle.main.path(forResource: "model", ofType: "tflite") else {
            loadError = "Model file (model.tflite) not found in app bundle. Please ensure the model is added to the project."
            isLoading = false
            return
        }
        
        do {
            // Initialize TensorFlow Lite interpreter
            var options = Interpreter.Options()
            options.threadCount = 4
            interpreter = try Interpreter(modelPath: modelPath, options: options)
            
            // Allocate tensors
            try interpreter?.allocateTensors()
            
            // Get input tensor details
            let inputTensor = try interpreter?.input(at: 0)
            print("Model loaded successfully!")
            print("Input shape: \(inputTensor?.shape ?? [])")
            print("Input data type: \(inputTensor?.dataType ?? .float32)")
            
            isModelReady = true
            isLoading = false
            
        } catch {
            loadError = "Failed to load model: \(error.localizedDescription)"
            isLoading = false
            print("Error loading model: \(error)")
        }
    }
    
    func classify(image: UIImage) async -> ClassificationResult? {
        guard let interpreter = interpreter else {
            return nil
        }
        
        // Preprocess image (this allocates memory that needs to be freed)
        guard let pixelBuffer = preprocessImage(image: image) else {
            return nil
        }
        
        // Ensure pixel buffer is deallocated even if an error occurs
        defer {
            pixelBuffer.deallocate()
        }
        
        do {
            // Copy pixel buffer to input tensor
            let inputTensor = try interpreter.input(at: 0)
            let inputData = pixelBuffer.baseAddress
            
            // Get the size of the input tensor
            let inputSize = inputTensor.shape.dimensions.reduce(1, { $0 * $1 }) * MemoryLayout<Float>.size
            
            inputTensor.data.copyBytes(from: inputData!, count: inputSize)
            
            // Run inference
            try interpreter.invoke()
            
            // Get output tensor
            let outputTensor = try interpreter.output(at: 0)
            let outputSize = outputTensor.shape.dimensions.reduce(1, { $0 * $1 })
            let outputData = outputTensor.data
            
            // Convert output to array of floats
            var probabilities: [Float] = []
            outputData.withUnsafeBytes { (pointer: UnsafeRawBufferPointer) in
                let floatPointer = pointer.bindMemory(to: Float.self)
                probabilities = Array(UnsafeBufferPointer(start: floatPointer.baseAddress, count: outputSize))
            }
            
            // Find the class with highest probability
            guard let maxIndex = probabilities.indices.max(by: { probabilities[$0] < probabilities[$1] }) else {
                return nil
            }
            
            let predictedLabel = labels[maxIndex]
            let confidence = probabilities[maxIndex] * 100.0
            
            return ClassificationResult(
                image: image,
                label: predictedLabel,
                confidence: confidence
            )
            
        } catch {
            print("Error during classification: \(error)")
            return nil
        }
    }
    
    private func preprocessImage(image: UIImage) -> UnsafeMutablePointer<Float>? {
        // Resize image to model input size (224x224)
        guard let resizedImage = image.resize(to: CGSize(width: imageSize, height: imageSize)) else {
            return nil
        }
        
        guard let cgImage = resizedImage.cgImage else {
            return nil
        }
        
        let width = cgImage.width
        let height = cgImage.height
        let bytesPerPixel = 4
        let bytesPerRow = bytesPerPixel * width
        let bitsPerComponent = 8
        
        // Create bitmap context
        guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB),
              let context = CGContext(
                data: nil,
                width: width,
                height: height,
                bitsPerComponent: bitsPerComponent,
                bytesPerRow: bytesPerRow,
                space: colorSpace,
                bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
              ) else {
            return nil
        }
        
        context.draw(cgImage, in: CGRect(x: 0, y: 0, width: width, height: height))
        
        guard let pixelData = context.data else {
            return nil
        }
        
        // Allocate memory for normalized pixel buffer
        let pixelCount = width * height * 3 // RGB channels
        let pixelBuffer = UnsafeMutablePointer<Float>.allocate(capacity: pixelCount)
        pixelBuffer.initialize(repeating: 0, count: pixelCount)
        
        // Convert RGBA to RGB and normalize to [0, 1]
        let data = pixelData.assumingMemoryBound(to: UInt8.self)
        for y in 0..<height {
            for x in 0..<width {
                let pixelIndex = y * width + x
                let rgbaIndex = pixelIndex * 4
                
                // Extract RGB values and normalize
                let r = Float(data[rgbaIndex]) / 255.0
                let g = Float(data[rgbaIndex + 1]) / 255.0
                let b = Float(data[rgbaIndex + 2]) / 255.0
                
                // Store in RGB order for model input
                let rgbIndex = (y * width + x) * 3
                pixelBuffer[rgbIndex] = r
                pixelBuffer[rgbIndex + 1] = g
                pixelBuffer[rgbIndex + 2] = b
            }
        }
        
        return pixelBuffer
    }
}

// UIImage extension for resizing
extension UIImage {
    func resize(to size: CGSize) -> UIImage? {
        UIGraphicsBeginImageContextWithOptions(size, false, scale)
        defer { UIGraphicsEndImageContext() }
        draw(in: CGRect(origin: .zero, size: size))
        return UIGraphicsGetImageFromCurrentImageContext()
    }
}
