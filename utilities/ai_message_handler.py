import os
import json
from groq import Groq

class AIMessageHandler:
    """ Handles LLM interactions and response processing """
    def __init__(self, llm_model_id):
        self.llm_model_id = llm_model_id
        self.llm_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def query_llm(self, query, prompt=None):
        """ Send a query to the LLM and return its response (blocking) """
        user_query = query
        if prompt:
            user_query = f"{prompt} \n {query}"
        print(f"[Message Handler] Querying LLM with: {user_query}")
        chat_completion = self.llm_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_query},
                    ],
                },
            ],
            model=self.llm_model_id,
        )
        return chat_completion.choices[0].message.content

    def parse_response(self, response):
            """ Parses agent response into structured tasks """
            try:
                print("Received: ", response)
                #return json.loads(response)
                return {"Message": {"message_1": response}}

            except json.JSONDecodeError:
                return {"Message": {"message_1": "Sorry, I didn't understand that."}}