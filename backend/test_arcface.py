import cv2
import numpy as np
from insightface.app import FaceAnalysis

print("===================================")
print("   FaceChain ArcFace Model Test")
print("===================================")

print("\nLoading ArcFace model: buffalo_l")
print("The first run may download the model...")

try:
    app = FaceAnalysis(
        name="buffalo_l",
        providers=["CPUExecutionProvider"]
    )

    app.prepare(ctx_id=0, det_size=(640, 640))

    print("\n✅ ArcFace model loaded successfully!")

except Exception as e:
    print("\n❌ Failed to load ArcFace model")
    print("Error:")
    print(e)
    raise


# Create a simple blank test image
test_image = np.zeros((640, 640, 3), dtype=np.uint8)

print("\nTesting model with a blank image...")

try:
    faces = app.get(test_image)

    print("Model inference: SUCCESS")
    print("Faces detected:", len(faces))

except Exception as e:
    print("\n❌ Model inference failed")
    print("Error:")
    print(e)
    raise


print("\n===================================")
print("✅ ArcFace model test PASSED")
print("===================================")