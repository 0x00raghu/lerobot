from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from api.robot_actions.test_action import execute_test_action
from api.robot_actions.real_actions import RobotActionExecutor

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize robot action executor
BASE_PATH = "/Users/raghuvamsivelagala/Desktop/lerobot"
robot_executor = RobotActionExecutor(BASE_PATH)

# Define valid robot actions
VALID_ROBOT_ACTIONS = {
    "testRobotAction": execute_test_action,
    "pickCandyBlackArm": robot_executor.execute_pick_candy_black_arm,
    "pickCandyOrangeArm": robot_executor.execute_pick_candy_orange_arm, 
    "giveCandyToHand": robot_executor.execute_give_candy_to_hand
}

@app.get("/trigger-robot-action/{functionName}")
async def trigger_robot_action(functionName: str):
    if functionName not in VALID_ROBOT_ACTIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid function name. Valid functions are: {list(VALID_ROBOT_ACTIONS.keys())}"
        )
    
    try:
        result = VALID_ROBOT_ACTIONS[functionName]()
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("Current working directory:", os.getcwd())
    print("Base path:", BASE_PATH)
    print("Full script path:", os.path.join(BASE_PATH, "lerobot/scripts/control_robot.py"))
    uvicorn.run(app, host="0.0.0.0", port=8000)