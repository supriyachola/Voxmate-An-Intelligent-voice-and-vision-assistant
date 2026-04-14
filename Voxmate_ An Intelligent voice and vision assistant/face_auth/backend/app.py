# app.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import os
import uuid
import numpy as np
from numpy.linalg import norm
from deepface import DeepFace
import traceback
import json

app = FastAPI()

# Allow frontend access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage paths
FACES_DIR = "faces"
os.makedirs(FACES_DIR, exist_ok=True)


# --------------------------
# Utilities
# --------------------------
def _save_upload_to_path(upload: UploadFile, path: str):
    with open(path, "wb") as f:
        f.write(upload.file.read())


def _extract_embedding_from_path(path: str):
    """
    Use DeepFace.represent to get the embedding vector from an image file.
    Returns a 1-D numpy array (float32) or raises an Exception if extraction fails.
    """
    # DeepFace.represent returns a list of dicts, each dict has "embedding"
    reps = DeepFace.represent(img_path=path, model_name="Facenet", enforce_detection=False)
    if not reps or len(reps) == 0:
        raise ValueError("No face representation returned by DeepFace")
    emb = np.array(reps[0]["embedding"], dtype=np.float32)
    return emb


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # handle zero vectors defensively
    if a is None or b is None:
        return 0.0
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _user_embedding_path(user_id: str) -> str:
    # store averaged embedding as .npy per user
    safe = user_id.strip().lower()
    return os.path.join(FACES_DIR, f"{safe}.npy")


# --------------------------
# Enroll endpoint (multiple files)
# --------------------------
@app.post("/enroll")
async def enroll(user_id: str = Form(...), files: List[UploadFile] = File(...)):
    """
    Expects:
      - user_id (form)
      - multiple files with field name 'files' (FormData)
    Stores averaged embedding for the user at faces/{user_id}.npy
    Returns JSON: {"status":"success","message":"..."} on success
    """
    try:
        user_id = user_id.strip().lower()
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="At least one image required for enrollment")

        embeddings = []
        temp_files = []
        # Save each uploaded file to a temp path and extract embedding
        for up in files:
            tmp_name = os.path.join(FACES_DIR, f"tmp_{uuid.uuid4().hex}.jpg")
            temp_files.append(tmp_name)
            # FastAPI UploadFile.file is a SpooledTemporaryFile - ensure pointer at start
            up.file.seek(0)
            with open(tmp_name, "wb") as f:
                f.write(await up.read())

            try:
                emb = _extract_embedding_from_path(tmp_name)
                embeddings.append(emb)
            except Exception as e:
                # skip images that fail face extraction but continue if others succeed
                app.logger if hasattr(app, "logger") else None
                print(f"[WARN] Failed to extract embedding for one image: {e}")

        # Cleanup temp files
        for t in temp_files:
            try:
                if os.path.exists(t):
                    os.remove(t)
            except Exception:
                pass

        if not embeddings:
            raise HTTPException(status_code=400, detail="No valid faces detected in uploaded images")

        # Average embeddings
        stacked = np.stack(embeddings, axis=0)
        avg = np.mean(stacked, axis=0).astype(np.float32)

        out_path = _user_embedding_path(user_id)
        np.save(out_path, avg)

        return {"status": "success", "message": f"User {user_id} enrolled"}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# Verify endpoint (single file)
# --------------------------
@app.post("/verify")
async def verify(user_id: str = Form(...), file: Optional[UploadFile] = File(None)):
    """
    Expects:
      - user_id (form)
      - single file under field name 'file'
    Returns:
      {"match": bool, "similarity": float, "message": str}
    """
    try:
        user_id = user_id.strip().lower()
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        if file is None:
            raise HTTPException(status_code=400, detail="Image file required")

        user_emb_path = _user_embedding_path(user_id)
        if not os.path.exists(user_emb_path):
            return {"match": False, "similarity": 0.0, "message": "❌ User not found. Please sign up first."}

        # Save the incoming file temporarily
        tmp_path = os.path.join(FACES_DIR, f"verify_{uuid.uuid4().hex}.jpg")
        file.file.seek(0)
        with open(tmp_path, "wb") as f:
            f.write(await file.read())

        try:
            probe_emb = _extract_embedding_from_path(tmp_path)
        except Exception as e:
            # clean up
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return {"match": False, "similarity": 0.0, "message": "❌ No face detected in the uploaded image."}

        # load stored embedding
        stored = np.load(user_emb_path)

        # compute cosine similarity
        sim = _cosine_similarity(probe_emb, stored)
        threshold = 0.90  # tweak as needed

        match = sim >= threshold
        msg = "✅ Login successful!" if match else "❌ Login failed (Face mismatch)."

        # cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        return {"match": bool(match), "similarity": float(sim), "message": msg}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# Optional: simple LiveKit token endpoint (safe)
# --------------------------
class TokenRequest(BaseModel):
    identity: str
    room: Optional[str] = "face-auth-room"


@app.post("/get_token")
def get_token(req: TokenRequest):
    """
    Optional helper. Will try to create a LiveKit access token if livekit-server-sdk
    is installed and LIVEKIT_API_KEY / LIVEKIT_API_SECRET env vars are set.
    If not available it will return a clear error message.
    """
    try:
        # lazy import so endpoint still works even if livekit lib isn't installed
        try:
            from livekit import api as lkapi  # type: ignore
        except Exception:
            return {"error": "livekit-server-sdk not installed on server. Install it or skip /get_token."}

        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        url = os.getenv("LIVEKIT_URL")

        if not api_key or not api_secret or not url:
            return {"error": "Missing LIVEKIT_API_KEY, LIVEKIT_API_SECRET or LIVEKIT_URL in server environment."}

        # Create token depending on the livekit-server-sdk version
        # There are multiple livekit libraries with slightly different APIs;
        # try a couple of patterns safely.
        try:
            # newer style (AccessToken(...); add_grant)
            token = lkapi.AccessToken(api_key, api_secret)
            grant = lkapi.VideoGrant(room_join=True, room=req.room)
            # some versions use add_grant, others use add_grants; try both
            if hasattr(token, "add_grant"):
                token.add_grant(grant)
            elif hasattr(token, "add_grants"):
                token.add_grants(grant)
            else:
                # fallback: try setting grants attr (not ideal)
                pass
            # set identity if supported
            try:
                token.identity = req.identity
            except Exception:
                pass

            jwt = token.to_jwt()
            return {"token": jwt, "url": url}
        except Exception as e:
            # if AccessToken signature is different, return helpful message
            return {"error": "Failed to create LiveKit token: " + str(e)}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# Root
# --------------------------
@app.get("/")
def root():
    return {"message": "Face Auth Backend running"}
