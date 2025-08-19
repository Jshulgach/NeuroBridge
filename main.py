import asyncio
import argparse

from neurobridge_utilities.ai_server import AIServer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Server")
    parser.add_argument("--config_file", type=str, default="config.yaml", help="Path to config file")
    parser.add_argument("--enable_tts", type=bool, default=False, help="Enable Text-To-Speech")
    parser.add_argument("--enable_stt", type=bool, default=False, help="Enable Speech-To-Text")
    parser.add_argument("--enable_camera", type=bool, default=False, help="Enable camera")
    parser.add_argument("--camera_id", type=int, default=0, help="Camera ID")
    parser.add_argument("--use_robot", type=bool, default=False, help="Use robot")
    parser.add_argument("--robot_port", type=str, default="COM7", help="Robot port")
    parser.add_argument("--personality", type=str, default="prompts/personality_robot_friendly.txt", help="Path to prompt file")
    parser.add_argument("--verbose", type=bool, default=False, help="Enable verbose mode")
    args = parser.parse_args()

    server = AIServer(enable_stt=args.enable_stt,
                      enable_tts=args.enable_tts,
                      use_robot=args.use_robot,
                      robot_port=args.robot_port,
                      personality_prompt=args.personality,
                      verbose=args.verbose)
    asyncio.run(server.run())
