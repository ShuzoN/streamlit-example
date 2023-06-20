from typing import Optional
import streamlit as st
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

class ChatPrompt:
    @st.cache_resource
    def __init__(_self, system_static, system_adaptive):
        system_prompt = """
        {static}

        {adaptive}
        """.format(static=system_static, adaptive=system_adaptive).strip()

        _self.prompt = ChatPromptTemplate.from_messages([
          SystemMessagePromptTemplate.from_template(system_prompt),
          MessagesPlaceholder(variable_name="history"),
          HumanMessagePromptTemplate.from_template("{input}")
        ])

    def getPromptTemplate(_self) -> Optional[ChatPromptTemplate]:
        return _self.prompt
