import os
import json
from dotenv import load_dotenv  # Load environment variables from .env file
from langchain_groq import ChatGroq  # Official Langchain integration for Groq
from langchain_core.prompts import ChatPromptTemplate  # For custom prompts
from langgraph.checkpoint.memory import MemorySaver  # Long-term memory
from langgraph.prebuilt import create_react_agent  # Creates a fully functional AI agent

# Load environment variables from .env
load_dotenv()

# Ensure the Groq API Key is set
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is not set. Please add it to your environment.")

class AIMessageHandler:
    """Handles AI interactions with Groq's LLM and maintains message memory using Langchain."""

    def __init__(self, model_name="llama-3.2-11b-vision-preview", personality_prompt=None):
        """
        Initializes the AI Message Handler with Groq's LLM and memory.

        Parameters:
        - model_name (str): The Groq LLM model to use. Default is `llama-3.2-11b-vision-preview`.
        - personality_prompt (str): Path to file containing personality system prompt
        """
        self.model_name = model_name
        self.memory = MemorySaver()

        # Define a structured chat prompt template
        self.system_prompt = self.load_system_prompt(
            hardware_file="prompts/hardware_specs.txt",
            message_template_file="prompts/message_template.txt",
            personality_file=personality_prompt
        )

        # Initialize Groq LLM using Langchain's official integration
        self.llm = ChatGroq(
            model_name=self.model_name,
            temperature=0.7,  # Controls randomness (0 = deterministic, 1 = more creative)
            api_key=GROQ_API_KEY  # Uses the loaded API key
        )

        # Define a structured chat prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "{input}")  # User message placeholder
        ])

        # Create the agent with long-term memory. If we need it to search the internet or use custom APIs, we'll pass
        # them along with tools but for now it can be an empty list
        self.agent = create_react_agent(self.llm, tools=[], checkpointer=self.memory)

    def load_system_prompt(self, hardware_file, message_template_file, personality_file):
        """
        Loads and merges system prompts from multiple sources.

        Parameters:
        - hardware_file (str): Path to the hardware specifications file.
        - message_template_file (str): Path to the message template file.
        - personality_file (str): Path to the personality prompt file.

        Returns:
        - str: The merged system prompt.
        """
        prompt_parts = []

        # Load hardware specs
        if os.path.exists(hardware_file):
            with open(hardware_file, "r", encoding="utf-8") as file:
                prompt_parts.append(file.read().strip())
        else:
            print(f"⚠️ Warning: {hardware_file} not found.")

        # Load message template
        if os.path.exists(message_template_file):
            with open(message_template_file, "r", encoding="utf-8") as file:
                prompt_parts.append(file.read().strip())
        else:
            print(f"⚠️ Warning: {message_template_file} not found.")

        # Load personality prompt (optional)
        if personality_file and os.path.exists(personality_file):
            with open(personality_file, "r", encoding="utf-8") as file:
                prompt_parts.append(file.read().strip())
        else:
            print(f"⚠️ Warning: {personality_file} not found. Using default system prompt.")

        return "\n\n".join(prompt_parts)  # Merge all into a single system prompt

    def query_llm(self, query, thread_id="default_thread"):
        """
        Sends a user query to the AI agent with memory.

        Parameters:
        - query (str): The user input message.
        - thread_id (str): The unique ID for tracking conversations.

        Returns:
        - str: The AI-generated response.
        """
        # Define the configuration for the agent
        config = {"configurable": {"thread_id": thread_id}}
        messages = [
            {"role": "system", "content": self.system_prompt}, # Apply the system prompt behavior
            {"role": "user", "content": query}  # User query
        ]

        # Query the agent in a streaming fashion (useful for real-time feedback)
        response = None
        for step in self.agent.stream(
                {"messages": messages},
                config,
                stream_mode="values"
        ):
            last_message = step["messages"][-1]  # Get the last message object

            if isinstance(last_message, str):
                response = last_message  # In case it's just a string, return it directly
            elif hasattr(last_message, "content"):
                response = last_message.content  # Extract content from Langchain message object
            else:
                print("⚠️ Unexpected message format:", last_message)
                response = "I encountered an unexpected error processing this message."

        return response

    def parse_response(self, response):
            """ Parses agent response into structured tasks """
            try:
                print("Received: ", response)
                return json.loads(response) # If the format needs to be JSON
                #return {"Message": {"message_1": response}}

            except json.JSONDecodeError:
                return {"Message": {"message_1": "Sorry, I didn't understand that."}}

    def clear_memory(self):
        """ Clears memory from Langroid agent"""
        self.agent.memory.clear()