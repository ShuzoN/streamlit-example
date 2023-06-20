from ChatPrompt import ChatPrompt
import streamlit as st
import re
import math

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationChain
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Does it work?
from langchain.callbacks.streamlit import StreamlitCallbackHandler

LLM_MODEL = 'gpt-3.5-turbo-16k'
TOKEN_LENGHT = 10240
TRANSCRIPTION_TEMPERATURE = 0.0
MEMORY_TEMPERATURE = 0.3
CHUNK_SIZE=4000


class Conversation:

  @st.cache_resource
  def __init__(_self, context_prompt, openai_api_key, transcription_temperature=TRANSCRIPTION_TEMPERATURE, memory_temperature=MEMORY_TEMPERATURE):

    system_message_transcription = """
    あなたはライター兼、編集企画者です。日本語で全ての返答を返します。
    以下の文字起こしの文を口語で可読な表現にします。
    その際、発話はまとめず個々人の発話の表現や言い回しは一切変更しないでください。
    また、主語などの省略が起きた場合は補完を提案し保管した部分は()で括って表現してください。
    前提となるコンテキストは以下です。ただし次の文字列`(e\.g\..+)`にマッチするものは全て無視すること。

    {context}

    """.format(context=context_prompt).strip()

    chatPrompt = ChatPrompt(system_message_transcription)
    _self.prompt = chatPrompt.getPromptTemplate()

    # 文字起こしのmodel
    llm = ChatOpenAI(
      streaming=True,
      model=LLM_MODEL,
      callback_manager=AsyncCallbackManager([
        StreamlitCallbackHandler(),
        StreamingStdOutCallbackHandler()
      ]),
      verbose=True,
      temperature=transcription_temperature,
      max_tokens=TOKEN_LENGHT,
      openai_api_key=openai_api_key
    )

    # memory用に要約するmodel
    memory = ConversationSummaryMemory(
       llm=ChatOpenAI(
        model=LLM_MODEL,
        temperature=memory_temperature,
        openai_api_key=openai_api_key),
        return_messages=True)

    _self.conversation = ConversationChain(
      memory=memory,
      prompt=_self.prompt,
      llm=llm
    )

  def predict(_self, user_message, chunk_size=CHUNK_SIZE):
    sentences = re.split("。|\n", user_message)

    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + "。"
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + "。"

    if current_chunk:
        chunks.append(current_chunk)

    for chunk in chunks:
        _self.conversation.predict(input=chunk.strip())