from chat_prompt import ChatPrompt
from conversation import TRANSCRIPTION_TEMPERATURE, Conversation
import streamlit as st

st.title('タイトル決め with GPT')

with st.sidebar:
  openai_api_key = st.text_input('OpenAI API Key')
  temperature= st.slider('temperature', 0.0, 2.0, TRANSCRIPTION_TEMPERATURE,step=0.1)
  if st.button('上手く行かなくなったら押すボタン'):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.experimental_rerun()

system_static_prompt = '''

これから入力するタイトル案を以下の6指標で10段階(1-10点)で評価します。 

「得すること」
「新しいこと」
「好奇心をくすぐること」
「簡単で楽にできそうなこと」
「ポジティブであること」
「信頼性があること」

markdownのtableで以下のフォーマットを利用しタイトルと評価をまとめます。

タイトル | 得する|新しい| 好奇心|楽|ポジティブ|信頼性
-|-|-|-|-|-|-
hoge | 1-10 | 1-10 | 1-10 | 1-10 | 1-10 | 1-10


最初に1つタイトル案を提示するため、まずはそれを評価します。
原案の評価を元に、ペルソナが興味を持つであろう仮タイトルを元のタイトル案のニュアンスを残したまま10個出してください。それぞれを6指標で10段階で評価します。同様のフォーマットを利用してください。
その後、最もスコアの良い2つの案を選択してください。
その2つを元に各スコアを改善するタイトル案を元のタイトル案のニュアンスを残したまま10個考え、それぞれを同じ指標、フォーマットで評価してください。

'''


system_adaptive_prompt = '''
'''

with st.form("編集アシスタントに質問する"):
  title_draft = st.text_area(
    label="タイトルの原案を教えてください",
    )

  persona = st.text_area(
    label="ペルソナを教えてください",
    )

  text = st.text_area("対象の文章を入れてください")
  submitted = st.form_submit_button("タイトルを考える")

@st.cache_resource
def getConv(system_static_prompt, system_adaptive_prompt, openai_api_key):
    chatPrompt = ChatPrompt(system_static_prompt, system_adaptive_prompt)
    return Conversation(chatPrompt, openai_api_key, temperature)

if submitted:
  if not openai_api_key.startswith('sk-'):
    st.warning('OpenAI API keyを入力してください', icon='⚠')
  if not system_adaptive_prompt:
    st.warning('前提を教えてください', icon='⚠')
  if submitted and openai_api_key.startswith('sk-'):
    conv = getConv(system_static_prompt, system_adaptive_prompt, openai_api_key)
    user_message = f"""
    タイトル原案は以下です
    {title_draft}
    
    ペルソナは以下です

    {persona}

    本文は以下です

    {text}
    """

    conv.predict(user_message)