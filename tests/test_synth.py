import numpy as np
import librosa
from ame.synth.generator import generate_tap_waveform

def test_modal_frequencies_invariant():
    """Test that modal frequencies don't shift with contact parameters."""
    E = 3.5e9
    rho = 1240.0
    scale = 0.1
    
    # Condition 1: Force level 1, Pos 1
    wave1, freqs1 = generate_tap_waveform(E, rho, scale, force_level=1, position_id=1, angle_deg=0)
    
    # Condition 2: Force level 3, Pos 3
    wave2, freqs2 = generate_tap_waveform(E, rho, scale, force_level=3, position_id=3, angle_deg=10)
    
    # Underlying physical frequencies should be EXACTLY the same
    np.testing.assert_allclose(freqs1, freqs2)

def test_spectral_centroid_shifts():
    """Test that harder taps (higher force) have a higher spectral centroid."""
    E = 3.5e9
    rho = 1240.0
    scale = 0.1
    sr = 192000
    
    wave1, _ = generate_tap_waveform(E, rho, scale, force_level=1, position_id=1, angle_deg=0)
    wave3, _ = generate_tap_waveform(E, rho, scale, force_level=3, position_id=1, angle_deg=0)
    
    # Calculate spectral centroid
    centroid1 = librosa.feature.spectral_centroid(y=wave1, sr=sr).mean()
    centroid3 = librosa.feature.spectral_centroid(y=wave3, sr=sr).mean()
    
    # Force level 3 should have a higher centroid due to shorter contact time -> wider bandwidth
    assert centroid3 > centroid1
