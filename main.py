import asyncio
import argparse
import collections
import threading
import time

# Import modular components
from utilities.ai_camera import AICamera
from utilities.ai_message_handler import AIMessageHandler
from utilities.ai_skills import AISkills
from utilities.ai_audio import AIAudio
from utilities.keyboard_poller import KeyboardPoller, KBHit

class AIServer:
    """ AI Server class handling user interactions and LLM responses """

    def __init__(self,
                 grounding_dino_id="IDEA-Research/grounding-dino-tiny",
                 llm_model_id="llama-3.2-11b-vision-preview",
                 enable_camera=False,
                 camera_id=0,
                 enable_tts=False,
                 verbose=False):
        self.grounding_dino_id = grounding_dino_id
        self.llm_model_id = llm_model_id
        self.verbose = verbose

        # Initialize parameters dictionary
        self.parameters = {'enable_camera': enable_camera, 'all_stop': False, 'enable_tts': enable_tts,
                           'verbose': verbose, 'audio_input_ready': True}

        # Initialize components
        self.audio_client = AIAudio()
        #self.poller = KeyboardPoller(self.verbose)
        self.kb = KBHit()
        self.message_handler = AIMessageHandler(llm_model_id)
        self.skills = AISkills(self)  # Pass reference to execute skills
        self.camera = AICamera(camera_id) if enable_camera else None

        # Query queues
        self.query_queue = collections.deque()
        self.response_queue = collections.deque()
        self.agent_response = None

    async def terminal_interface(self):
        """ A Non-blocking terminal interface to safely collect user queries from the terminal
        """
        print("\n🚀 AI Assistant Terminal is Online! Type a command and press Enter.")
        while not self.parameters['all_stop']:
            try:
                # user_input = input("You: ") # Blocking call
                user_input = []
                while True:
                    if self.kb.kbhit():
                        c = self.kb.getch()
                        # If enter was pressed, we break the loop
                        if ord(c) == 13: # ENTER key
                            print()
                            break
                        user_input.append(c)
                        msg = "".join(user_input)
                        print("\rYou: " + msg, end="")

                    await asyncio.sleep(0.05)

                user_input_str = "".join(user_input)
                user_input = [] # Clear the user input

                if user_input_str.lower() in ["exit", "quit"]:
                    print("Shutting down...")
                    self.parameters['all_stop'] = True

                # Add to the queue
                self.query_queue.append(user_input_str)

            except KeyboardInterrupt:
                print("Ctrl+C detected, Shutting down...")
                self.parameters['all_stop'] = True

            await asyncio.sleep(0.1)

    def microphone_interface(self):
        """ A non-blocking microphone interface to safely collect user queries from the microphone
        """
        print('n🚀 AI Assistant Microphone in Online! Your voice is automatically transcribed. Say "exit" or "quit" to stop.')
        while not self.parameters['all_stop']:
            try:
                # If we are ready to get more audio input then do so, otherwise wait until no other sound is being played
                if not self.parameters['audio_input_ready']:
                    time.sleep(0.5)

                user_input_str = self.audio_client.listen_and_transcribe()
                user_input_str = user_input_str.strip().strip('.')
                print(f"Received audio: {user_input_str}")

                if user_input_str.lower() in ["exit", "quit"]:
                    print("Shutting down...")
                    self.parameters['all_stop'] = True

                # Add to the queue
                print("Adding to queue")
                self.query_queue.append(user_input_str)


            except KeyboardInterrupt:
                print("Ctrl+C detected, Shutting down...")
                self.parameters['all_stop'] = True


        #await asyncio.sleep(0.1)

    async def process_user_queries(self):
        """ Process user queries asynchronously """
        while not self.parameters['all_stop']:
            if self.query_queue:
                query = self.query_queue.popleft()
                response = self.message_handler.query_llm(query)
                self.skills.execute_task(response)

            await asyncio.sleep(0.05)

    async def run(self):
        """ Start AI server """
        print("🚀 AI Server is starting...")
        # Run the microphone as a thread
        threading.Thread(target=self.microphone_interface, daemon=True).start()
        await asyncio.gather(
            self.terminal_interface(), # Not together with microphone_interface
            #self.microphone_interface(),
            self.process_user_queries(),
        ) # Run both functions concurrently until done
        print("🚀 AI Server shutting down...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Server")
    parser.add_argument("--config_file", type=str, default="config.yaml", help="Path to config file")
    parser.add_argument("--enable_tts", type=bool, default=True, help="Enable Text-To-Speech")
    parser.add_argument("--enable_camera", type=bool, default=False, help="Enable camera")
    parser.add_argument("--verbose", type=bool, default=False, help="Enable verbose mode")
    args = parser.parse_args()

    server = AIServer(enable_tts=args.enable_tts,verbose=args.verbose)
    asyncio.run(server.run())
