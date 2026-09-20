import os
import io
import hashlib
import hmac
from dotenv import load_dotenv

# Load secret environment variables
load_dotenv()
HASH_SALT = os.getenv("HASH_SALT", "facechain_default_secure_salt_2026").encode('utf-8')

import cv2
import numpy as np
import requests

from blockchain import store_face_record, verify_face_record

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from insightface.app import FaceAnalysis


# ============================================================
# FACECHAIN BACKEND
# YuNet + ArcFace + Google Lens + Blockchain
# ============================================================

app = FastAPI(
    title="FaceChain Backend",
    description="Face Identification & Blockchain Verification Backend",
    version="3.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "face_detection_yunet_2026may.onnx",
)

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

SERPAPI_IMAGE_URL = "https://serpapi.com/image"
SERPAPI_SEARCH_URL = "https://serpapi.com/search"

# Face similarity threshold.
# This is a heuristic and does NOT prove identity.
FACE_MATCH_THRESHOLD = 0.65

# Maximum number of web images to compare.
MAX_FACE_COMPARISONS = 20

# Minimum useful face image dimension.
MIN_FACE_IMAGE_DIMENSION = 500


# ============================================================
# LOAD YUNET
# ============================================================

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"YuNet model not found at: {MODEL_PATH}"
    )


face_detector = cv2.FaceDetectorYN.create(
    MODEL_PATH,
    "",
    (320, 320),
    0.6,
    0.3,
    5000,
)


# ============================================================
# LOAD INSIGHTFACE / ARCFACE
# ============================================================

print("Loading InsightFace buffalo_l model...")

face_analysis = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"],
)

face_analysis.prepare(
    ctx_id=0,
    det_size=(640, 640),
)

print("InsightFace loaded successfully.")


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "FaceChain Backend is running",
        "status": "online",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    try:
        from blockchain import blockchain_status

        blockchain = blockchain_status()

    except Exception as e:

        blockchain = {
            "connected": False,
            "message": str(e),
        }

    return {
        "status": "healthy",
        "opencv_version": cv2.__version__,
        "face_detector": "YuNet",
        "face_embedding_model": "InsightFace buffalo_l / ArcFace",
        "search_api_configured": bool(SERPAPI_KEY),
        "face_match_threshold": FACE_MATCH_THRESHOLD,
        "blockchain": blockchain,
    }
# ============================================================
# BLOCKCHAIN ENDPOINTS
# ============================================================

@app.get("/blockchain/status")
def get_blockchain_status():
    from blockchain import blockchain_status
    return blockchain_status()


@app.post("/blockchain/verify")
def verify_hash(image_hash: str):
    return verify_face_record(image_hash)


# ============================================================
# YUNET FACE DETECTION
# ============================================================

def detect_faces(image):

    height, width = image.shape[:2]

    face_detector.setInputSize(
        (width, height)
    )

    _, faces = face_detector.detect(image)

    detected_faces = []

    if faces is not None:

        for index, face in enumerate(faces):

            x = int(face[0])
            y = int(face[1])
            w = int(face[2])
            h = int(face[3])

            confidence = float(face[14])

            detected_faces.append({

                "face_id": index + 1,

                "x": x,
                "y": y,

                "width": w,
                "height": h,

                "confidence": round(
                    confidence,
                    4,
                ),
            })

    return detected_faces


# ============================================================
# CHOOSE BEST FACE
# ============================================================

def choose_best_face(faces):

    if not faces:
        return None

    return max(
        faces,
        key=lambda face: (
            face["width"] *
            face["height"]
        ),
    )


# ============================================================
# CROP FACE
# ============================================================

def crop_face(image, face):

    image_height, image_width = image.shape[:2]

    x = face["x"]
    y = face["y"]

    w = face["width"]
    h = face["height"]

    # Larger context around the face.
    margin_x = int(w * 0.25)
    margin_y = int(h * 0.25)

    left = max(
        0,
        x - margin_x,
    )

    top = max(
        0,
        y - margin_y,
    )

    right = min(
        image_width,
        x + w + margin_x,
    )

    bottom = min(
        image_height,
        y + h + margin_y,
    )

    cropped_face = image[
        top:bottom,
        left:right
    ]

    return cropped_face


