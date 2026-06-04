from fastapi.middleware.cors import CORSMiddleware


def add_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:4200"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
