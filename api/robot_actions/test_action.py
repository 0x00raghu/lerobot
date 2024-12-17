import time

def execute_test_action() -> dict:
    """
    Test robot action that waits for 5 seconds
    Returns:
        dict: Success status
    """
    print("Starting to wait for 5 seconds...")
    time.sleep(5)
    print("Done waiting!")
    return {"success": True}