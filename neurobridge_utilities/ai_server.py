import asyncio
import collections
import threading
import time
from mini_arm import MiniArmClient

from neurobridge_utilities.ai_camera import AICamera
from neurobridge_utilities.ai_message_handler import AIMessageHandler
from neurobridge_utilities.ai_skills import AISkills
from neurobridge_utilities.ai_audio import AIAudio
from neurobridge_utilities.keyboard_poller import KeyboardPoller, KBHit


class AIServer:
    """ AI Server class handling user interactions and LLM responses

    Parameters:
    -----------
        object_detector_id    (str) : The model type used for object detect (example: groundingDino, YoloV5)
        """

    def __init__(self,
                 object_detector_id="IDEA-Research/grounding-dino-tiny",
                 llm_model_id="llama-3.2-11b-vision-preview",
                 enable_camera=False,
                 camera_id=0,
                 enable_tts=False,
                 enable_stt=False,
                 personality_prompt=None,
                 use_robot=False,
                 robot_port="COM7",
                 verbose=False):
        self.object_detector_id = object_detector_id
        self.llm_model_id = llm_model_id
        self.enable_camera = enable_camera
        self.camera_id = camera_id
        self.enable_tts = enable_tts
        self.enable_stt = enable_stt
        self.verbose = verbose

        # Initialize parameters dictionary
        self.parameters = {
            'enable_camera': enable_camera,
            'all_stop': False,
            'enable_tts': enable_tts,
            'enable_stt': enable_stt,
            'verbose': verbose,
            'use_robot': use_robot,
            'audio_input_ready': True
        }

        # Initialize TTS Audio client if requested
        if self.parameters['enable_tts'] or self.parameters['enable_stt']:
            self.audio_client = AIAudio(
                use_elevenlabs=self.parameters['enable_tts'],
                speech_model_id="eleven_flash_v2", # Fastest one I found
                voice_id='robot_cold',
            )

        # Initialize Keyboard Poller
        # self.poller = KeyboardPoller(self.verbose)s
        self.kb = KBHit()

        # Initialize LLM Message Handler with system prompts, pass in personality if desired
        self.message_handler = AIMessageHandler(llm_model_id, personality_prompt)

        # Initialize AI Skills, handles the function/tool/robot executions
        self.skills = AISkills(self)  # Pass reference to execute skills

        # Initialize Camera
        self.camera = AICamera(camera_id) if self.parameters['enable_camera'] else None

        # Query queues
        self.query_queue = collections.deque()
        self.response_queue = collections.deque()
        self.agent_response = None

        # Load the robot client
        self.robot = None
        if self.parameters['use_robot']:
            self.robot = MiniArmClient('MiniArm', port=robot_port, baudrate=9600)
            print("Robot connected!")

    def terminal_interface(self):
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

                    # await asyncio.sleep(0.05)
                    time.sleep(0.05)

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

            time.sleep(0.1)

    def microphone_interface(self):
        """ A non-blocking microphone interface to safely collect user queries from the microphone
        """
        print \
            ('n🚀 AI Assistant Microphone in Online! Your voice is automatically transcribed. Say "exit" or "quit" to stop.')
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
                    break

                # Add to the queue
                self.query_queue.append(user_input_str)

                time.sleep(5)  # Wait 5 seconds before saying the next message

            except KeyboardInterrupt:
                print("Ctrl+C detected, Shutting down...")
                self.parameters['all_stop'] = True

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
        if self.parameters['enable_stt']:
            threading.Thread(target=self.microphone_interface, daemon=True).start()
        else:
            threading.Thread(target=self.terminal_interface, daemon=True).start()

        await asyncio.gather(
            # self.terminal_interface(), # Not together with microphone_interface
            # self.microphone_interface(),
            self.process_user_queries(),
        ) # Run both functions concurrently until done
        print("🚀 AI Server shutting down...")
