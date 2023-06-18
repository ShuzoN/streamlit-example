import streamlit as st

st.title('ペルソナ決め with GPT')

with st.sidebar:
  openai_api_key = st.text_input('OpenAI API Key')



st.write("文字起こしを口語の文章に変換することに長けています。")