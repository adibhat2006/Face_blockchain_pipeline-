import sys

print("=== InsightFace / ArcFace Compatibility Test ===")

print("\nPython version:")
print(sys.version)

# Test ONNX Runtime
try:
    import onnxruntime as ort

    print("\nONNX Runtime:")
    print("Version:", ort.__version__)
    print("Providers:", ort.get_available_providers())

except Exception as e:
    print("\n❌ ONNX Runtime FAILED")
    print(e)
    sys.exit(1)


# Test InsightFace
try:
    import insightface

    print("\nInsightFace:")
    print("Version:", insightface.__version__)
    print("Import: SUCCESS")

except Exception as e:
    print("\n❌ InsightFace IMPORT FAILED")
    print(e)
    sys.exit(1)


# Test ArcFace
try:
    from insightface.model_zoo.arcface_onnx import ArcFaceONNX

    print("\nArcFace:")
    print("ArcFaceONNX import: SUCCESS")

except Exception as e:
    print("\n❌ ArcFace IMPORT FAILED")
    print(e)
    sys.exit(1)


print("\n===================================")
print("✅ Python 3.14 + InsightFace + ArcFace")
print("   compatibility test PASSED")
print("===================================")