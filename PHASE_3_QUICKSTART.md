# Phase 3 Quick Start Guide

## 🚀 Quick Start

### Install Phase 3 Dependencies

```bash
pip install -r requirements.txt
```

New dependencies:
- `Pillow==10.2.0` - Image processing
- `google-cloud-vision==3.7.0` - Vision API (optional)

---

## 🎨 Generate Images

### Basic Image Generation

```python
from src.agents.image_generator_agent import ImageGeneratorAgent

agent = ImageGeneratorAgent()

# Generate a single image
result = agent.execute(
    project_id="my_project",
    prompts="Modern office workspace, professional lighting, minimalist design",
    number_of_images=1,
    aspect_ratio="16:9"
)

# Access generated images
for img_data in result['images']:
    image = img_data['image']  # PIL Image object
    # Use image as needed
```

### Generate Multiple Images

```python
# Generate multiple variations
result = agent.execute(
    project_id="my_project",
    prompts=[
        "Hero image: technology and innovation",
        "Supporting visual: team collaboration",
        "Thumbnail: colorful abstract pattern"
    ],
    number_of_images=2,  # 2 per prompt = 6 total
    aspect_ratio="1:1"
)
```

### AI-Enhanced Prompts

```python
# Let AI improve your prompt
basic = "person at computer"
enhanced = agent.enhance_prompt(basic, content_type="blog")
# Enhanced will be much more detailed and specific
```

### Content-Aware Suggestions

```python
# Get image suggestions from your content
suggestions = agent.suggest_images_for_content(
    content="Your blog post content here...",
    title="10 Productivity Tips",
    num_suggestions=3
)
# Returns list of prompts tailored to your content
```

---

## 🎥 Create Video Scripts

### Basic Video Script

```python
from src.agents.video_creator_agent import VideoCreatorAgent

agent = VideoCreatorAgent()

# Create video script
result = agent.execute(
    project_id="my_project",
    topic="Introduction to Python",
    duration=120,  # 2 minutes
    video_type="tutorial",
    target_platform="youtube"
)

# Access script
script = result['script']
print(script['title'])
for scene in script['scenes']:
    print(f"Scene {scene['scene_number']}: {scene['script']}")
```

### Generate Video Metadata

```python
# SEO-optimized metadata for YouTube
metadata = agent.generate_video_metadata(
    script=script,
    platform="youtube"
)

print(metadata['optimized_title'])
print(metadata['description'])
print(metadata['tags'])
```

### Create Storyboard

```python
# Generate image prompts for storyboard frames
storyboard_prompts = agent.create_storyboard_description(
    scenes=script['scenes']
)

# Use these prompts with ImageGeneratorAgent
image_agent = ImageGeneratorAgent()
for prompt in storyboard_prompts:
    result = image_agent.execute(
        project_id="my_project",
        prompts=[prompt],
        aspect_ratio="16:9"
    )
```

---

## 🎙️ Create Audio/Podcast Scripts

### Basic Podcast Script

```python
from src.agents.audio_creator_agent import AudioCreatorAgent

agent = AudioCreatorAgent()

# Create podcast episode
result = agent.execute(
    project_id="my_project",
    topic="The Future of AI",
    duration=15,  # 15 minutes
    audio_type="podcast",
    num_speakers=2,
    tone="conversational"
)

# Access script
script = result['script']
for segment in script['segments']:
    print(f"{segment['title']}")
    for line in segment['content']:
        print(f"  {line['speaker']}: {line['text']}")
```

### Single Speaker Narration

```python
# Convert text to narration script
narration = agent.create_narration_from_text(
    text="Your article content...",
    tone="professional",
    max_duration_minutes=10
)

print(f"Word count: {narration['narration_word_count']}")
print(f"Duration: {narration['estimated_duration_minutes']:.1f} min")
```

### Get Production Elements

```python
# Generate with music cues and sound effects
result = agent.execute(
    project_id="my_project",
    topic="Meditation Guide",
    duration=20,
    audio_type="meditation",
    include_music_cues=True,
    include_sound_effects=True
)

# Access production elements
music_cues = result['music_cues']
voice_config = result['voice_configuration']
```

---

## 🖼️ Process and Optimize Media

### Basic Image Optimization

```python
from src.infrastructure.media_processor import MediaProcessor
from PIL import Image

processor = MediaProcessor()

# Load image
image = Image.open("original.jpg")

# Optimize
optimized = processor.optimize_image(
    image=image,
    quality=85,
    max_width=1920,
    max_file_size_kb=500
)

optimized.save("optimized.jpg")
```

### Create Responsive Images

```python
# Generate multiple sizes for responsive design
responsive = processor.create_responsive_set(image)

# Default sizes: mobile (320), tablet (768), desktop (1024), large (1920)
responsive['mobile'].save("image_mobile.jpg")
responsive['tablet'].save("image_tablet.jpg")
responsive['desktop'].save("image_desktop.jpg")
responsive['large'].save("image_large.jpg")
```

