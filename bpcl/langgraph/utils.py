from langchain_openai.chat_models import ChatOpenAI
from bpcl import SETTINGS

OPENAI_LLM = ChatOpenAI(model=SETTINGS.OPENAI_MODEL)