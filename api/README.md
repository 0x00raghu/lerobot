# Gemini-Multimodal-Backend
We set up policies as function calls that the chrome extension triggers when the model outputs a function call on https://aistudio.google.com/live.

## API Usage

The API server runs on port 8000. To interact with it from another local server:

### Run Robot Test Action

**Endpoint:** `GET http://localhost:8000/trigger-robot-action/{functionName}`

**Description:**  
Triggers running of a python file corresponding to the function name.


**Response:**

json
{
"success": true
}

or in case of error:

json
{
"success": false,
"error": "error message"
}

Or for invalid function names:

json
{
"detail": "Invalid function name. Valid functions are: ['testRobotAction']"
}

## Setup
1. Install dependencies:

bash
pip install -r requirements.txt

2. Run the server:

bash
python api/main.py


The server will start on `http://0.0.0.0:8000`


## Adding New Robot Actions

1. Add your robot action implementation in `api/robot_actions/real_actions.py`
2. Register the new action in the `VALID_ROBOT_ACTIONS` dictionary in `api/main.py`

## Development

- The `test_action.py` provides a simple way to test the API functionality without actual robot hardware
- Real robot actions are implemented through the `RobotActionExecutor` class in `real_actions.py`
- All robot control scripts are executed from the main lerobot package


## License
This project is licensed under the Apache License 2.0 - see the LICENSE file for details.