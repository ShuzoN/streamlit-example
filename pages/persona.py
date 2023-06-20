from conversation import Conversation
import streamlit as st

st.title('ペルソナ決め with GPT')

with st.sidebar:
  openai_api_key = st.text_input('OpenAI API Key')

prompt = '''この文章を読むであろうエンジニアのペルソナを定義しその特性や特徴を書き出してください。またそのペルソナがどのような単語を好みそうかを書いてください。

読者ペルソナ:

職種: Webエンジニア (ここに領域を明記)
経験: x~y年の経験)
興味: エンジニアリング領域に紐づく特有のワード
業務課題: プロジェクト、プロダクト、ビジネスに紐づく課題

読者ペルソナが好みそうな単語:
箇条書きで10個列挙する

'''

with st.form("編集アシスタントに質問する"):
  context_prompt_input = st.text_area(
    label="前提となる知識を細かく書くとより高精度な文字起こしの編集が可能です。",
    placeholder=prompt
    )

  user_message = st.text_area("編集する文章を入れてください")
  submitted = st.form_submit_button("編集する")

if submitted:
  if not openai_api_key.startswith('sk-'):
    st.warning('OpenAI API keyを入力してください', icon='⚠')
  if not context_prompt_input:
    st.warning('前提を教えてください', icon='⚠')
  if submitted and openai_api_key.startswith('sk-'):
    conv = Conversation(context_prompt_input, openai_api_key)
    conv.predict(user_message)

