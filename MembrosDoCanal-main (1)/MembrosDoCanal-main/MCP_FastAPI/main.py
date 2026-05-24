from fastapi_mcp import FastApiMCP
from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

@app.get("/")
async def root():
   
    return {"message": "Hello World"}

# Add MCP server to the FastAPI app
mcp = FastApiMCP(app)

# Mount the MCP server to the FastAPI app
mcp.mount()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)