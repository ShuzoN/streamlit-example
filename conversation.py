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
  def __init__(_self, _chatPrompt, openai_api_key, transcription_temperature=TRANSCRIPTION_TEMPERATURE, memory_temperature=MEMORY_TEMPERATURE):

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
      prompt=_chatPrompt.getPromptTemplate(),
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