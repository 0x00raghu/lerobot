import subprocess
import os
from typing import Dict, Any

class RobotActionExecutor:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def execute_pick_candy_black_arm(self, **kwargs) -> Dict[str, Any]:
        """Execute the pick candy with black arm action"""
        try:
            cmd = [
                "python", 
                os.path.join(self.base_path, "lerobot/scripts/control_robot.py"),
                "record",
                "--robot-path", "lerobot/configs/robot/so100.yaml",
                "--fps", "30",
                "--repo-id", "0x00raghu/eval_pick_red_candy",
                "--warmup-time-s", "5",
                "--episode-time-s", "30",
                "--reset-time-s", "1",
                "--num-episodes", "1",
                "--play-sounds", "0",
                "-p", "outputs/train/all_red/checkpoints/last/pretrained_model",
                "--single-task", "pick_candy_red"
            ]
            
            subprocess.run(cmd, check=True)
            return {"success": True}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}

    def execute_pick_candy_orange_arm(self, **kwargs) -> Dict[str, Any]:
        """Execute the pick candy with orange arm action"""
        try:
            cmd = [
                "python",
                os.path.join(self.base_path, "lerobot/scripts/control_robot.py"), 
                "record",
                "--robot-path", "lerobot/configs/robot/so100_orange.yaml",
                "--fps", "30",
                "--repo-id", "0x00raghu/eval_pick_blue_candy",
                "--warmup-time-s", "5",
                "--episode-time-s", "30",
                "--reset-time-s", "1",
                "--num-episodes", "1",
                "--play-sounds", "0",
                "-p", "outputs/train/all_blue_og/checkpoints/last/pretrained_model",
                "--single-task", "pick_candy_blue"
            ]
            
            subprocess.run(cmd, check=True)
            return {"success": True}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}

    def execute_give_candy_to_hand(self, **kwargs) -> Dict[str, Any]:
        """Execute the give candy to hand action"""
        try:
            cmd = [
                "python",
                os.path.join(self.base_path, "lerobot/scripts/control_robot.py"),
                "record", 
                "--robot-path", "lerobot/configs/robot/so100.yaml",
                "--fps", "30",
                "--repo-id", "0x00raghu/eval_candy_to_hand",
                "--warmup-time-s", "5",
                "--episode-time-s", "30",
                "--reset-time-s", "1",
                "--num-episodes", "1",
                "--play-sounds", "0",
                "-p", "outputs/train/pick_blue_candy/checkpoints/last/pretrained_model",
                "--single-task", "pick_candy_blue"
            ]
            
            subprocess.run(cmd, check=True)
            return {"success": True}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}