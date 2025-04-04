import streamlit as st
import requests
import io
import base64
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np

def main():
    st.set_page_config(page_title="Depression Analysis Tool", layout="wide")
    
    st.title("Depression Analysis from Handwritten Journals")
    st.write("This tool analyzes handwritten text for potential signs of depression.")
    
    # Create tabs for different analysis methods
    tab1, tab2 = st.tabs(["Image Upload & OCR", "Direct Text Input"])
    
    with tab1:
        image_analysis()
    
    with tab2:
        text_analysis()

def image_analysis():
    st.header("Upload Image for OCR and Depression Analysis")
    
    uploaded_file = st.file_uploader("Upload an image of handwritten text", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Analyze Image"):
            with st.spinner("Analyzing..."):
                # Prepare image for sending
                img_bytes = io.BytesIO()
                image.save(img_bytes, format=image.format)
                img_bytes = img_bytes.getvalue()
                
                # Process with OCR and depression analysis
                try:
                    # Replace with your worker URL
                    worker_url = "https://dp-worker.ayushsachan49.workers.dev/"
                    files = {'image': ('image.jpg', img_bytes)}
                    
                    response = requests.post(worker_url, files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display results
                        st.subheader("Extracted Text")
                        st.write(result['extractedText'])
                        
                        st.subheader("Depression Analysis Results")
                        st.write(f"Depression Score: {result['depressionScore']}/25")
                        st.write(f"Interpretation: {result['interpretations']}")
                        
                        # Show visualization
                        fig = visualize_depression_score(result['depressionScore'])
                        st.pyplot(fig)
                        
                        # Show recommendations based on score
                        display_recommendations(result['depressionScore'])
                    else:
                        st.error(f"Error: {response.status_code}")
                        st.error(response.text)
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                    st.info("Falling back to local analysis. Note: OCR functionality is not available locally.")
                    st.info("Try the Direct Text Input tab instead.")

def text_analysis():
    st.header("Direct Text Input for Depression Analysis")
    
    text = st.text_area("Enter journal text for analysis:", height=200)
    
    if st.button("Analyze Text"):
        if text:
            with st.spinner("Analyzing..."):
                # Process the text locally
                score, interpretation = analyze_text_locally(text)
                
                st.subheader("Depression Analysis Results")
                st.write(f"Depression Score: {score:.1f}/25")
                st.write(f"Interpretation: {interpretation}")
                
                # Show visualization
                fig = visualize_depression_score(score)
                st.pyplot(fig)
                
                # Show recommendations
                display_recommendations(score)
        else:
            st.warning("Please enter some text to analyze.")

def analyze_text_locally(text):
    """Analyze text for depression indicators without using external APIs"""
    
    # Start at middle for balanced assessment
    score = 12.5
    
    # Depression indicators with weights
    indicators = [
        (r'hopeless|worthless|emptiness|despair', 1.5),
        (r'sad|down|low|blue|unhappy', 0.8),
        (r'tired|exhausted|fatigue|no energy', 0.7),
        (r'alone|lonely|isolated', 0.9),
        (r'suicide|death|dying|end it', 2.5),
        (r'guilt|blame|fault|shame', 1.0),
        (r'anxiety|anxious|worry|worried|panic', 0.8),
        (r'sleep|insomnia|nightmare', 0.7),
        (r'appetite|eating|weight', 0.6),
        (r'concentration|focus|distract', 0.7)
    ]
    
    # Positive indicators
    positive = [
        (r'happy|joy|grateful|thankful', -1.0),
        (r'hopeful|looking forward|excited', -1.2),
        (r'energetic|motivated|inspired', -0.7),
        (r'accomplish|achievement|proud', -0.9),
        (r'support|friend|family|love', -0.8),
        (r'calm|peaceful|relaxed', -0.6)
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
    
    return score, interp

def visualize_depression_score(score):
    """Create a visual representation of the depression score"""
    
    # Convert to float if necessary
    score = float(score)
    
    categories = [
        "Minimal\n(0-5)",
        "Mild\n(5-10)",
        "Moderate\n(10-15)",
        "Mod. Severe\n(15-20)",
        "Severe\n(20-25)"
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
    ax1.set_title(f"Depression Score: {score:.1f}/25")
    ax1.axvline(x=score, color='red', linestyle='-', linewidth=2)
    ax1.set_yticks([])
    
    # Add color bands for different severity levels
    ax1.axvspan(0, 5, alpha=0.2, color='green')
    ax1.axvspan(5, 10, alpha=0.2, color='yellow')
    ax1.axvspan(10, 15, alpha=0.2, color='orange')
    ax1.axvspan(15, 20, alpha=0.3, color='red')
    ax1.axvspan(20, 25, alpha=0.4, color='darkred')
    
    # Add severity labels
    for i, (start, end, label) in enumerate([
        (0, 5, 'Minimal'), 
        (5, 10, 'Mild'), 
        (10, 15, 'Moderate'),
        (15, 20, 'Mod. Severe'),
        (20, 25, 'Severe')
    ]):
        ax1.text((start+end)/2, 0.5, label, ha='center', va='center', fontsize=9)
    
    # Bottom plot: category breakdown
    ax2.bar(categories, [1, 1, 1, 1, 1], color=colors)
    ax2.set_ylabel('Current Level')
    ax2.set_title('Depression Severity Classification')
    
    plt.tight_layout()
    
    return fig

def display_recommendations(score):
    """Display appropriate recommendations based on the depression score"""
    
    score = float(score)
    
    st.subheader("Recommendations")
    
    if score < 5:
        st.write("• Continue with healthy habits and self-care")
        st.write("• Maintain your social connections")
        st.write("• Practice gratitude journaling")
    
    elif score < 10:
        st.write("• Consider increasing physical activity")
        st.write("• Practice mindfulness or meditation regularly")
        st.write("• Ensure you're getting enough sleep")
        st.write("• Talk to friends or family about how you're feeling")
    
    elif score < 15:
        st.write("• Consider speaking with a mental health professional")
        st.write("• Establish a regular exercise routine")
        st.write("• Practice stress reduction techniques")
        st.write("• Maintain a structured daily routine")
        st.write("• Consider joining a support group")
    
    elif score < 20:
        st.write("• Strongly recommended to consult with a mental health professional")
        st.write("• Establish regular check-ins with supportive friends or family")
        st.write("• Practice self-care and ensure basic needs are met")
        st.write("• Consider depression support groups or resources")
    
    else:
        st.write("• Please seek professional help promptly")
        st.write("• Contact a mental health provider or crisis hotline")
        st.write("• If you're having thoughts of suicide, call the National Suicide Prevention Lifeline: 988")
    
    st.info("**Disclaimer:** This tool provides an estimate only and is not a clinical diagnosis. Always consult with qualified mental health professionals for proper evaluation and treatment.")

if __name__ == "__main__":
    main()