# ============================================================
# UPSCALE SMALL FACE CROP
# ============================================================

def improve_face_crop(image):

    if image is None or image.size == 0:
        return image

    height, width = image.shape[:2]

    largest_dimension = max(
        height,
        width,
    )

    if largest_dimension >= MIN_FACE_IMAGE_DIMENSION:
        return image

    scale = (
        MIN_FACE_IMAGE_DIMENSION /
        largest_dimension
    )

    new_width = max(
        1,
        int(width * scale),
    )

    new_height = max(
        1,
        int(height * scale),
    )

    return cv2.resize(
        image,
        (
            new_width,
            new_height,
        ),
        interpolation=cv2.INTER_CUBIC,
    )


# ============================================================
# ARCFACE EMBEDDING
# ============================================================

def get_face_embedding(image):

    if image is None or image.size == 0:

        return None, False

    try:

        faces = face_analysis.get(
            image
        )

    except Exception as e:

        print(
            "InsightFace error:",
            e,
        )

        return None, False

    if not faces:

        return None, False

    # Select largest face.
    selected_face = max(
        faces,
        key=lambda face: (
            face.bbox[2] - face.bbox[0]
        ) * (
            face.bbox[3] - face.bbox[1]
        ),
    )

    embedding = selected_face.embedding

    if embedding is None:

        return None, False

    embedding = np.asarray(
        embedding,
        dtype=np.float32,
    )

    norm = np.linalg.norm(
        embedding
    )

    if norm == 0:

        return None, False

    embedding = embedding / norm

    return embedding, True


# ============================================================
# COSINE SIMILARITY
# ============================================================

def calculate_face_similarity(
    embedding_a,
    embedding_b,
):

    if (
        embedding_a is None
        or embedding_b is None
    ):

        return 0.0

    embedding_a = np.asarray(
        embedding_a,
        dtype=np.float32,
    )

    embedding_b = np.asarray(
        embedding_b,
        dtype=np.float32,
    )

    norm_a = np.linalg.norm(
        embedding_a
    )

    norm_b = np.linalg.norm(
        embedding_b
    )

    if norm_a == 0 or norm_b == 0:

        return 0.0

    return float(
        np.dot(
            embedding_a / norm_a,
            embedding_b / norm_b,
        )
    )


# ============================================================
# MATCH CLASSIFICATION
# ============================================================

def classify_face_match(similarity):

    if similarity >= FACE_MATCH_THRESHOLD:

        return "potential_face_match"

    if similarity >= 0.50:

        return "low_confidence_similarity"

    return "not_a_face_match"


# ============================================================
# PREPARE SEARCH IMAGE
# ============================================================

def prepare_search_image(image):

    """
    Compress image below SerpApi's 500 KB limit
    while keeping the image as large as practical.
    """

    if image is None or image.size == 0:

        raise ValueError(
            "Cannot prepare an empty image."
        )

    max_dimension = 1600
    quality = 90

    for attempt in range(15):

        height, width = image.shape[:2]

        scale = min(
            1.0,
            max_dimension / max(
                height,
                width,
            ),
        )

        new_width = max(
            1,
            int(width * scale),
        )

        new_height = max(
            1,
            int(height * scale),
        )

        resized = cv2.resize(
            image,
            (
                new_width,
                new_height,
            ),
            interpolation=cv2.INTER_AREA,
        )

        success, encoded = cv2.imencode(
            ".jpg",
            resized,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                quality,
            ],
        )

        if not success:

            raise ValueError(
                "Could not convert image to JPEG."
            )

        image_bytes = encoded.tobytes()

        size_kb = len(image_bytes) / 1024

        print(
            "Search image:",
            f"{new_width}x{new_height}",
            f"quality={quality}",
            f"size={size_kb:.1f} KB",
        )

        if len(image_bytes) <= 500 * 1024:

            return image_bytes

        if quality > 50:

            quality -= 10

        else:

            max_dimension = int(
                max_dimension * 0.80
            )

            quality = 80

    raise ValueError(
        "Could not compress image below "
        "SerpApi's 500 KB limit."
    )


