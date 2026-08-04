import pytest
from pydantic import ValidationError
from ame.schema import TapRecord

def test_valid_tap_record():
    record = TapRecord(
        sample_id="PLA_20_1",
        material="PLA",
        infill_pct=20,
        force_level=2,
        measured_peak_force_N=15.5,
        position_id=1,
        angle_deg=0.0,
        tip_id="steel_ball",
        rep_index=0,
        timestamp="2026-07-30T10:00:00Z",
        waveform_path="data/raw/PLA_20_1/uuid1.wav",
        sample_rate_hz=192000,
        density_kgm3=1240.5,
        density_err_kgm3=5.0,
        youngs_modulus_pa=3.5e9,
        youngs_err_pa=0.1e9
    )
    assert record.sample_id == "PLA_20_1"

def test_invalid_tap_record():
    with pytest.raises(ValidationError):
        TapRecord(
            sample_id="PLA_20_1",
            material="PLA",
            infill_pct=150, # invalid, > 100
            force_level=2,
            measured_peak_force_N=15.5,
            position_id=1,
            angle_deg=0.0,
            tip_id="steel_ball",
            rep_index=0,
            timestamp="2026-07-30T10:00:00Z",
            waveform_path="data/raw/PLA_20_1/uuid1.wav",
            sample_rate_hz=192000
        )
