import streamlit as st
import os
import moviepy.editor as mp
from moviepy.video.fx.mirror_x import mirror_x
from moviepy.video.fx.freeze import freeze
import google.generativeai as genai
import edge_tts
import asyncio

# API Keys Configuration
GEMINI_API_KEY = "AQ.Ab8RN6IKAuYEDcyVSudnyOpMuiMXQNG75mF0NPaS2ZYZrA3JPA"
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Wildlife Movie Recap AI", layout="centered")
st.title("🐾 Wildlife Movie Recap Generator")
st.write("ဖုန်းဖြင့် အလွယ်တကူ ဗီဒီယိုဖန်တီးနိုင်သော Web App")

# 1. Video Upload File Uploader
uploaded_file = st.file_uploader("Wildlife ဗီဒီယိုကို Upload တင်ပါ", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    st.success("ဗီဒီယို Upload အောင်မြင်ပါသည်။")

    if st.button("Recap ဗီဒီယို စတင်ဖန်တီးမည်"):
        st.info("🔄 အဆင့် ၂: Original Script ထုတ်ယူပြီး Cinematic မြန်မာစာသား ပြောင်းလဲနေပါသည်...")
        
        original_text_sample = "A hungry leopard stalks its prey in the African savanna, waiting for the perfect moment to strike."
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction=(
                "You are a professional Wildlife Movie Recap Content Creator. "
                "Translate the original script to Burmese. "
                "Style: Cinematic Wildlife Storytelling + Predator vs Prey Survival Story + Engaging Narrative. "
                "Do NOT include timestamps, introduction, or outro. Deliver the script as a single cohesive story paragraph. "
                "မြန်မာဘာသာစကားကို နားထောင်ရ ကြည့်ရှုရ စိတ်လှုပ်ရှားစရာကောင်းအောင် သဘာဝကျကျနှင့် ပီပြင်စွာ ရေးပေးပါ။"
            )
        )
        
        response = model.generate_content(f"Translate and rewrite this: {original_text_sample}")
        burmese_script = response.text
        
        st.subheader("📝 ဖန်တီးထားသော မြန်မာ Script:")
        st.write(burmese_script)

        st.info("🎙️ အဆင့် ၃: မြန်မာ Voiceover အသံသွင်းနေပါသည်...")
        
        async def generate_voice():
            communicate = edge_tts.Communicate(burmese_script, "my-MM-ThihaNeural", rate="+0%")
            await communicate.save("voiceover.mp3")
            
        asyncio.run(generate_voice())
        st.success("Voiceover အသံသွင်းယူမှု အောင်မြင်ပါသည်။")

        st.info("🎬 အဆင့် ၄၊ ၅၊ ၆: ဗီဒီယိုအား Copyright လွတ်အောင် ပြုပြင်ပြီး အသံညှိနေပါသည်...")
        
        try:
            video = mp.VideoFileClip("input_video.mp4")
            flipped_video = mirror_x(video)
            
            video_duration = flipped_video.duration
            edited_clips = []
            current_time = 0
            
            while current_time < video_duration:
                end_time = min(current_time + 5, video_duration)
                clip = flipped_video.subclip(current_time, end_time)
                frozen_clip = freeze(clip, t='end', freeze_duration=0.5)
                edited_clips.append(frozen_clip)
                current_time += 5
                
            final_visual_video = mp.concatenate_videoclips(edited_clips)
            audio_background = mp.AudioFileClip("voiceover.mp3")
            
            final_video = final_visual_video.set_audio(audio_background)
            final_video = final_video.set_duration(audio_background.duration)
            
            final_video.write_videofile("output_final.mp4", codec="libx264", audio_codec="aac", fps=24)
            st.success("ဗီဒီယို တည်းဖြတ်မှု အားလုံး ပြီးမြောက်ပါပြီ။")
            
            with open("output_final.mp4", "rb") as file:
                st.download_button(
                    label="📥 ဗီဒီယို (MP4) ကို ဒေါင်းလုဒ်ဆွဲရန် နှိပ်ပါ",
                    data=file,
                    file_name="wildlife_recap_final.mp4",
                    mime="video/mp4"
                )
                
        except Exception as e:
            st.error(f"ဗီဒီယိုတည်းဖြတ်ရာတွင် အမှားအယွင်းရှိခဲ့ပါသည်: {str(e)}")
