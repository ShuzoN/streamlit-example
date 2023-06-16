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
  def __init__(self, context_prompt):

    system_message_transcription = """
    あなたはライター兼、編集企画者です。日本語で全ての返答を返します。
    以下の文字起こしの文を口語で可読な表現にします。
    その際、発話はまとめず個々人の発話の表現や言い回しは一切変更しないでください。
    また、主語などの省略が起きた場合は補完を提案し保管した部分は()で括って表現してください。

    前提となるコンテキストは以下です。

    {context}

    """.format(context=context_prompt).strip()


    self.prompt = ChatPromptTemplate.from_messages([
      SystemMessagePromptTemplate.from_template(system_message_transcription),
      MessagesPlaceholder(variable_name="history"),
      HumanMessagePromptTemplate.from_template("{input}")
    ])

  @st.cache_resource
  def load_conversation(_self):
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
    conversation = ConversationChain(
      memory=memory,
      prompt=_self.prompt,
      llm=llm
    )
    return conversation

if "generated" not in st.session_state:
    st.session_state.generated = []
if "past" not in st.session_state:
    st.session_state.past = []

st.write("文字起こしを口語の文章に変換することに長けています。")
with st.form("編集アシスタントに質問する"):

  context_prompt_input = st.text_area("どのような人や前提で話された内容かを教えてください。登場人物、その関係性、どのような目的で話しているか、前提となる知識は何かを書くとより高精度な文字起こしの編集が可能です。")
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