# ============================================================
# SERPAPI IMAGE UPLOAD
# ============================================================

def upload_image_to_serpapi(image_bytes):

    if not SERPAPI_KEY:

        raise ValueError(
            "SERPAPI_KEY environment variable "
            "is not configured."
        )

    files = {

        "image": (
            "facechain_face.jpg",
            io.BytesIO(image_bytes),
            "image/jpeg",
        )

    }

    data = {
        "api_key": SERPAPI_KEY,
    }

    response = requests.post(
        SERPAPI_IMAGE_URL,
        files=files,
        data=data,
        timeout=60,
    )

    if response.status_code != 200:

        raise ValueError(
            "SerpApi Image API failed "
            f"({response.status_code}): "
            f"{response.text}"
        )

    result = response.json()

    if "error" in result:

        raise ValueError(
            "SerpApi image upload error: "
            f"{result['error']}"
        )

    image_id = result.get(
        "image_id"
    )

    if not image_id:

        raise ValueError(
            "SerpApi did not return an image_id."
        )

    return image_id


# ============================================================
# GOOGLE LENS
# ============================================================

def search_google_lens(
    image_id,
    search_type="visual_matches",
):

    if not SERPAPI_KEY:

        raise ValueError(
            "SERPAPI_KEY environment variable "
            "is not configured."
        )

    params = {

        "engine": "google_lens",

        "api_key": SERPAPI_KEY,

        "image_id": image_id,

        "type": search_type,

        "hl": "en",

        "country": "in",

        "safe": "active",

        "auto_crop": "true",
    }

    response = requests.get(
        SERPAPI_SEARCH_URL,
        params=params,
        timeout=90,
    )

    if response.status_code != 200:

        raise ValueError(
            "Google Lens API failed "
            f"({response.status_code}): "
            f"{response.text}"
        )

    result = response.json()

    if "error" in result:

        raise ValueError(
            "Google Lens error: "
            f"{result['error']}"
        )

    return result


# ============================================================
# FORMAT VISUAL MATCHES
# ============================================================

def format_visual_matches(lens_data):

    formatted = []

    matches = lens_data.get(
        "visual_matches",
        [],
    )

    for item in matches:

        formatted.append({

            "type": "visual_match",

            "title": item.get(
                "title"
            ),

            "source": item.get(
                "source"
            ),

            "link": item.get(
                "link"
            ),

            "thumbnail": item.get(
                "thumbnail"
            ),

            "image": item.get(
                "image"
            ),

            "exact_match": bool(
                item.get(
                    "exact_matches",
                    False,
                )
            ),
        })

    return formatted


# ============================================================
# FORMAT EXACT MATCHES
# ============================================================

def format_exact_matches(lens_data):

    formatted = []

    matches = lens_data.get(
        "exact_matches",
        [],
    )

    for item in matches:

        formatted.append({

            "type": "exact_match",

            "title": item.get(
                "title"
            ),

            "source": item.get(
                "source"
            ),

            "link": item.get(
                "link"
            ),

            "thumbnail": item.get(
                "thumbnail"
            ),

            "image": item.get(
                "image"
            ),

            "exact_match": True,
        })

    return formatted


# ============================================================
# DOWNLOAD IMAGE
# ============================================================

def download_web_image(image_url):

    if not image_url:

        return None

    try:

        headers = {

            "User-Agent":
                (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/140.0 Safari/537.36"
                ),

            "Accept":
                "image/avif,image/webp,image/apng,"
                "image/svg+xml,image/*,*/*;q=0.8",
        }

        response = requests.get(
            image_url,
            headers=headers,
            timeout=15,
            allow_redirects=True,
        )

        if response.status_code != 200:

            print(
                "Image download failed:",
                response.status_code,
                image_url,
            )

            return None

        if not response.content:

            return None

        image_array = np.frombuffer(
            response.content,
            dtype=np.uint8,
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR,
        )

        if image is None:

            return None

        return image

    except Exception as e:

        print(
            "Image download exception:",
            e,
        )

        return None


