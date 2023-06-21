from ChatPrompt import ChatPrompt
from conversation import Conversation
import streamlit as st

st.title('ペルソナ決め with GPT')

with st.sidebar:
  openai_api_key = st.text_input('OpenAI API Key')
  if st.button('上手く行かなくなったら押すボタン'):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.experimental_rerun()

system_static_prompt = '''この文章を読むであろうエンジニアのペルソナを定義しその特性や特徴を書き出してください。またそのペルソナがどのような単語を好みそうかを書いてください。
また、読者ペルソナを定義した後、そのペルソナを定義した理由があれば教えてください。もし、本文の意図や主張とそぐわない場合はそぐわない理由を教えてください。
その理由を列挙した後、再度読者ペルソナを定義してください。また、そのペルソナが好みそうな単語を箇条書きで10個列挙してください。

ペルソナ定義に最低限、必要な項目は以下です。
'''

with st.form("編集アシスタントに質問する"):
  system_adaptive_prompt = st.text_area(
    label="ペルソナに設定する項目を教えてください。",
    )

  with st.expander("ペルソナのテンプレートはこちら"):
    codeblock = '''読者ペルソナ:

職種: Webエンジニア (ここに領域を明記)
経験: x~y年の経験(x, yにはそれぞれ数字が入る)
興味: エンジニアリング領域に紐づく特有のワード
業務課題: プロジェクト、プロダクト、ビジネスに紐づく課題
'''
    st.code(codeblock)

  user_message = st.text_area("対象の文章を入れてください")
  submitted = st.form_submit_button("ペルソナを考える")

@st.cache_resource
def getConv(system_static_prompt, system_adaptive_prompt, openai_api_key):
    chatPrompt = ChatPrompt(system_static_prompt, system_adaptive_prompt)
    return Conversation(chatPrompt, openai_api_key)

if submitted:
  if not openai_api_key.startswith('sk-'):
    st.warning('OpenAI API keyを入力してください', icon='⚠')
  if not system_adaptive_prompt:
    st.warning('前提を教えてください', icon='⚠')
  if submitted and openai_api_key.startswith('sk-'):
    conv = getConv(system_static_prompt, system_adaptive_prompt, openai_api_key)
    conv.predict(user_message)