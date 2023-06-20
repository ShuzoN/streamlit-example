from ChatPrompt import ChatPrompt
import streamlit as st
from conversation import MEMORY_TEMPERATURE, TRANSCRIPTION_TEMPERATURE, Conversation

st.title('文字起こし編集 with GPT')

system_static_prompt = """あなたはライター兼、編集企画者です。日本語で全ての返答を返します。
    以下の文字起こしの文を口語で可読な表現にします。
    その際、発話はまとめず個々人の発話の表現や言い回しは一切変更しないでください。
    また、主語などの省略が起きた場合は補完を提案し保管した部分は()で括って表現してください。
    前提となるコンテキストは以下です。ただし次の文字列`(e\.g\..+)`にマッチするものは全て無視すること。
"""

with st.sidebar:
  openai_api_key = st.text_input('OpenAI API Key')
  transcription_temperature= st.slider('文字起こしのtemperature', 0.0, 2.0, TRANSCRIPTION_TEMPERATURE,step=0.1)
  memory_temperature = st.slider('記憶のtemperature', 0.0, 2.0, MEMORY_TEMPERATURE,step=0.1)
  if st.button('上手く行かなくなったら押すボタン'):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.experimental_rerun()

if "generated" not in st.session_state:
    st.session_state.generated = []
if "past" not in st.session_state:
    st.session_state.past = []

st.write("文字起こしを口語の文章に変換することに長けています。")
with st.form("編集アシスタントに質問する"):
  system_adaptive_prompt = st.text_area(label="前提となる知識を細かく書くとより高精度な文字起こしの編集が可能です。")

  with st.expander("前提のテンプレートはこちら"):
    codeblock = '''
トピック: 〇〇に関する〇〇について
  * (e.g. インターンシップSunrise2023の魅力について)
登場人物: 
  * 〇〇である"〇〇"
    * (e.g. インターンシップの講師であるともかつ)
  * 〇〇である"〇〇"
    * (e.g. 記事の編集者かつインタビュアーであるしゅーぞー)
目的:
  * この会話の目的は〇〇(what)を〇〇(who)に〇〇のように(how)訴求する記事を書くためです。
  * (e.g. このインタビューの目的はインターンシップをエンジニア学生のエントリー訴求する記事を書くためです。)
発話の特徴をどのように識別するか:
  * この会話は◯人の話者が話しています
  * (e.g. 2人)
  * 語尾や問答の内容から、どの発言が個々人のものか推論します。
  * 疑問形や話の整理、記事の書き方や狙いについては〇〇、〇〇の狙いや詳細に関する回答は〇〇が答えているケースが多いです。
    * (e.g.前からしゅーぞー、インターン、ともかつ)
発話のフォーマット: 
  * 発話には下のように発話者を明記してください。その発話に紐づいた人の名前を選びます。
```
〇〇(e.g.しゅーぞー): 
```
  * また発話者ごとに必ず改行を2つ入れ、markdownで記述してください。
'''
    st.code(codeblock)
  user_message = st.text_area("編集する文章を入れてください")
  submitted = st.form_submit_button("編集する")

if submitted:
  if not openai_api_key.startswith('sk-'):
    st.warning('OpenAI API keyを入力してください', icon='⚠')
  if not system_adaptive_prompt:
    st.warning('前提を教えてください', icon='⚠')
  if submitted and openai_api_key.startswith('sk-'):

    chatPrompt = ChatPrompt(system_static_prompt, system_adaptive_prompt)
    conv = Conversation(chatPrompt, openai_api_key)

    conv.predict(user_message)
