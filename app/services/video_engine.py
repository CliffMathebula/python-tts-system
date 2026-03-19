import os
import PIL.Image

# --- PILLOW COMPATIBILITY PATCH ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = getattr(PIL.Image, 'LANCZOS', PIL.Image.BICUBIC)

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings

# Configure ImageMagick for Ubuntu
if os.path.exists("/usr/bin/convert"):
    change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def generate_video(audio_path, image_paths, text, output_path, width=1920, height=1080):
    """
    Generates a full-screen video and automatically deletes source audio/images 
    after processing to save disk space.
    """
    try:
        # 1. Load Audio and Calculate Timings
        audio = AudioFileClip(audio_path)
        text_parts = text.split('|')
        duration_per_image = audio.duration / len(image_paths)
        
        final_clips = []
        for i, img in enumerate(image_paths):
            # 2. Load and Scale Image (Object-Fit: Cover)
            img_clip = ImageClip(img).set_duration(duration_per_image)
            
            img_ratio = img_clip.w / img_clip.h
            screen_ratio = width / height

            if img_ratio > screen_ratio:
                img_clip = img_clip.resize(height=height)
            else:
                img_clip = img_clip.resize(width=width)

            # Center and Crop to requested dimensions
            img_clip = img_clip.set_position('center').crop(
                x_center=img_clip.w/2, 
                y_center=img_clip.h/2, 
                width=width, 
                height=height
            )

            # 3. Add Subtitles
            current_text = text_parts[i].strip() if i < len(text_parts) else ""
            if current_text:
                dynamic_font_size = max(24, int(height * 0.05))
                txt_overlay = TextClip(
                    current_text, 
                    fontsize=dynamic_font_size, 
                    color='white', 
                    stroke_color='black',
                    stroke_width=2,
                    method='caption', 
                    size=(width * 0.9, None)
                ).set_duration(duration_per_image).set_position(('center', height * 0.8))
                
                step_clip = CompositeVideoClip([img_clip, txt_overlay], size=(width, height))
            else:
                step_clip = CompositeVideoClip([img_clip], size=(width, height))
                
            final_clips.append(step_clip)

        # 4. Final Assembly and Export
        video = concatenate_videoclips(final_clips, method="compose").set_audio(audio)
        video.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            threads=4
        )
        print(f"✅ Video successfully rendered: {output_path}")

    except Exception as e:
        print(f"❌ Video Engine Error: {e}")
        raise e

    finally:
        # --- AUTOMATIC CLEANUP ---
        print("🧹 Starting cleanup of temporary source files...")
        
        # Delete Audio Source
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                print(f"🗑️ Deleted: {os.path.basename(audio_path)}")
            except Exception as cleanup_err:
                print(f"⚠️ Could not delete audio: {cleanup_err}")

        # Delete Image Sources
        for img_p in image_paths:
            if os.path.exists(img_p):
                try:
                    os.remove(img_p)
                    print(f"🗑️ Deleted: {os.path.basename(img_p)}")
                except Exception as cleanup_err:
                    print(f"⚠️ Could not delete image {img_p}: {cleanup_err}")
        
        print("✨ Environment sanitized.")