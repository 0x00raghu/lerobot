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
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
robot_executor = RobotActionExecutor(BASE_PATH)

# Define valid robot actions
VALID_ROBOT_ACTIONS = {
    "testRobotAction": execute_test_action,
    "pickRedCandy": robot_executor.execute_pick_red_candy
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
    uvicorn.run(app, host="0.0.0.0", port=8000)