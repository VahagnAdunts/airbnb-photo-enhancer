# 🏠 Airbnb Photo Enhancer

A professional web application that uses AI (LLM) to analyze and enhance Airbnb listing photos. Upload your photos, and the system will intelligently improve them using Google Gemini for analysis and professional image processing techniques.

## Features

- 📸 **Drag & Drop Upload**: Easy photo upload interface
- 🤖 **AI-Powered Analysis**: Uses Google Gemini to analyze each photo
- ✨ **Intelligent Enhancement**: Applies professional enhancements based on AI analysis
- 🎨 **Professional Quality**: Optimized for Airbnb listing standards
- 📊 **Progress Tracking**: Real-time progress updates for each photo
- 🔄 **Before/After Comparison**: Compare original and enhanced photos side-by-side
- 💾 **Batch Download**: Download all enhanced photos at once

## How It Works

1. **Upload**: Users upload one or multiple photos of their Airbnb listings
2. **Analysis**: Each photo is analyzed by Google Gemini using a comprehensive prompt that evaluates:
   - Lighting conditions and exposure
   - Color accuracy and saturation
   - Sharpness and focus
   - Composition and perspective
   - Airbnb-specific appeal factors
3. **Enhancement**: Based on the AI analysis, the system applies:
   - Brightness and contrast adjustments
   - Color saturation and vibrance improvements
   - Sharpness enhancement
   - Composition corrections (rotation, straightening)
   - Professional touches (noise reduction, etc.)
4. **Download**: Users can download individual or all enhanced photos

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (get it from https://makersuite.google.com/app/apikey)

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd airbnb_photoh_enhancment
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Gemini API Key**:
   
   Option 1: Environment variable (recommended)
   ```bash
   export GEMINI_API_KEY='your-api-key-here'
   ```
   
   Option 2: Create a `.env` file (you'll need python-dotenv):
   ```bash
   echo "GEMINI_API_KEY=your-api-key-here" > .env
   ```
   
   Get your API key from: https://makersuite.google.com/app/apikey

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
airbnb_photoh_enhancment/
├── app.py                 # Flask backend server
├── image_enhancer.py      # Image enhancement service with LLM integration
├── index.html             # Frontend HTML
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── app.js         # Frontend JavaScript
├── uploads/               # Original uploaded images (created automatically)
├── enhanced/              # Enhanced images (created automatically)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Enhancement Prompt

The system uses a comprehensive prompt that guides the LLM to analyze images specifically for Airbnb listings. The prompt evaluates:

- **Overall Assessment**: General quality and professional appearance
- **Lighting**: Brightness, contrast, and exposure analysis
- **Color**: Saturation, vibrance, and white balance
- **Sharpness**: Focus quality and sharpening needs
- **Composition**: Framing, perspective, and straightening
- **Professional Touches**: Distraction removal, ambiance enhancement
- **Airbnb-Specific**: Space effectiveness, inviting appearance, guest appeal

The prompt is designed to ensure photos meet professional Airbnb listing standards while maintaining accuracy and authenticity.

## API Endpoints

### `POST /api/enhance`

Upload and enhance an image.

**Request**:
- Content-Type: `multipart/form-data`
- Body: `image` (file)

**Response**:
```json
{
  "success": true,
  "original_image_url": "data:image/jpeg;base64,...",
  "enhanced_image_url": "data:image/jpeg;base64,...",
  "enhancements": {
    "overall_assessment": "...",
    "lighting": "...",
    "color": "...",
    "sharpness": "...",
    "airbnb_recommendations": "..."
  }
}
```

## Configuration

You can modify the enhancement behavior by editing `image_enhancer.py`:

- Adjust the enhancement prompt in `_get_enhancement_prompt()`
- Modify enhancement application logic in `_apply_enhancements()`
- Change default values in `_get_default_analysis()`

## Notes

- The application processes images one by one to ensure quality
- Enhanced images are saved as JPEG with 95% quality
- Original images are preserved in the `uploads/` folder
- The system uses Google Gemini (gemini-1.5-pro) for image analysis
- If the LLM API call fails, the system falls back to default enhancement values

## Troubleshooting

**Gemini API Errors**:
- Ensure your API key is set correctly
- Check that you have access to Gemini models
- Verify your API quota/billing is set up
- Get your API key from: https://makersuite.google.com/app/apikey

**Image Processing Errors**:
- Ensure uploaded files are valid image formats (PNG, JPG, JPEG, GIF, WEBP)
- Check that the `uploads/` and `enhanced/` directories are writable

**Port Already in Use**:
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

## License

This project is open source and available for personal and commercial use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

