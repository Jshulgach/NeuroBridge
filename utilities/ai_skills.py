import threading

#from dotenv import load_dotenv
#load_dotenv()


class AISkills:
    """ Handles robot actions based on AI responses """

    def __init__(self, server):
        self.server = server

    def execute_task(self, response):
        """ Determines and executes AI-generated tasks """
        print("Sending to message handler: ", response)
        response_data = self.server.message_handler.parse_response(response)

        print(f"Response data: {response_data}")
        for key, value in response_data.items():
            if key == "Message":
                print(f"AI Response: {value['message_1']}")
                if self.server.parameters['enable_tts']:
                    threading.Thread(target=self.server.audio_client.say, args=(value['message_1'],), daemon=True).start()
                    #self.server.audio_client.say(value['message_1'])

            elif key == "Action":
                for action, details in value.items():
                    if "skills" in details:
                        self.execute_skill(details["skills"])

    def execute_skill(self, skills):
        """ Executes robot-specific skills """
        for skill, params in skills.items():
            if skill == "camera_enable":
                if self.server.camera:
                    threading.Thread(target=self.server.camera.start, daemon=True).start()

            elif skill == "camera_disable":
                if self.server.camera:
                    self.server.camera.stop()

            elif skill == "object_detection":
                if self.server.camera:
                    threading.Thread(target=self.server.camera.detect_objects, args=(params["object"],), daemon=True).start()
