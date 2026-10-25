from backend.assistant.assistant_service import answer_question


PREDICTION = {
    "predicted_class": "Patches",
    "raw_top_class": "Patches",
    "confidence": 0.91,
    "threshold": 0.5,
    "top_k": [{"class_name": "Patches", "confidence": 0.91}],
}


def test_general_question_does_not_repeat_camera_prediction(monkeypatch):
    monkeypatch.setenv("ASSISTANT_MODE", "dataset")
    answer = answer_question("What are the 6 steel surface defects?", PREDICTION)["answer"]
    assert "Prediction:" not in answer
    assert "There are 6 main defect classes" in answer
    assert "Steel is an iron-carbon alloy" not in answer


def test_explicit_other_defect_overrides_camera_prediction(monkeypatch):
    monkeypatch.setenv("ASSISTANT_MODE", "dataset")
    answer = answer_question("How can Inclusion defects be prevented?", PREDICTION)["answer"]
    assert "Prediction: Patches" not in answer
    assert "inclusion" in answer.lower()
    assert "Recommended actions" in answer
    assert "Most likely defect" not in answer


def test_prediction_question_includes_camera_result(monkeypatch):
    monkeypatch.setenv("ASSISTANT_MODE", "dataset")
    answer = answer_question("What was detected in the current prediction?", PREDICTION)["answer"]
    assert "Prediction: Patches (91.0%)" in answer
    assert "Local surface imperfections" not in answer


def test_referential_followup_uses_detected_label_without_repeating_score(monkeypatch):
    monkeypatch.setenv("ASSISTANT_MODE", "dataset")
    answer = answer_question("How can this defect be prevented?", PREDICTION)["answer"]
    assert "Prediction:" not in answer
    assert "patch" in answer.lower()


def test_spelled_number_catalog_question(monkeypatch):
    monkeypatch.setenv("ASSISTANT_MODE", "dataset")
    answer = answer_question("What are the six steel defects?")["answer"]
    assert "There are 6 main defect classes" in answer


def test_generic_defect_definition_does_not_guess_a_class(monkeypatch):
    monkeypatch.setenv("ASSISTANT_MODE", "dataset")
    answer = answer_question("What are defects?")["answer"]
    assert "A surface defect is" in answer
    assert "Most likely defect" not in answer


def test_scanner_question_returns_imaging_setup(monkeypatch):
    monkeypatch.setenv("ASSISTANT_MODE", "dataset")
    answer = answer_question("What kind of scanner is required to scan metal defects?")["answer"]
    assert "industrial area-scan camera" in answer
    assert "line-scan camera" in answer


def test_ambiguous_surface_identification_requests_clarification(monkeypatch):
    monkeypatch.setenv("ASSISTANT_MODE", "dataset")
    answer = answer_question("How to identify surface?")["answer"]
    assert "Please specify" in answer
    assert "Patches:" not in answer
