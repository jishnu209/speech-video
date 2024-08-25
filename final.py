import os
import requests
from gtts import gTTS
from moviepy.editor import *
import speech_recognition as sr

# Function to generate speech from text
def text_to_speech(text, lang='en', index=0):
    tts = gTTS(text=text, lang=lang)
    audio_file = f"audio_{index}.mp3"
    tts.save(audio_file)
    return audio_file

# Function to fetch images based on text using Unsplash API
def fetch_image_based_on_text(text):
    access_key = 'Bs8CDRR69SRlMaUdRQ1Q0JyOq5RAnnd5oMpA38B_uVI'  # Replace with your Unsplash access key
    url = f'https://api.unsplash.com/photos/random?query={text}&client_id={access_key}&count=1'
    
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200 and data:
        # Get the image URL from the API response
        image_url = data[0]['urls']['regular']
        return image_url
    else:
        return None  # Handle case where no image is found

# Function to recognize speech from the microphone
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please speak your text...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

# Function to create video from segments using dynamically fetched images
def create_video_from_segments(segments):
    clips = []
    audio_files = []

    for i, text in enumerate(segments):
        # Generate speech for the text
        audio_file = text_to_speech(text, index=i)
        audio_files.append(audio_file)

        # Fetch an image based on the text
        image_url = fetch_image_based_on_text(text)
        if image_url:
            # Download the image to use in the video
            image_file = f"image_{i}.jpg"
            img_data = requests.get(image_url).content
            with open(image_file, 'wb') as handler:
                handler.write(img_data)

            # Load the image and audio for the video segment
            image_clip = ImageClip(image_file).set_duration(5)  # 5 seconds duration
            audio_clip = AudioFileClip(audio_file)

            # Set the audio for the image clip
            video_segment = image_clip.set_audio(audio_clip)
            clips.append(video_segment)

            # Clean up image file after use
            os.remove(image_file)
        else:
            print(f"No image found for: {text}")

    # Concatenate all clips to create the final video
    final_video = concatenate_videoclips(clips, method="compose")

    # Write the final video file
    final_video_file = "output_video.mp4"
    final_video.write_videofile(final_video_file, fps=24)

    # Clean up temporary audio files
    for audio_file in audio_files:
        os.remove(audio_file)

# Main function
if __name__ == "__main__":
    # Capture speech from the user
    segments = []
    for _ in range(3):  # Capture 3 segments of speech
        text = recognize_speech()
        if text:
            segments.append(text)

    create_video_from_segments(segments)
