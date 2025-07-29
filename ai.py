from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()


class AIModel:
    def __init__(self):   
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

    def create_rrule(self,user_msg):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction=os.getenv('SYSTEM_PROMPT')),contents=user_msg)
        return(response.text)
    
llm = AIModel()

