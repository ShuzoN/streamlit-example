import streamlit as st

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

LLM_MODEL = 'gpt-3.5-turbo-16k'
TOKEN_LENGHT = 10240
TEMPERATURE = 0.9

class Conversation:

  @st.cache_resource
  def __init__(_self, context_prompt, openai_api_key):

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
      model=LLM_MODEL,
      callback_manager=AsyncCallbackManager([
        StreamlitCallbackHandler(),
        StreamingStdOutCallbackHandler()
      ]),
      verbose=True,
      temperature=TEMPERATURE,
      max_tokens=TOKEN_LENGHT,
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