# ============================================================
# DOWNLOAD BEST AVAILABLE CANDIDATE IMAGE
# ============================================================

def download_candidate_image(result):

    """
    Try actual image first.
    If that fails, try Lens thumbnail.
    """

    image_url = result.get(
        "image"
    )

    thumbnail_url = result.get(
        "thumbnail"
    )

    # Try full image first.
    if image_url:

        print(
            "Trying candidate image..."
        )

        image = download_web_image(
            image_url
        )

        if image is not None:

            return image, "image"

    # Fallback to thumbnail.
    if thumbnail_url:

        print(
            "Trying candidate thumbnail..."
        )

        image = download_web_image(
            thumbnail_url
        )

        if image is not None:

            return image, "thumbnail"

    return None, None


# ============================================================
# COMPARE SINGLE WEB IMAGE
# ============================================================

def compare_web_image(
    result,
    query_embedding,
):

    candidate_image, source_used = (
        download_candidate_image(
            result
        )
    )

    if candidate_image is None:

        return {

            "status": "completed",

            "face_found": False,

            "similarity": None,

            "match":
                "image_download_failed",

            "image_source":
                None,
        }

    candidate_embedding, face_found = (
        get_face_embedding(
            candidate_image
        )
    )

    if not face_found:

        return {

            "status": "completed",

            "face_found": False,

            "similarity": None,

            "match":
                "no_face_in_candidate",

            "image_source":
                source_used,
        }

    similarity = calculate_face_similarity(
        query_embedding,
        candidate_embedding,
    )

    return {

        "status": "completed",

        "face_found": True,

        "similarity": round(
            similarity,
            4,
        ),

        "match":
            classify_face_match(
                similarity
            ),

        "image_source":
            source_used,
    }


# ============================================================
# COMPARE SEARCH RESULTS
# ============================================================

def compare_search_results(
    results,
    query_embedding,
):

    compared_results = []

    comparisons_done = 0

    for result in results:

        if comparisons_done >= MAX_FACE_COMPARISONS:

            result["face_comparison"] = {

                "status":
                    "not_compared",

                "reason":
                    "Comparison limit reached.",
            }

            compared_results.append(
                result
            )

            continue

        print(
            "Comparing candidate:",
            result.get("title"),
        )

        comparison = compare_web_image(
            result,
            query_embedding,
        )

        result["face_comparison"] = (
            comparison
        )

        comparisons_done += 1

        compared_results.append(
            result
        )

    def similarity_value(item):

        comparison = item.get(
            "face_comparison",
            {}
        )

        similarity = comparison.get(
            "similarity"
        )

        if similarity is None:

            return -1

        return similarity

    compared_results.sort(
        key=similarity_value,
        reverse=True,
    )

    return compared_results


# ============================================================
# BLOCKCHAIN RECORD
# ============================================================

def process_blockchain_record(contents):

    """
    Create a SHA-256 hash of the uploaded image
    and store/verify that hash on FaceChain.
    """

    blockchain_result = {

        "status": "not_started",

        "verified": False,

        "image_hash": None,

        "transaction_hash": None,

        "block_number": None,

        "contract_address": None,

        "submitted_by": None,

        "timestamp": None,

        "message": None,
    }

    try:

        # ----------------------------------------------------
        # SHA-256 HASH
        # ----------------------------------------------------

        image_hash = hmac.new(HASH_SALT, contents, hashlib.sha256).hexdigest()

        blockchain_result["image_hash"] = (
            image_hash
        )

        print(
            "SHA-256 image hash:",
            image_hash,
        )

        # ----------------------------------------------------
        # CHECK EXISTING RECORD
        # ----------------------------------------------------

        existing_record = verify_face_record(
            image_hash
        )

        blockchain_result["contract_address"] = (
            existing_record.get(
                "contract_address"
            )
        )

        if existing_record.get("verified"):

            blockchain_result["status"] = (
                "already_verified"
            )

            blockchain_result["verified"] = True

            blockchain_result["submitted_by"] = (
                existing_record.get(
                    "submitted_by"
                )
            )

            blockchain_result["timestamp"] = (
                existing_record.get(
                    "timestamp"
                )
            )

            blockchain_result["message"] = (
                "This image hash already exists "
                "on the FaceChain blockchain."
            )

            print(
                "Image already exists on blockchain."
            )

            return blockchain_result

        # ----------------------------------------------------
        # STORE NEW RECORD
        # ----------------------------------------------------

        transaction = store_face_record(
            image_hash
        )

        blockchain_result["status"] = (
            "verified"
        )

        blockchain_result["verified"] = True

        blockchain_result["transaction_hash"] = (
            transaction.get(
                "transaction_hash"
            )
        )

        blockchain_result["block_number"] = (
            transaction.get(
                "block_number"
            )
        )

        blockchain_result["contract_address"] = (
            transaction.get(
                "contract_address"
            )
        )

        blockchain_result["submitted_by"] = (
            transaction.get(
                "submitted_by"
            )
        )

        blockchain_result["message"] = (
            "Image hash successfully stored "
            "on the FaceChain blockchain."
        )

        print(
            "Blockchain transaction:",
            transaction,
        )

    except Exception as e:

        blockchain_result["status"] = (
            "failed"
        )

        blockchain_result["verified"] = False

        blockchain_result["message"] = str(e)

        print(
            "Blockchain error:",
            e,
        )

    return blockchain_result


