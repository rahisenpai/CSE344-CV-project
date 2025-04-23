import streamlit as st
import tempfile
from pipeline.main import process_video
import os
os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"

# Custom CSS with dark traffic-inspired theme
def set_custom_style():
    st.markdown("""
    <style>
    /* Dark traffic-inspired color palette */
    .stApp {
        background-color: #1c2331;
        color: #e0e0e0;
        font-family: 'Arial', sans-serif;
    }
    
    /* Road-inspired title style */
    .title {
        color: #4db8ff;
        text-align: center;
        font-weight: bold;
        margin-bottom: 30px;
        font-size: 2.5em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Dark file uploader */
    .stFileUploader {
        background-color: #2c3e50;
        border: 2px solid #4db8ff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    
    /* Sidebar like a dark control panel */
    .css-1aumxhk {
        background-color: #273746;
        border: 2px solid #34495e;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    /* Dark buttons styled like traffic signals */
    .stButton>button {
        background-color: #2ecc71;  /* Green for go */
        color: #1c2331;
        border-radius: 8px;
        border: 2px solid #27ae60;
        padding: 10px 20px;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #27ae60;
        transform: scale(1.05);
    }
    
    /* Dark info message like a road warning */
    .stAlert {
        border-radius: 8px;
        background-color: #34495e;
        color: #ecf0f1;
        border: 2px solid #4db8ff;
    }
    
    /* Text color adjustments */
    .stMarkdown, .stText {
        color: #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Apply custom styling
    set_custom_style()
    
    # Updated title to reflect specific detection focus
    st.markdown('<h1 class="title">⛔ Helmet Violation Detection </h1>', unsafe_allow_html=True)
    
    # Video upload with traffic-inspired styling
    st.markdown("### 📹 Upload Traffic Video")
    uploaded_file = st.file_uploader(
        "Choose a video file", 
        type=['mp4', 'avi', 'mov'], 
        help="Upload a traffic surveillance video"
    )
    
    # Process video when uploaded
    if uploaded_file is not None:
        # Create two columns for better layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎥 Uploaded Video")
            st.video(uploaded_file)
        
        with col2:
            st.markdown("### 📋 Video Details")
            st.write(f"Filename: {uploaded_file.name}")
            st.write(f"File Size: {uploaded_file.size} bytes")
        
        # Detection button with traffic signal styling
        if st.button("🚨 Start Detection"):
            # st.info("🚧 Detection functionality will be implemented soon")
            with st.spinner("Processing video..."):
                # Save to temp file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_file.write(uploaded_file.read())
                temp_file.close()

                # Run detection
                csv_output = process_video(temp_file.name)

                st.success("Detection complete!")
                st.download_button(
                    label="📥 Download CSV",
                    data=open(csv_output, "rb"),
                    file_name="detection_results.csv",
                    mime="text/csv"
                )
                os.remove(temp_file.name)

if __name__ == "__main__":
    main()