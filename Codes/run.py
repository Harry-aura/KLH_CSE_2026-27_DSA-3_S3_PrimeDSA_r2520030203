"""Server launcher script for Prime Check Service."""

import sys
import uvicorn

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)

if __name__ == "__main__":
    print("================================================================")
    print("  Prime Check Service - Miller-Rabin 1024-Bit Engine")
    print("  Server starting on http://127.0.0.1:8000")
    print("  Interactive Web UI: http://127.0.0.1:8000")
    print("  Swagger API Docs:   http://127.0.0.1:8000/docs")
    print("================================================================")
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=True)
