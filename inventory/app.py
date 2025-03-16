import threading
from fastapi import FastAPI

from api import router
from events import order_event_listener


app = FastAPI()

app.include_router(router)



# start the listener in a separate thread
threading.Thread(target=order_event_listener, daemon=True).start()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
