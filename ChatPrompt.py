from typing import Optional
import streamlit as st
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

class ChatPrompt:
    def __init__(self, systemStaticPrompt):
        self.systemStaticPrompt = systemStaticPrompt
        self.prompt = ChatPromptTemplate.from_messages([
          SystemMessagePromptTemplate.from_template(systemStaticPrompt),
          MessagesPlaceholder(variable_name="history"),
          HumanMessagePromptTemplate.from_template("{input}")
        ])

    def getPromptTemplate(self) -> Optional[ChatPromptTemplate]:
        return self.prompt
