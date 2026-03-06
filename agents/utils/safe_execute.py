import traceback


def safe_execute(func, *args, **kwargs):

    try:
        result = func(*args, **kwargs)

        if result is None:
            return {
                "status": "error",
                "message": "Empty response from service"
            }

        return result

    except Exception as e:

        print("🚨 TOOL ERROR:", str(e))
        traceback.print_exc()

        return {
            "status": "error",
            "message": "Service temporarily unavailable"
        }