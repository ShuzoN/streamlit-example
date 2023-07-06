# .env ファイルをロードして環境変数へ反映
from dotenv import load_dotenv
load_dotenv()

# 環境変数を参照
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def getOPENAI_API_KEY():
    return OPENAI_API_KEY
