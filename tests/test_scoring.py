from assurance_lab.scoring import band, inherent_score, residual_score


def test_inherent_and_band():
    assert inherent_score("High", "Severe") == 12
    assert band(12) == "Critical"


def test_residual_reduces_for_effective_controls():
    assert residual_score(12, ["Effective", "Effective"]) == 1.8
    assert residual_score(12, ["Ineffective"]) == 12

