import streamlit as st
import os
import re
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from pytube import YouTube


def rename_audio_file_name(base_name):
    # Rename extension to MP3
    file_name = os.path.basename(base_name)
    file_name = file_name.split('.')[0]
    file_name = f'{file_name}.mp3'
    file_name = re.sub('\s+', '-', file_name)
    return file_name


def transcribe(audio_file_to_transcribe,video_not_english):
    if not os.path.exists(audio_file_to_transcribe):
        st.session_state["processing_status"] += "Audio file is not found  \n"
        return False
    st.session_state["processing_status"] += "Starting transcribe audio file... \n"
    with open(audio_file_to_transcribe, 'rb') as f:
        if video_not_english:
            response = client.audio.translations.create(model='whisper-1', file=f)
        else:
            response = client.audio.transcriptions.create(model='whisper-1', file=f)

        name, extension = os.path.splitext(audio_file_to_transcribe)
        transcript_file_name = f'{name}.txt'
        with open(transcript_file_name, 'w') as f:
            f.write(response.text)
            st.session_state["processing_status"] += "Done transcription \n"
    return transcript_file_name


def summarizer(file_to_summarize):
    if not os.path.exists(file_to_summarize):
        st.session_state["processing_status"] += "No file to summarize \n"

    with open(file_to_summarize) as f:
        text = f.read()
        system_role = "You are a professional technical writer"
        prompt = f'''
        summarize the text deleimeted by three backticks. 
        ```{text}```
        Add a title for the summary
        the summary should be informative and factual, covering the most important aspects of the topic.
        Start your summary with an introduction paragraph that gives an overview of the topic, then followed by
        Bullet points if possible.Add a conclusion phrase at the end of the summary
        '''
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ],
            temperature=1,
            max_tokens=2048
        )
        return response.choices[0].message.content


if __name__ == "__main__":
    load_dotenv(find_dotenv(), override=True)
    apiKey = os.environ.get('OPENAI_API_KEY')
    client = OpenAI(api_key=apiKey)

st.title("Welcome to YouTube Summarizer")
video_info_col, status_col = st.columns(2)
with video_info_col:
    video_url = st.text_input("Url")
    video_not_english = st.toggle("Not English")
    if video_url:
        if "processing_status" not in st.session_state:
            st.session_state["processing_status"] = 'Fetching video info...'
            st.experimental_rerun()
        video = YouTube(video_url)
        with st.expander("Video Information"):
            st.write(f'Video Title: {video.title}')
            st.write(f'Author: {video.author}')
            st.write(f'Length: {video.length}')
            st.write(f'Views: {video.views}')
            st.image(video.thumbnail_url)
            st.write(video.streams)
        st.session_state["processing_status"] += "Starting download audio file.... \n"
        audio_stream = video.streams.filter(only_audio=True).first()
        audio_file = audio_stream.download()
        st.session_state["processing_status"] += "Download audio file Done :+1: \n"
        st.session_state["processing_status"] += "Renaming audio file name.... \n"
        update_file_name = rename_audio_file_name(audio_file)
        os.rename(audio_file, update_file_name)
        st.session_state["processing_status"] += "Rename audio file name Done :100: \n"
        transcript_file_name = transcribe(update_file_name, video_not_english)
        summary = summarizer(transcript_file_name)
        st.session_state["summary"] = summary


with status_col:
    st.text_area("Video Processing Status:", key="processing_status")
    st.text_area("Summary", key="summary", height=500)
