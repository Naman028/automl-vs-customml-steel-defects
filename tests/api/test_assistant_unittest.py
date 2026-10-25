import os
import unittest
from unittest.mock import patch


from backend.assistant.assistant_service import answer_question


PREDICTION = {
    "predicted_class": "Patches",
    "raw_top_class": "Patches",
    "confidence": 0.72,
    "threshold": 0.55,
    "top_k": [
        {"class_name": "Patches", "confidence": 0.72},
        {"class_name": "Crazing", "confidence": 0.18},
    ],
}


class AssistantBehaviorTests(unittest.TestCase):
    def ask(self, question, prediction=None):
        with patch.dict(os.environ, {"ASSISTANT_MODE": "dataset"}):
            return answer_question(question, prediction)["answer"]

    def test_catalog_with_spelled_number(self):
        answer = self.ask("What are the six steel defects?")
        self.assertIn("There are 6 main defect classes", answer)
        self.assertIn("Pitted Surface", answer)

    def test_generic_definition_does_not_guess(self):
        answer = self.ask("What is a steel surface defect?")
        self.assertIn("A surface defect is", answer)
        self.assertNotIn("Most likely defect", answer)

    def test_specific_defect_visual_answer(self):
        answer = self.ask("What is pitted surface?")
        self.assertIn("Pitted Surface: Visual cues", answer)

    def test_prevention_is_focused(self):
        answer = self.ask("How can scratches be prevented?")
        self.assertIn("Recommended actions", answer)
        self.assertNotIn("Likely root causes", answer)

    def test_severity_does_not_guess_class(self):
        answer = self.ask("Which defect is most severe?")
        self.assertIn("No defect class is always", answer)

    def test_scanner_guidance(self):
        answer = self.ask("What camera should I use to inspect defects?")
        self.assertIn("industrial area-scan camera", answer)
        self.assertIn("line-scan camera", answer)

    def test_lighting_guidance(self):
        answer = self.ask("What lighting is best for scratches?")
        self.assertIn("dark-field", answer)

    def test_upload_formats(self):
        answer = self.ask("What image format is accepted?")
        self.assertIn("JPEG/JPG, PNG, WebP, and BMP", answer)

    def test_metric_definitions(self):
        self.assertIn("TP / (TP + FP)", self.ask("What is precision?"))
        self.assertIn("TP / (TP + FN)", self.ask("What is recall?"))
        self.assertIn("harmonic mean", self.ask("What is F1 score?"))

    def test_out_of_scope_material(self):
        self.assertIn("not one of the six trained classes", self.ask("Can this detect rust?"))
        self.assertIn("not aluminum defects", self.ask("Can this detect aluminum defects?"))

    def test_human_inspector_limit(self):
        self.assertIn(
            "must not replace qualified inspection", self.ask("Can it replace a human inspector?")
        )

    def test_general_question_ignores_camera_prediction(self):
        answer = self.ask("What are the six steel defects?", PREDICTION)
        self.assertNotIn("Prediction:", answer)

    def test_explicit_other_defect_ignores_camera_label(self):
        answer = self.ask("How can Inclusion defects be prevented?", PREDICTION)
        self.assertIn("Inclusion: Recommended actions", answer)
        self.assertNotIn("Prediction: Patches", answer)

    def test_prediction_question_uses_camera_context(self):
        answer = self.ask("What was detected in the current prediction?", PREDICTION)
        self.assertIn("Prediction: Patches (72.0%)", answer)

    def test_referential_followup_uses_camera_label_without_repeating_score(self):
        answer = self.ask("How can this defect be prevented?", PREDICTION)
        self.assertIn("Patches: Recommended actions", answer)
        self.assertNotIn("Prediction:", answer)

    def test_ambiguous_surface_question_requests_clarification(self):
        answer = self.ask("How to identify surface?")
        self.assertIn("Please specify", answer)


if __name__ == "__main__":
    unittest.main()
