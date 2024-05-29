import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import streamlit as st

def get_sentiment_emotion(prompt, emotions):
    system_role = f'''
    You are an emotionally intelligent assistant. 
    classify the sentiment of the user's text with ONLY ONE  of the following emotions
    {emotions} After classifying the text respond with the emotion only.
    '''
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,
        temperature=0,
    )
    response = response.choices[0].message.content
    return response

if __name__ == '__main__':
    load_dotenv(find_dotenv(), override=True)
    apiKey = os.environ.get('OPENAI_API_KEY')
    client = OpenAI(api_key=apiKey)

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.title("Zero-Shot Sentiment Analysis")

    with col2:
        st.image("ai.png",width=70)

    with st.form(key="my_form"):
        default_emotions = 'Positive', 'Negative', 'Neutral'
        emotions_list = st.text_input("Emotions:", value=default_emotions)
        user_text = st.text_area("Text To Classify")
        submit_button = st.form_submit_button("Check")
        if submit_button:
            response = get_sentiment_emotion(user_text,emotions_list)
            result = f'{user_text} ===> {response}\n'
            st.write(result)
            if 'History' not in st.session_state:
                if result:
                    st.session_state["History"] = result
                else:
                    st.session_state["History"] = ''
            else:
                st.session_state["History"] += result

            st.text_area("History", value=st.session_state["History"],height=400)

