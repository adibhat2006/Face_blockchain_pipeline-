import cv2
import numpy as np
from insightface.app import FaceAnalysis

print("===================================")
print(" FaceChain - ArcFace Face Embedding")
print("===================================")

IMAGE_PATH = "test_face.jpg"

print("\nLoading ArcFace model...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

print("✅ Model loaded")


print("\nReading image...")

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise FileNotFoundError(
        f"Could not read image: {IMAGE_PATH}"
    )

print("✅ Image loaded")
print("Image size:", image.shape[1], "x", image.shape[0])


print("\nDetecting face...")

faces = app.get(image)

print("Faces detected:", len(faces))


if len(faces) == 0:
    print("\n❌ No face detected.")
    print("Try a clearer image with a visible face.")
    exit()


# Select the largest detected face
face = max(
    faces,
    key=lambda f: (f.bbox[2] - f.bbox[0]) *
                  (f.bbox[3] - f.bbox[1])
)


print("\n✅ Face detected!")

print("Bounding box:")
print(face.bbox)

print("\nFace detection score:")
print(face.det_score)


# ArcFace embedding
embedding = face.embedding

print("\n===================================")
print("ArcFace Embedding")
print("===================================")

print("Embedding type:", type(embedding))
print("Embedding shape:", embedding.shape)
print("Embedding length:", len(embedding))

print("\nFirst 10 embedding values:")
print(embedding[:10])


# Normalize embedding
normalized_embedding = embedding / np.linalg.norm(embedding)

print("\nNormalized embedding length:")
print(np.linalg.norm(normalized_embedding))


# Save embedding
np.save(
    "test_face_embedding.npy",
    normalized_embedding
)

print("\n✅ Embedding saved:")
print("test_face_embedding.npy")


print("\n===================================")
print("✅ FACE EMBEDDING TEST PASSED")
print("===================================")