# Testing Guide for Airbnb Photo Enhancer

## Quick Test Methods

### 1. **Browser Test (Easiest)**

1. Make sure the server is running:
   ```bash
   cd "/Users/vahagn/Desktop/Ai Agents/airbnb_photoh_enhancment"
   source venv/bin/activate
   python app.py
   ```

2. Open your browser and go to:
   ```
   http://localhost:5000
   ```

3. Upload a test image:
   - Drag and drop a photo, or
   - Click the upload area and select a photo

4. Wait for processing (you'll see progress bars)

5. View the enhanced result and compare with original

### 2. **API Test Script**

Use the provided test script:

```bash
# Test server connection only
python test_api.py

# Test with an actual image
python test_api.py path/to/your/image.jpg
```

### 3. **Manual API Test with cURL**

Test the API endpoint directly:

```bash
# Test server is running
curl http://localhost:5000

# Test image upload (replace with your image path)
curl -X POST \
  -F "image=@/path/to/your/image.jpg" \
  http://localhost:5000/api/enhance
```

### 4. **Python Interactive Test**

```python
import requests

# Test upload
with open('test_image.jpg', 'rb') as f:
    files = {'image': ('test.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:5000/api/enhance', files=files)
    print(response.json())
```

## What to Test

### ✅ Basic Functionality
- [ ] Server starts without errors
- [ ] Homepage loads correctly
- [ ] Can upload a single image
- [ ] Can upload multiple images
- [ ] Progress bars show during processing
- [ ] Enhanced images are displayed
- [ ] Download button works
- [ ] Compare button shows before/after

### ✅ API Endpoints
- [ ] GET `/` returns HTML page
- [ ] POST `/api/enhance` accepts image files
- [ ] API returns JSON with enhanced image data
- [ ] Error handling for invalid files
- [ ] Error handling for missing API key

### ✅ Image Processing
- [ ] Images are enhanced (check visually)
- [ ] Original images are preserved
- [ ] Enhanced images are saved correctly
- [ ] Multiple formats supported (JPG, PNG, etc.)

### ✅ Error Cases
- [ ] Uploading non-image files shows error
- [ ] Missing API key shows appropriate error
- [ ] Invalid API key shows appropriate error
- [ ] Large files are handled gracefully

## Test Images

You can use any photo, but for best testing:
- Use a real Airbnb listing photo
- Try different lighting conditions
- Test with various image sizes
- Test with different formats (JPG, PNG)

## Troubleshooting

### Server won't start
- Check if port 5000 is in use: `lsof -i :5000`
- Kill existing process: `lsof -ti:5000 | xargs kill -9`
- Or change port in `app.py`

### API key errors
- Check `.env` file exists and has `OPENAI_API_KEY=your-key`
- Verify API key is valid at https://platform.openai.com/api-keys
- Check you have credits/quota available

### Images not processing
- Check server logs for errors
- Verify API key is set correctly
- Check internet connection (needed for OpenAI API)
- Verify image file is valid

### Slow processing
- Normal: Each image takes 10-30 seconds (LLM analysis + enhancement)
- Large images take longer
- Multiple images process sequentially

## Expected Behavior

1. **Upload**: Image uploads immediately
2. **Analysis**: "Analyzing with AI..." (10-20 seconds)
3. **Enhancement**: "Enhancing image..." (5-10 seconds)
4. **Complete**: Enhanced image appears with download option

## Performance Benchmarks

- Small image (< 1MB): ~15-25 seconds
- Medium image (1-5MB): ~20-35 seconds
- Large image (> 5MB): ~30-60 seconds

*Times include LLM analysis and image processing*

