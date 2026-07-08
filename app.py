import gradio as gr
import numpy as np
from PIL import Image
import tensorflow as tf

# Simple placeholder model (since your actual model isn't uploaded)
def predict(image):
    # This is a dummy prediction for demo
    # Replace this with your actual model loading code
    
    # For now, just show a sample response
    classes = ["Early Blight", "Late Blight", "Healthy"]
    
    # Simple logic based on image color (just for demo)
    img_array = np.array(image)
    avg_color = np.mean(img_array)
    
    if avg_color < 100:
        result = "Early Blight"
        confidence = 85.5
    elif avg_color < 150:
        result = "Late Blight"
        confidence = 78.2
    else:
        result = "Healthy"
        confidence = 92.3
    
    return f"🌱 **Result:** {result}\n📊 **Confidence:** {confidence:.1f}%"

# Create interface
iface = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil", label="Upload Potato Leaf Image"),
    outputs=gr.Textbox(label="Prediction Result", lines=3),
    title="🥔 Potato Disease Detection",
    description="Upload a photo of a potato leaf to detect disease",
    examples=[]
)

iface.launch()
