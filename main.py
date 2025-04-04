import requests
import io
import base64
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
from google.colab import files

# For local testing without Cloudflare Worker
import re
import numpy as np

def upload_and_analyze_image():
    """Upload an image and send it to Cloudflare Worker for OCR and depression analysis"""
    
    print("Please upload an image of handwritten text:")
    uploaded = files.upload()
    
    for filename in uploaded.keys():
        # Display the uploaded image
        img = Image.open(io.BytesIO(uploaded[filename]))
        plt.figure(figsize=(10, 10))
        plt.imshow(img)
        plt.axis('off')
        plt.title(f"Uploaded Image: {filename}")
        plt.show()
        
        # Send to Cloudflare Worker
        # Replace with your actual worker URL
        worker_url = "https://dp-worker.ayushsachan49.workers.dev/"
        
        # Create form data with the image
        files = {'image': (filename, uploaded[filename])}
        
        print("Sending to OCR and depression analysis...")
        response = requests.post(worker_url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n--- EXTRACTED TEXT ---")
            print(result['extractedText'])
            
            print("\n--- DEPRESSION ANALYSIS ---")
            print(f"Depression Score: {result['depressionScore']}/25")
            print(f"Interpretation: {result['interpretations']}")
            
            # Visualize the score
            visualize_depression_score(result['depressionScore'])
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

def visualize_depression_score(score):
    """Create a visual representation of the depression score"""
    
    categories = [
        "Minimal (0-5)",
        "Mild (5-10)",
        "Moderate (10-15)",
        "Moderately Severe (15-20)",
        "Severe (20-25)"
    ]
    
    # Determine which category the score falls into
    if score < 5:
        category_index = 0
    elif score < 10:
        category_index = 1
    elif score < 15:
        category_index = 2
    elif score < 20:
        category_index = 3
    else:
        category_index = 4
    
    # Create bar colors (highlight the relevant category)
    colors = ['lightgray'] * 5
    colors[category_index] = 'blue'
    
    # Create a figure showing the score on a scale
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [1, 2]})
    
    # Top plot: score on a continuous scale
    ax1.set_xlim(0, 25)
    ax1.set_title(f"Depression Score: {score}/25")
    ax1.axvline(x=score, color='red', linestyle='-', linewidth=2)
    ax1.set_yticks([])
    
    # Add color bands for different severity levels
    ax1.axvspan(0, 5, alpha=0.2, color='green')
    ax1.axvspan(5, 10, alpha=0.2, color='yellow')
    ax1.axvspan(10, 15, alpha=0.2, color='orange')
    ax1.axvspan(15, 20, alpha=0.3, color='red')
    ax1.axvspan(20, 25, alpha=0.4, color='darkred')
    
    # Add severity labels
    for i, (start, end, label) in enumerate([(0, 5, 'Minimal'), 
                                            (5, 10, 'Mild'), 
                                            (10, 15, 'Moderate'),
                                            (15, 20, 'Mod. Severe'),
                                            (20, 25, 'Severe')]):
        ax1.text((start+end)/2, 0.5, label, ha='center', va='center', fontsize=9)
    
    # Bottom plot: category breakdown
    ax2.bar(categories, [1, 1, 1, 1, 1], color=colors)
    ax2.set_ylabel('Current Level')
    ax2.set_title('Depression Severity Classification')
    
    plt.tight_layout()
    plt.show()

# Optional: Add a local testing function for development without Cloudflare
def local_test_with_text_input():
    """Test depression analysis with directly entered text"""
    
    print("Enter text for depression analysis (without sending to Cloudflare):")
    text = input()
    
    # Simple scoring algorithm for local testing
    score = 12.5  # Start at middle
    
    # Depression indicators with weights
    indicators = [
        (r'hopeless|worthless|emptiness|despair', 1.5),
        (r'sad|down|low|blue|unhappy', 0.8),
        (r'tired|exhausted|fatigue|no energy', 0.7),
        (r'alone|lonely|isolated', 0.9),
        (r'suicide|death|dying|end it', 2.5),
        (r'guilt|blame|fault|shame', 1.0)
    ]
    
    # Positive indicators
    positive = [
        (r'happy|joy|grateful|thankful', -1.0),
        (r'hopeful|looking forward|excited', -1.2),
        (r'energetic|motivated|inspired', -0.7)
    ]
    
    # Calculate score based on text patterns
    for pattern, weight in indicators:
        matches = len(re.findall(pattern, text, re.IGNORECASE))
        score += matches * weight
    
    for pattern, weight in positive:
        matches = len(re.findall(pattern, text, re.IGNORECASE))
        score += matches * weight
    
    # Ensure score stays within range
    score = max(0, min(25, score))
    
    print(f"\nDepression Score: {score:.1f}/25")
    
    # Determine interpretation
    if score < 5:
        interp = "Minimal or no depression indicators detected"
    elif score < 10:
        interp = "Mild depression indicators detected"
    elif score < 15:
        interp = "Moderate depression indicators detected"
    elif score < 20:
        interp = "Moderately severe depression indicators detected"
    else:
        interp = "Severe depression indicators detected"
    
    print(f"Interpretation: {interp}")
    visualize_depression_score(score)

# Main menu
def main():
    print("Depression Analysis from Handwritten Journals")
    print("1. Upload image for OCR and depression analysis")
    print("2. Local text testing (without Cloudflare)")
    
    choice = input("\nEnter your choice (1 or 2): ")
    
    if choice == '1':
        upload_and_analyze_image()
    elif choice == '2':
        local_test_with_text_input()
    else:
        print("Invalid choice")

# Run the main function
if __name__ == "__main__":
    main()