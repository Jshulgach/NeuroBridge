import threading


class AISkills:
    """ Handles robot actions based on AI responses """

    def __init__(self, server):
        self.server = server

    def execute_task(self, response):
        """ Determines and executes AI-generated tasks """
        response_data = self.server.message_handler.parse_response(response)
        for key, value in response_data.items():
            if key == "Message":
                print(f"AI Response: {value['message_1']}")
                if self.server.parameters['enable_tts']:
                    # Combine all the data contains in the keys into a single value
                    combined_message = ""
                    for msg_key, msg_value in value.items():
                        combined_message += msg_value
                    threading.Thread(target=self.server.audio_client.say, args=(combined_message,), daemon=True).start()
                    #self.server.audio_client.say(value['message_1'])

            if key == "Action":
                for action, details in value.items():
                    if "skills" in details:
                        self.execute_skill(details["skills"])

                    if "movements" in details:
                        self.execute_movement(details["movements"])

    def execute_skill(self, skills):
        """ Executes hardware-specific skills """
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

            else:
                print(f"Unknown skill: {skill}")

    def execute_movement(self, movements):
        """ Executes robot-specific movements """
        for movement_name, movement_data in movements.items():
            print("Executing Movement: ", movement_name)

            # Extract movement type
            for action, params in movement_data.items():
                if action == "move_joint":
                    motor_id = params.get("motor")
                    position = params.get("value")

                    if motor_id is not None and position is not None:
                        print(f"Sending move_joint command to motor '{motor_id}' with value {position}")

                        # Send command to the robot if available
                        if self.server.robot:
                            self.server.robot.move_joint(motor_id, position)
                    else:
                        print(f"⚠️ Invalid move_joint parameters: {params}")