### Create Thumbnails

```python
# Create thumbnail
thumbnail = processor.create_thumbnail(
    image=image,
    size=(300, 300),
    crop_to_fit=True  # Crop to exact size, or False to fit
)

thumbnail.save("thumbnail.jpg")
```

### Enhance Images

```python
# Adjust image properties
enhanced = processor.enhance_image(
    image=image,
    brightness=1.1,    # 10% brighter
    contrast=1.2,      # 20% more contrast
    sharpness=1.3,     # 30% sharper
    saturation=0.9     # 10% less saturated
)
```

---

## ☁️ Store Media in Cloud

### Upload Images

```python
from src.infrastructure.storage_manager import CloudStorageManager

storage = CloudStorageManager()

# Upload PIL Image
result = storage.upload_image(
    image=pil_image,
    project_id="my_project",
    filename="hero_image.jpg",
    optimize=True,
    quality=85
)

print(f"Public URL: {result['public_url']}")
print(f"Signed URL: {result['signed_url']}")
```

### Upload Any File

```python
# Upload from file object
with open("video_script.json", "rb") as f:
    result = storage.upload_file(
        file_obj=f,
        blob_path="projects/my_project/scripts/video.json",
        content_type="application/json"
    )

# Upload from local path
result = storage.upload_from_local(
    local_path="./audio_script.txt",
    project_id="my_project"
)
```

### Manage Files

```python
# List files
files = storage.list_files(project_id="my_project")
for file in files:
    print(f"{file['name']} - {file['size_bytes']} bytes")

# Download file
content = storage.download_file(
    blob_path="projects/my_project/images/hero.jpg",
    local_path="./downloaded.jpg"  # Optional
)

# Delete file
storage.delete_file("projects/my_project/old_image.jpg")

# Get storage stats
stats = storage.get_storage_stats(project_id="my_project")
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size_mb']} MB")
```

---

## 🔗 Complete Workflow Example

### Generate Blog Post with Media

```python
from src.agents.content_agent import ContentGeneratorAgent
from src.agents.image_generator_agent import ImageGeneratorAgent
from src.infrastructure.media_processor import MediaProcessor
from src.infrastructure.storage_manager import CloudStorageManager

# 1. Generate content
content_agent = ContentGeneratorAgent()
content = content_agent.execute(
    project_id="blog_001",
    topic="10 Tips for Remote Work",
    research_findings=research_data
)

# 2. Generate hero image
image_agent = ImageGeneratorAgent()
prompts = image_agent.suggest_images_for_content(
    content=content['body'],
    title=content['title']
)

image_result = image_agent.execute(
    project_id="blog_001",
    prompts=[prompts[0]],
    aspect_ratio="16:9"
)

# 3. Process image
processor = MediaProcessor()
image = image_result['images'][0]['image']
optimized = processor.optimize_image(image, quality=85)
responsive = processor.create_responsive_set(optimized)

# 4. Upload to cloud
storage = CloudStorageManager()
urls = {}
for size_name, img in responsive.items():
    result = storage.upload_image(
        image=img,
        project_id="blog_001",
        filename=f"hero_{size_name}.jpg"
    )
    urls[size_name] = result['public_url']

# 5. You now have:
# - content['title'] and content['body']
# - urls with all image sizes
# Ready to publish!
```

---

## 🧪 Testing

### Run All Phase 3 Tests

```bash
python examples/test_phase3.py
```

### Run Complete Example

```bash
python examples/generate_with_media.py
```

---

## 💰 Cost Estimates

| Operation | Cost | Notes |
|-----------|------|-------|
| Generate 1 image | ~$0.02 | Imagen 3.0 |
| Generate video script | ~$0.001 | Gemini Pro |
| Generate audio script | ~$0.001 | Gemini Pro |
| Storage (per GB/month) | $0.023 | Standard class |
| **Total per content piece** | **~$0.05** | With 2-3 images |

---

## 🎯 Next Steps

1. **Try the examples** - Run `test_phase3.py`
2. **Generate content** - Use `generate_with_media.py`
3. **Customize** - Adjust prompts and configs for your needs
4. **Integrate** - Add to your existing workflow
5. **Deploy** - Set up Cloud Storage bucket

---

## 🆘 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Vertex AI authentication errors
```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### Image generation fails
- Ensure Vertex AI Imagen is enabled in your project
- Check region availability (use us-central1)

### Storage errors
- Verify Cloud Storage API is enabled
- Check IAM permissions for storage.buckets.create

---

## 📚 More Information

- [Complete Phase 3 Documentation](./PHASE_3_COMPLETE.md)
- [Architecture Guide](./ARCHITECTURE.md)
- [Main README](./README.md)

---

*Happy Creating! 🎨🎥🎙️*
