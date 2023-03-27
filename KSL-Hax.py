from error_handling import CompletelyDestroyedException, ApplicationErrorWindow, ErrorData
import traceback
import os

os.system('cls')

try:
    from app import App 
    app = App()
    app.start()
except CompletelyDestroyedException as c:
    ApplicationErrorWindow(c.message).start()
except Exception as e:
    ApplicationErrorWindow(ErrorData(title="Ya done did.", stack_trace=traceback.format_exc())).start()
