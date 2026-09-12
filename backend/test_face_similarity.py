import cv2
import numpy as np
from insightface.app import FaceAnalysis

print("===================================")
print(" FaceChain - Face Similarity Test")
print("===================================")

# -----------------------------
# Load ArcFace
# -----------------------------

print("\nLoading ArcFace model...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

print("✅ ArcFace loaded")


# -----------------------------
# Get face embedding
# -----------------------------

def get_embedding(image_path):

    print(f"\nProcessing: {image_path}")

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(
            f"Could not read {image_path}"
        )

    faces = app.get(image)

    if len(faces) == 0:
        raise ValueError(
            f"No face detected in {image_path}"
        )

    # Select largest face
    face = max(
        faces,
        key=lambda f:
        (f.bbox[2] - f.bbox[0]) *
        (f.bbox[3] - f.bbox[1])
    )

    embedding = face.embedding.astype(np.float32)

    # Normalize
    embedding = embedding / np.linalg.norm(embedding)

    print("✅ Face detected")
    print("Detection confidence:", round(float(face.det_score), 3))
    print("Embedding size:", embedding.shape)

    return embedding


# -----------------------------
# Load both faces
# -----------------------------

embedding1 = get_embedding("test_face1.jpg")
embedding2 = get_embedding("test_face2.jpg")


# -----------------------------
# Cosine similarity
# -----------------------------

similarity = float(
    np.dot(embedding1, embedding2)
)

print("\n===================================")
print(" FACE SIMILARITY RESULT")
print("===================================")

print(
    "Cosine similarity:",
    round(similarity, 4)
)


# -----------------------------
# Simple interpretation
# -----------------------------

if similarity >= 0.5:
    result = "Potentially similar faces"
elif similarity >= 0.3:
    result = "Weak similarity"
else:
    result = "Likely different faces"

print("\nResult:", result)

print("\n===================================")
print("✅ SIMILARITY TEST COMPLETED")
print("===================================")