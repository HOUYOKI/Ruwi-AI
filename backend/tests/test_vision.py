import json
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from vision.identify import (
    VisionProviderError,
    VisionResponseError,
    get_showcase_candidates,
    identify_artifact,
    normalize_provider_result,
)
from vision.routes import MAX_IMAGE_BYTES, create_vision_router
from vision.schemas import IdentificationResponse


ROOT = Path(__file__).resolve().parents[2]
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"valid-image-content"


def load_artifacts():
    records = json.loads((ROOT / "data" / "artifacts.json").read_text(encoding="utf-8"))
    return {record["id"]: record for record in records}


class VisionNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = load_artifacts()
        cls.candidates = get_showcase_candidates(cls.artifacts)

    def test_valid_matched_response(self):
        result = normalize_provider_result({
            "artifact_id": 46,
            "confidence": 0.93,
            "reason": "A thin gold facial mask with edge holes.",
            "alternatives": [],
        }, self.candidates)
        self.assertEqual(result.status, "matched")
        self.assertEqual(result.artifact_id, 46)

    def test_partial_response_requires_confirmation(self):
        result = normalize_provider_result({
            "artifact_id": 46,
            "confidence": 0.62,
            "reason": "The face is similar, but the image is unclear.",
            "alternatives": [],
        }, self.candidates)
        self.assertEqual(result.status, "partial")
        self.assertIsNone(result.artifact_id)
        self.assertEqual(result.alternatives[0].artifact_id, 46)

    def test_low_confidence_is_unsupported(self):
        result = normalize_provider_result({
            "artifact_id": 46,
            "confidence": 0.18,
            "reason": "There is too little visual evidence.",
            "alternatives": [],
        }, self.candidates)
        self.assertEqual(result.status, "unsupported")
        self.assertIsNone(result.artifact_id)
        self.assertEqual(result.alternatives, [])

    def test_invalid_model_artifact_id_is_rejected(self):
        with self.assertRaises(VisionResponseError):
            normalize_provider_result({
                "artifact_id": 999,
                "confidence": 0.99,
                "reason": "Invalid ID",
                "alternatives": [],
            }, self.candidates)

    def test_malformed_provider_response_is_rejected(self):
        with self.assertRaises(VisionResponseError):
            normalize_provider_result({"unexpected": True}, self.candidates)

    def test_provider_failure_is_controlled(self):
        def failed_provider(*_args):
            raise TimeoutError("provider timed out")

        with self.assertRaises(VisionProviderError):
            identify_artifact(PNG_BYTES, "image/png", self.artifacts, failed_provider)

    def test_candidates_come_only_from_showcase_overlay(self):
        candidate_ids = {candidate["artifact_id"] for candidate in self.candidates}
        self.assertEqual(candidate_ids, {6, 14, 18, 43, 46, 79})

    def test_existing_artifact_46_remains_matchable_after_expansion(self):
        result = normalize_provider_result({
            "artifact_id": 46,
            "confidence": 0.91,
            "reason": "The photograph shows the supported gold facial mask.",
            "alternatives": [{"artifact_id": 43, "confidence": 0.22}],
        }, self.candidates)
        self.assertEqual(result.status, "matched")
        self.assertEqual(result.artifact_id, 46)
        self.assertEqual(result.alternatives[0].artifact_id, 43)

    def test_invalid_alternative_artifact_id_is_rejected(self):
        with self.assertRaises(VisionResponseError):
            normalize_provider_result({
                "artifact_id": 46,
                "confidence": 0.9,
                "reason": "Strong match.",
                "alternatives": [
                    {"artifact_id": 999, "confidence": 0.2}
                ],
            }, self.candidates)


class VisionRouteValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        artifacts = load_artifacts()

        def matched_identifier(_content, _mime_type, _artifacts):
            return IdentificationResponse(
                status="matched",
                artifact_id=46,
                artifact_name=artifacts[46]["name"],
                confidence=0.93,
                reason="Matched in a test provider.",
                alternatives=[],
            )

        app = FastAPI()
        app.include_router(create_vision_router(artifacts, matched_identifier))
        cls.client = TestClient(app)

    def test_empty_upload(self):
        response = self.client.post("/identify", files={"file": ("empty.png", b"", "image/png")})
        self.assertEqual(response.status_code, 400)

    def test_unsupported_mime_type(self):
        response = self.client.post("/identify", files={"file": ("artifact.gif", b"GIF89a", "image/gif")})
        self.assertEqual(response.status_code, 415)

    def test_oversized_image(self):
        content = b"\x89PNG\r\n\x1a\n" + b"0" * MAX_IMAGE_BYTES
        response = self.client.post("/identify", files={"file": ("large.png", content, "image/png")})
        self.assertEqual(response.status_code, 413)

    def test_valid_upload_reaches_identifier(self):
        response = self.client.post("/identify", files={"file": ("mask.png", PNG_BYTES, "image/png")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["artifact_id"], 46)

        


if __name__ == "__main__":
    unittest.main()
