"""FastAPI Application Entry Point for Prime Check Service."""

import os
import sys
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes import router

# Ensure Python handles integers with large string representations (> 4300 digits)
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)

app = FastAPI(
    title="Prime Check Service (Miller-Rabin Engine)",
    description="High-performance, arbitrary-precision prime validation service up to 1024 bits and beyond.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time-Ms"] = f"{process_time * 1000.0:.3f}"
    return response


# Include API Router
app.include_router(router)

# Mount static folder
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
async def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Prime Check Service API is running. Access /docs for Swagger UI."}
