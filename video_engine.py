import os
import glob
import PIL.Image
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings

# --- COMPATIBILITY PATCHES ---
# Fix for Pillow 10.0+ (where ANTIALIAS was removed)
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# Auto-configure ImageMagick for Ubuntu
# Ensure you have run: sudo apt install imagemagick
if os.path.exists("/usr/bin/convert"):
    change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def generate_video_from_assets(audio_path, image_paths, text, output_path="final_video.mp4"):
    try:
        # 1. Load the TTS audio
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        audio = AudioFileClip(audio_path)
        
        # 2. Setup images and text splitting
        # Use "|" to separate text for different images (e.g., "Hello|Welcome")
        text_parts = text.split('|')
        
        num_images = len(image_paths)
        if num_images == 0:
            raise ValueError("No images provided for video generation.")
            
        duration_per_image = audio.duration / num_images
        
        final_clips = []
        for i, img in enumerate(image_paths):
            if not os.path.exists(img):
                print(f"Warning: Image {img} not found, skipping.")
                continue
                
            # Create the base image clip with a subtle zoom (Ken Burns effect)
            img_clip = ImageClip(img).set_duration(duration_per_image)
            img_clip = img_clip.resize(lambda t: 1 + 0.04 * (t/duration_per_image)) 
            
            # Get specific text for this image index
            current_text = text_parts[i].strip() if i < len(text_parts) else ""
            
            if current_text:
                # Create the caption for this specific image
                txt_overlay = TextClip(
                    current_text, 
                    fontsize=50, 
                    color='white', 
                    stroke_color='black', 
                    stroke_width=1,
                    method='caption', 
                    size=(img_clip.w * 0.8, None)
                ).set_duration(duration_per_image).set_position(('center', 'bottom'))
                
                # Stack the text on top of the image
                step_clip = CompositeVideoClip([img_clip, txt_overlay])
            else:
                step_clip = img_clip
                
            final_clips.append(step_clip)
        
        if not final_clips:
            raise ValueError("No valid image clips were created.")

        # 3. Concatenate the "Image+Text" chunks into one video
        video = concatenate_videoclips(final_clips, method="compose")
        
        # 4. Attach the full audio
        video = video.set_audio(audio)
        
        # 5. Write the file to disk (libx264 is the standard for CPU encoding)
        video.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True
        )
        
        print(f"✅ Success! Video with segmented captions saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error in video engine: {e}")
        return None

if __name__ == "__main__":
    # --- LOCAL TEST ---
    test_images = sorted(glob.glob("video_images/*.jpg") + glob.glob("video_images/*.jpeg") + glob.glob("video_images/*.png"))
    
    # Path to a test audio file in your project root
    test_audio = "mathebula_cloned_voice.mp3" 
    
    if not test_images:
        print("❌ Error: No images found in 'video_images/' folder.")
    elif not os.path.exists(test_audio):
        print(f"❌ Error: Could not find audio file: {test_audio}")
    else:
        print(f"🚀 Found {len(test_images)} images. Testing segmented captions...")
        # Test string using the pipe separator
        sample_text = "First image caption|Second image caption|Third image caption"
        generate_video_from_assets(
            test_audio, 
            test_images, 
            sample_text, 
            "test_output_segmented.mp4"
        )