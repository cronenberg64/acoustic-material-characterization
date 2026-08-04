from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

class TapRecord(BaseModel):
    """
    Metadata schema for a single acoustic tap record.
    All data downstream depends on this schema being adhered to.
    """
    model_config = ConfigDict(strict=True)

    # Identifiers
    sample_id: str = Field(..., description="Unique identifier for the sample")
    material: str = Field(..., description="Material of the sample (e.g., 'PLA', 'PETG')")
    infill_pct: int = Field(..., description="Infill percentage of the printed sample (0-100)", ge=0, le=100)
    
    # Contact Parameters
    force_level: int = Field(..., description="Nominal tap force level (1-3)", ge=1, le=3)
    measured_peak_force_N: float | None = Field(None, description="Actual measured peak force from the load cell in Newtons")
    position_id: int = Field(..., description="Position ID of the tap on the sample (1-3)", ge=1, le=3)
    angle_deg: float = Field(..., description="Angle of the tap in degrees")
    tip_id: str = Field(..., description="Identifier for the tapper tip used")
    rep_index: int = Field(..., description="Repetition index for this specific condition", ge=0)
    timestamp: str = Field(..., description="ISO 8601 timestamp of the recording")
    
    # Audio Metadata
    waveform_path: str = Field(..., description="Relative path to the raw waveform file (.npy or .wav)")
    sample_rate_hz: int = Field(..., description="Sample rate of the recording in Hz", gt=0)
    
    # Ground Truth Properties
    density_kgm3: Optional[float] = None
    density_err_kgm3: float | None = Field(None, description="Uncertainty of the density measurement")
    youngs_modulus_pa: Optional[float] = None
    youngs_err_pa: float | None = Field(None, description="Uncertainty of the Young's Modulus measurement")

class ExternalAudioRecord(BaseModel):
    """
    Lightweight schema for externally-sourced audio (e.g., RealImpact).
    Kept strictly separated from experimental rig measurements to prevent contamination.
    """
    uid: str
    source_dataset: str
    material: str
    audio_path: str
    sample_rate_hz: int
    
    # RealImpact specific metadata (Optional, depending on dataset)
    object_id: Optional[str] = None
    contact_force_profile: Optional[list] = None
    impact_location: Optional[str] = None