# ============================================================
# FACE DETECTION ENDPOINT
# ============================================================

@app.post("/detect-face")
async def detect_face(
    file: UploadFile = File(...),
):

    contents = await file.read()

    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    image_array = np.frombuffer(
        contents,
        dtype=np.uint8,
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR,
    )

    if image is None:

        raise HTTPException(
            status_code=400,
            detail="Invalid image file.",
        )

    faces = detect_faces(
        image
    )

    return {

        "success": True,

        "face_detected":
            len(faces) > 0,

        "message":
            (
                f"{len(faces)} face(s) detected successfully."
                if faces
                else "No face detected."
            ),

        "face_count":
            len(faces),

        "faces":
            faces,

        "image_width":
            int(image.shape[1]),

        "image_height":
            int(image.shape[0]),
    }


# ============================================================
# FULL INVESTIGATION
# ============================================================

@app.post("/investigate")
async def investigate(
    file: UploadFile = File(...),
):

   # -----------------------------------------------------------------
    # 1. VALIDATE FILE TYPE & EMPTY CHECK
    # -----------------------------------------------------------------
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format: '{file.content_type}'. Please upload a valid JPEG or PNG image.",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # -----------------------------------------------------------------
    # 2. VALIDATE IMAGE DECODING & DETECT FACE PRESENCE
    # -----------------------------------------------------------------
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Corrupted image file: unable to decode image.",
        )

    detected_faces = detect_faces(image)
    if not detected_faces or len(detected_faces) == 0:
        raise HTTPException(
            status_code=400,
            detail="No valid face detected in the provided image.",
        )

    # -----------------------------------------------------------------
    # 3. RUN BLOCKCHAIN RECORDING (Only after validation passes)
    # -----------------------------------------------------------------
    blockchain_result = process_blockchain_record(contents)

    # --------------------------------------------------------
    # DECODE
    # --------------------------------------------------------

    image_array = np.frombuffer(
        contents,
        dtype=np.uint8,
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR,
    )

    if image is None:

        raise HTTPException(
            status_code=400,
            detail="Invalid image file.",
        )

    # --------------------------------------------------------
    # DETECT FACES
    # --------------------------------------------------------

    faces = detect_faces(
        image
    )

    image_width = int(
        image.shape[1]
    )

    image_height = int(
        image.shape[0]
    )

    # --------------------------------------------------------
    # NO FACE
    # --------------------------------------------------------

    if not faces:

        return {

            "success": False,

            "message":
                "No face detected.",

            "face_detected":
                False,

            "face_detection": {

                "status":
                    "failed",

                "face_count":
                    0,

                "faces":
                    [],

                "image_width":
                    image_width,

                "image_height":
                    image_height,
            },

            "web_search": {

                "status":
                    "not_started",

                "results":
                    [],
            },

            "face_matching": {

                "status":
                    "not_started",

                "potential_matches":
                    [],
            },

            "blockchain": blockchain_result,
        }

    # --------------------------------------------------------
    # BEST FACE
    # --------------------------------------------------------

    best_face = choose_best_face(
        faces
    )

    print(
        "Selected face:",
        best_face,
    )

    # --------------------------------------------------------
    # FACE CROP
    # --------------------------------------------------------

    face_crop = crop_face(
        image,
        best_face
    )

    if face_crop is None or face_crop.size == 0:

        return {

            "success": False,

            "message":
                "Face detected, but face crop failed.",

            "face_detected":
                True,

            "face_detection": {

                "status":
                    "success",

                "face_count":
                    len(faces),

                "faces":
                    faces,

                "selected_face":
                    best_face,

                "image_width":
                    image_width,

                "image_height":
                    image_height,
            },

            "web_search": {

                "status":
                    "failed",

                "results":
                    [],

                "error":
                    "Could not crop detected face.",
            },

            "face_matching": {

                "status":
                    "not_started",

                "potential_matches":
                    [],
            },

            "blockchain": blockchain_result,
        }

    # --------------------------------------------------------
    # IMPROVE CROP
    # --------------------------------------------------------

    face_crop = improve_face_crop(
        face_crop
    )

    print(
        "Face crop size:",
        face_crop.shape[1],
        "x",
        face_crop.shape[0],
    )

    # --------------------------------------------------------
    # ARCFACE EMBEDDING
    # --------------------------------------------------------

    query_embedding, embedding_face_found = (
        get_face_embedding(
            face_crop
        )
    )

    if not embedding_face_found:

        return {

            "success": False,

            "message":
                (
                    "Face detected, but ArcFace "
                    "could not generate an embedding."
                ),

            "face_detected":
                True,

            "face_detection": {

                "status":
                    "success",

                "face_count":
                    len(faces),

                "faces":
                    faces,

                "selected_face":
                    best_face,

                "image_width":
                    image_width,

                "image_height":
                    image_height,
            },

            "web_search": {

                "status":
                    "not_started",

                "results":
                    [],
            },

            "face_matching": {

                "status":
                    "failed",

                "potential_matches":
                    [],

                "error":
                    "ArcFace embedding generation failed.",
            },

           "blockchain": blockchain_result,
        }

    print(
        "ArcFace embedding generated:",
        len(query_embedding),
        "dimensions",
    )

    # --------------------------------------------------------
    # PREPARE SEARCH IMAGE
    # --------------------------------------------------------

    try:

        search_image = prepare_search_image(
            face_crop
        )

    except Exception as e:

        return {

            "success": False,

            "message":
                "Face detected, but image preparation failed.",

            "face_detected":
                True,

            "face_detection": {

                "status":
                    "success",

                "face_count":
                    len(faces),

                "faces":
                    faces,

                "selected_face":
                    best_face,

                "image_width":
                    image_width,

                "image_height":
                    image_height,
            },

            "web_search": {

                "status":
                    "failed",

                "results":
                    [],

                "error":
                    str(e),
            },

            "face_matching": {

                "status":
                    "not_started",

                "potential_matches":
                    [],
            },

            "blockchain": blockchain_result,
        }

    # --------------------------------------------------------
    # SERPAPI UPLOAD
    # --------------------------------------------------------

    try:

        image_id = upload_image_to_serpapi(
            search_image
        )

    except Exception as e:
        print(f"SerpAPI upload error: {e}")
        blockchain_result = process_blockchain_record(contents)

        return {

            "success": False,

            "message":
                "Face detected, but face image upload failed.",

            "face_detected":
                True,

            "face_detection": {

                "status":
                    "success",

                "face_count":
                    len(faces),

                "faces":
                    faces,

                "selected_face":
                    best_face,

                "image_width":
                    image_width,

                "image_height":
                    image_height,
            },

            "web_search": {

                "status":
                    "failed",

                "results":
                    [],

                "error":
                    str(e),
            },

            "face_matching": {

                "status":
                    "not_started",

                "potential_matches":
                    [],
            },

            "blockchain": blockchain_result,
        }

    # --------------------------------------------------------
    # VISUAL SEARCH
    # --------------------------------------------------------

    visual_results = []

    visual_error = None

    try:

        visual_data = search_google_lens(
            image_id,
            "visual_matches",
        )

        visual_results = format_visual_matches(
            visual_data
        )

    except Exception as e:

        visual_error = str(e)

        print(
            "Visual search error:",
            visual_error,
        )

    # --------------------------------------------------------
    # EXACT SEARCH
    # --------------------------------------------------------

    exact_results = []

    exact_error = None

    try:

        exact_data = search_google_lens(
            image_id,
            "exact_matches",
        )

        exact_results = format_exact_matches(
            exact_data
        )

    except Exception as e:

        exact_error = str(e)

        print(
            "Exact search error:",
            exact_error,
        )

    # --------------------------------------------------------
    # COMBINE RESULTS
    # --------------------------------------------------------

    all_results = []

    for result in exact_results:

        all_results.append(
            result
        )

    existing_links = set()

    for result in all_results:

        if result.get("link"):

            existing_links.add(
                result.get("link")
            )

    for result in visual_results:

        link = result.get(
            "link"
        )

        if link not in existing_links:

            all_results.append(
                result
            )

            if link:

                existing_links.add(
                    link
                )

    # --------------------------------------------------------
    # SEARCH STATUS
    # --------------------------------------------------------

    search_successful = (
        len(all_results) > 0
        or (
            visual_error is None
            and exact_error is None
        )
    )

    # --------------------------------------------------------
    # FACE COMPARISON
    # --------------------------------------------------------

    face_matching_results = []

    face_matching_error = None

    if all_results:

        try:

            face_matching_results = (
                compare_search_results(
                    all_results,
                    query_embedding,
                )
            )

        except Exception as e:

            face_matching_error = str(e)

            print(
                "Face matching error:",
                face_matching_error,
            )

            face_matching_results = (
                all_results
            )

    # --------------------------------------------------------
    # POTENTIAL MATCHES
    # --------------------------------------------------------

    potential_matches = []

    for result in face_matching_results:

        comparison = result.get(
            "face_comparison",
            {}
        )

        if comparison.get(
            "match"
        ) == "potential_face_match":

            potential_matches.append(
                result
            )
            filtered_results = [
        r for r in face_matching_results
        if r.get("face_comparison", {}).get("match") in ("potential_face_match", "low_confidence_similarity")
    ]

    # --------------------------------------------------------
    # BLOCKCHAIN
    # --------------------------------------------------------

    blockchain_result = (process_blockchain_record(contents)) 

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    return {

        "success":
            True,

        "message":
            "Face detected and reverse image investigation completed.",

        "face_detected":
            True,

        "face_detection": {

            "status":
                "success",

            "face_count":
                len(faces),

            "faces":
                faces,

            "selected_face":
                best_face,

            "image_width":
                image_width,

            "image_height":
                image_height,
        },

        "face_embedding": {

            "status":
                "generated",

            "model":
                "InsightFace buffalo_l / ArcFace",

            "dimensions":
                int(
                    len(query_embedding)
                ),
        },

        "web_search": {

            "status":
                (
                    "success"
                    if search_successful
                    else "failed"
                ),

            "image_id":
                image_id,

            "search_target":
                "detected_face",

            "result_count":
                len(face_matching_results),

            "exact_match_count":
                len(exact_results),

            "visual_match_count":
                len(visual_results),

            "results":
                face_matching_results,

            "visual_error":
                visual_error,

            "exact_error":
                exact_error,
        },

        "face_matching": {

            "status":
                (
                    "completed"
                    if face_matching_results
                    else "no_candidates"
                ),

            "model":
                "InsightFace buffalo_l / ArcFace",

            "threshold":
                FACE_MATCH_THRESHOLD,

            "comparisons_performed":
                min(
                    len(face_matching_results),
                    MAX_FACE_COMPARISONS,
                ),

            "potential_match_count":
                len(potential_matches),

            "potential_matches":
                potential_matches,

            "error":
                face_matching_error,
        },

        "blockchain":
            blockchain_result,
    }