import os
import uuid
import datetime
import time
import argparse
import numpy as np
import pandas as pd
import soundfile as sf
import serial
from typing import Dict, Any

from ame.schema import TapRecord
from ame.synth.generator import generate_tap_waveform

try:
    from pydwf import DwfLibrary, DwfEnumConfigInfo, DwfAcquisitionMode, DwfTriggerSource, DwfTriggerSlope
except ImportError:
    pass

class DAQMock:
    """Mock DAQ using the synthetic generator."""
    def __init__(self, sample_rate: int = 192000, duration: float = 0.3):
        self.sample_rate = sample_rate
        self.duration = duration
        
    def configure(self):
        print("Mock DAQ configured.")
        
    def wait_for_trigger_and_read(self) -> np.ndarray:
        print("Mock DAQ triggered. Generating synthetic wave...")
        time.sleep(0.1) # Simulate acquisition time
        # Return a synthetic tap wave
        wave, _ = generate_tap_waveform(
            youngs_modulus=3.5e9, 
            density=1240.0, 
            geometry_scale=0.1, 
            force_level=2, 
            position_id=1, 
            angle_deg=0.0,
            sr=self.sample_rate,
            duration=self.duration
        )
        return wave
        
class DAQHardware:
    """Real DAQ interfacing with Analog Discovery 3 via pydwf."""
    def __init__(self, sample_rate: int = 1000000, duration: float = 0.3):
        self.sample_rate = sample_rate
        self.duration = duration
        self.num_samples = int(self.sample_rate * self.duration)
        self.dwf = DwfLibrary()
        self.device = None
        
    def configure(self):
        # Open first available device
        self.device = self.dwf.deviceControl.open(-1)
        self.ain = self.device.analogIn
        
        # Configure channels
        self.ain.channelEnableSet(0, True) # Piezo
        self.ain.channelEnableSet(1, True) # Trigger from ESP32
        
        self.ain.channelRangeSet(0, 5.0) # +/- 5V
        self.ain.channelRangeSet(1, 5.0)
        
        # Acquisition
        self.ain.acquisitionModeSet(DwfAcquisitionMode.Record)
        self.ain.frequencySet(float(self.sample_rate))
        self.ain.recordLengthSet(self.duration)
        
        # Trigger on Channel 1 (ESP32 pulse) rising edge
        self.ain.triggerSourceSet(DwfTriggerSource.DetectorAnalogIn)
        self.ain.triggerChannelSet(1)
        self.ain.triggerLevelSet(2.0) # 2V threshold
        self.ain.triggerConditionSet(DwfTriggerSlope.Rise)
        
        # Pre-trigger 10ms
        self.ain.triggerPositionSet(0.01)
        
    def wait_for_trigger_and_read(self) -> np.ndarray:
        self.ain.configure(False, True)
        
        while True:
            status = self.ain.status(True)
            if status == 2: # DwfStateDone
                break
            time.sleep(0.001)
            
        data = self.ain.statusData(0, self.num_samples)
        return np.array(data)
        
    def close(self):
        if self.device:
            self.device.close()


def check_signal_quality(waveform: np.ndarray, max_val: float = 5.0) -> bool:
    """Quality checks: clipping, flat-line, SNR."""
    if np.all(waveform == waveform[0]):
        print("ERROR: Flat-line detected in signal.")
        return False
        
    if np.max(np.abs(waveform)) >= (max_val - 0.05):
        print("ERROR: Clipping detected.")
        return False
        
    rms = np.sqrt(np.mean(waveform**2))
    peak = np.max(np.abs(waveform))
    if peak / rms < 2.0: # Very low crest factor means it might be mostly noise
        print("ERROR: Low SNR detected (mostly noise).")
        return False
        
    return True

def record_tap(daq, esp_serial: serial.Serial, metadata: dict, output_dir: str) -> TapRecord:
    if esp_serial:
        esp_serial.write(f"TAP {metadata['force_level']}\n".encode())
    
    waveform = daq.wait_for_trigger_and_read()
    
    if not check_signal_quality(waveform):
        raise RuntimeError("Signal quality check failed. Aborting collection.")
        
    sample_dir = os.path.join(output_dir, metadata['sample_id'])
    os.makedirs(sample_dir, exist_ok=True)
    
    uid = str(uuid.uuid4())
    fpath = os.path.join(sample_dir, f"{uid}.wav")
    sf.write(fpath, waveform, metadata['sample_rate_hz'])
    
    metadata['waveform_path'] = fpath
    metadata['timestamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    metadata['measured_peak_force_N'] = metadata['force_level'] * 5.0 # Mocked for now
    
    return TapRecord(**metadata)

def run_session(config: Dict[str, Any], mock: bool = False):
    out_dir = config.get("output_dir", "data/raw")
    os.makedirs(out_dir, exist_ok=True)
    
    if mock:
        daq = DAQMock(sample_rate=192000)
        esp = None
    else:
        daq = DAQHardware(sample_rate=192000)
        esp = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        
    daq.configure()
    
    samples = config.get("samples", ["PLA_30_1"])
    forces = config.get("forces", [1, 2, 3])
    positions = config.get("positions", [1, 2, 3])
    reps = config.get("reps", 5)
    
    records = []
    
    try:
        for sample in samples:
            input(f"Operator: Please mount sample {sample} and press Enter...")
            
            for pos in positions:
                input(f"Operator: Adjust tapper to position {pos} and press Enter...")
                
                for force in forces:
                    for rep in range(reps):
                        print(f"Recording {sample} | Pos: {pos} | Force: {force} | Rep: {rep+1}/{reps}")
                        
                        meta = {
                            "sample_id": sample,
                            "material": sample.split("_")[0],
                            "infill_pct": int(sample.split("_")[1]),
                            "force_level": force,
                            "position_id": pos,
                            "angle_deg": 0.0,
                            "tip_id": "standard",
                            "rep_index": rep,
                            "sample_rate_hz": 192000,
                            "density_kgm3": None,
                            "youngs_modulus_pa": None
                        }
                        
                        record = record_tap(daq, esp, meta, out_dir)
                        records.append(record.model_dump())
                        
                        time.sleep(0.5) # Inter-tap interval
    except KeyboardInterrupt:
        print("\nSession aborted by user.")
    finally:
        if not mock:
            daq.close()
            esp.close()
            
        if records:
            df = pd.DataFrame(records)
            df.to_csv(os.path.join(out_dir, "metadata_session.csv"), index=False)
            print(f"Saved {len(records)} records.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without hardware")
    args = parser.parse_args()
    
    cfg = {
        "output_dir": "data/session_1",
        "samples": ["PLA_30_1", "PETG_50_1"],
        "forces": [1, 2],
        "positions": [1, 2],
        "reps": 2
    }
    run_session(cfg, mock=args.mock)
