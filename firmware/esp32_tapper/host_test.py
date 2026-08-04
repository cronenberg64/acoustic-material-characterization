import serial
import time
import json
import argparse

def test_commands(port: str, baud: int = 115200):
    print(f"Connecting to ESP32 on {port} at {baud} baud...")
    try:
        esp = serial.Serial(port, baud, timeout=2)
        time.sleep(2) # Wait for ESP32 to reset upon serial connection
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # Flush initial ready message
    while esp.in_waiting:
        print("Init:", esp.readline().decode().strip())

    commands = [
        "ID",
        "STATUS",
        "TARE",
        "READ_FORCE",
        "SET_PW 12000",
        "TAP 1",
        "TAP 2",
        "TAP 3"
    ]

    for cmd in commands:
        print(f"\nSending: {cmd}")
        esp.write((cmd + "\n").encode())
        
        # Wait for response
        start = time.time()
        response_received = False
        while time.time() - start < 2.0:
            if esp.in_waiting:
                line = esp.readline().decode().strip()
                print(f"Received: {line}")
                
                try:
                    data = json.loads(line)
                    if "error" in data:
                        print("-> ERROR parsed from JSON")
                except json.JSONDecodeError:
                    print("-> Invalid JSON")
                    
                response_received = True
                break
            time.sleep(0.01)
            
        if not response_received:
            print("Timeout waiting for response!")
            
        time.sleep(0.6) # Wait for inter-tap timeout to clear
        
    esp.close()
    print("\nTest complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port of ESP32")
    args = parser.parse_args()
    
    test_commands(args.port)
