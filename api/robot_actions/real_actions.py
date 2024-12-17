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
                "--repo-id", "${HF_USER}/eval_all_black",
                "--warmup-time-s", "5",
                "--episode-time-s", "40",
                "--reset-time-s", "10",
                "--num-episodes", "10",
                "--play-sounds", "0",
                "-p", "outputs/train/all_black/checkpoints/last/pretrained_model"
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
                "--robot-path", "lerobot/configs/robot/so100.yaml",
                "--fps", "30",
                "--repo-id", "${HF_USER}/eval_all_orange",
                "--warmup-time-s", "5",
                "--episode-time-s", "40",
                "--reset-time-s", "10",
                "--num-episodes", "10",
                "--play-sounds", "0",
                "-p", "outputs/train/all_orange/checkpoints/last/pretrained_model"
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
                "--repo-id", "${HF_USER}/eval_give_hand",
                "--warmup-time-s", "5",
                "--episode-time-s", "40",
                "--reset-time-s", "10",
                "--num-episodes", "10",
                "--play-sounds", "0",
                "-p", "outputs/train/give_hand/checkpoints/last/pretrained_model"
            ]
            
            subprocess.run(cmd, check=True)
            return {"success": True}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}