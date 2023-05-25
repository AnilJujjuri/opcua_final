import asyncio
import time
from fastapi import FastAPI
from opcua import Client, Server, ua

app = FastAPI()

# Set up the server
server = Server()
server.set_endpoint("opc.tcp://localhost:5007/freeopcua/server/")

# Get Objects node, this is where we should put our nodes
objects = server.get_objects_node()

# Populating our address space
uri = "http://examples.freeopcua.github.io"
idx = server.register_namespace(uri)
myobj = objects.add_object(idx, "MyObject")
myvar = myobj.add_variable(idx, "MyVariable", 6.7)
myvar.set_writable() # Set MyVariable to be writable by clients

# Start the server in a try-finally block to ensure it's properly closed
try:
    server.start()

    @app.get("/")
    def read_root():
        return {"Hello": "World"}

    # Define a route to read the variable
    @app.get("/read_var")
    async def read_var():
        value = myvar.get_value()
        return {"value": value}

    # Define a route to write to the variable
    @app.put("/write_var")
    async def write_var(value: float):
        myvar.set_value(value)
        return {"value": value}

    # Define a route to check if the server is running
    @app.get("/final")
    async def final():
        return {"status": "ok"}

    # Define a background task to read the variable periodically
    async def read_loop():
        count=6.7
        while True:
            time.sleep(0.1)
            count+=0.1
            myvar.set_value(count)
            await asyncio.sleep(1)

    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(read_loop())

    @app.on_event("shutdown")
    async def shutdown_event():
        server.stop()

    # Set up the client
    client = Client("opc.tcp://localhost:5007/freeopcua/server/")
    client.connect()

except Exception as e:
    print("Error:", e)
    server.stop()