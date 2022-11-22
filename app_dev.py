import os
import uvicorn


def run_development_api():
    os.environ["ENV"] = 'dev'
    host = "0.0.0.0"
    port = os.getenv("API_PORT", 8000)
    print(f">>>>> \tUI API deployed over: http://{host}:{port}/docs")
    uvicorn.run("app.main:api", host=host, port=port, debug=True, reload=True)


if __name__ == "__main__":
    run_development_api()
