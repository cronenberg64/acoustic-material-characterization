import time
import argparse
import pandas as pd
import serial
from typing import List

def run_calibration_sweep(esp_port: str = '/dev/ttyUSB0', baud: int = 115200, 
                          pulse_widths_us: List[int] = None, reps: int = 5):
    """
    Sweeps solenoid pulse widths and records the peak impact force (or preload)
    to generate a calibration curve.
    """
    if pulse_widths_us is None:
        pulse_widths_us = list(range(1000, 10001, 1000))
        
    print(f"connecting to esp32 on {esp_port}...")
    try:
        esp = serial.Serial(esp_port, baud, timeout=2)
        time.sleep(2) # wait for reset
    except Exception as e:
        print(f"failed to connect: {e}")
        print("running in mock mode. results will be synthetic.")
        esp = None
        
    results = []
    
    for pw in pulse_widths_us:
        for rep in range(reps):
            print(f"testing pulse width: {pw} us | rep {rep+1}/{reps}")
            
            if esp:
                esp.write(f"SET_PW {pw}\n".encode())
                time.sleep(0.1)
                esp.write(b"TAP 1\n") # Force level 1 is generic tap
                
                # Wait for response (JSON with measured force)
                response = esp.readline().decode().strip()
                # Assuming JSON contains "peak_force": X
                import json
                try:
                    data = json.loads(response)
                    force = data.get("peak_force", 0.0)
                except Exception:
                    force = 0.0
            else:
                # Mock force ~ linear to pulse width
                force = (pw / 10000.0) * 20.0 + (rep * 0.1)
                
            results.append({
                "pulse_width_us": pw,
                "rep": rep,
                "measured_force_N": force
            })
            
            time.sleep(0.5) # cooling
            
    df = pd.DataFrame(results)
    df.to_csv("force_calibration.csv", index=False)
    
    # Calculate means
    means = df.groupby("pulse_width_us")["measured_force_N"].mean().reset_index()
    print("\ncalibration summary:")
    print(means)
    
    # Simple interpolation to find 5N, 10N, 15N
    target_forces = [5.0, 10.0, 15.0]
    print("\nrecommended pulse widths:")
    for target in target_forces:
        # linear interpolation
        pw_interp = np.interp(target, means["measured_force_N"], means["pulse_width_us"]) if esp is None else 0 # Mock
        print(f"target force: {target} n -> pulse width: ~{int(pw_interp)} us")
        
    if esp:
        esp.close()

if __name__ == "__main__":
    import numpy as np # for interp
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="/dev/ttyUSB0")
    args = parser.parse_args()
    
    run_calibration_sweep(esp_port=args.port)
