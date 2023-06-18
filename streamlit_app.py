import streamlit as st
from streamlit_chat import message

from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Does it work?
from langchain.callbacks.streamlit import StreamlitCallbackHandler


# logic

st.title('edit with GPT')

openai_api_key = st.sidebar.text_input('OpenAI API Key')

class Conversation:

  @st.cache_resource
  def __init__(_self, context_prompt):

    system_message_transcription = """
    あなたはライター兼、編集企画者です。日本語で全ての返答を返します。
    以下の文字起こしの文を口語で可読な表現にします。
    その際、発話はまとめず個々人の発話の表現や言い回しは一切変更しないでください。
    また、主語などの省略が起きた場合は補完を提案し保管した部分は()で括って表現してください。
    前提となるコンテキストは以下です。ただし次の文字列`(e\.g\..+)`にマッチするものは全て無視すること。

    {context}

    """.format(context=context_prompt).strip()


    _self.prompt = ChatPromptTemplate.from_messages([
      SystemMessagePromptTemplate.from_template(system_message_transcription),
      MessagesPlaceholder(variable_name="history"),
      HumanMessagePromptTemplate.from_template("{input}")
    ])

    llm = ChatOpenAI(
      streaming=True,
      model='gpt-3.5-turbo-16k',
      callback_manager=AsyncCallbackManager([
        StreamlitCallbackHandler(),
        StreamingStdOutCallbackHandler()
      ]),
      verbose=True,
      temperature=0,
      max_tokens=10240,
      openai_api_key=openai_api_key
    )
    memory = ConversationBufferMemory(return_messages=True)
    _self.conversation = ConversationChain(
      memory=memory,
      prompt=_self.prompt,
      llm=llm
    )


  def load_conversation(_self):
    return _self.conversation

if "generated" not in st.session_state:
    st.session_state.generated = []
if "past" not in st.session_state:
    st.session_state.past = []

st.write("文字起こしを口語の文章に変換することに長けています。")
with st.form("編集アシスタントに質問する"):

  context_prompt_input = st.text_area('''どのような人や前提で話された内容かを教えてください。
  登場人物、その関係性、どのような目的で話しているか以下のフォーマットで書いてください。
  前提となる知識を細かく書くとより高精度な文字起こしの編集が可能です。''')

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
  if not context_prompt_input:
    st.warning('前提を教えてください', icon='⚠')
  if submitted and openai_api_key.startswith('sk-'):
    conv = Conversation(context_prompt_input)
    conversation = conv.load_conversation()
    answer = conversation.predict(input=user_message)