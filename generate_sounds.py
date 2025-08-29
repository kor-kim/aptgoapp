#!/usr/bin/env python3
"""
Generate sound files for the Android ANPR app
"""
import numpy as np
import wave
import struct

def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
    """Generate a sine wave with specified frequency and duration"""
    frames = int(duration * sample_rate)
    wavedata = b""
    
    for i in range(frames):
        wave_value = amplitude * np.sin(2 * np.pi * frequency * i / sample_rate)
        data = struct.pack('<f', wave_value)
        wavedata += data
        
    return wavedata, frames, sample_rate

def create_success_sound():
    """Create success sound - 띠리링 (rising tone)"""
    sample_rate = 44100
    
    # 띠리링 - three ascending tones
    tone1 = generate_sine_wave(800, 0.2, sample_rate, 0.3)  # 띠
    tone2 = generate_sine_wave(1000, 0.2, sample_rate, 0.3)  # 리
    tone3 = generate_sine_wave(1200, 0.3, sample_rate, 0.3)  # 링 (longer)
    
    # Combine the tones
    combined_data = tone1[0] + tone2[0] + tone3[0]
    total_frames = tone1[1] + tone2[1] + tone3[1]
    
    # Write to WAV file
    with wave.open('/Users/dragonship/파이썬/aptgoapp/app/src/main/res/raw/success_beep.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(4)  # 32-bit float
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(combined_data)
    
    print("✅ Success sound created: success_beep.wav")

def create_warning_sound():
    """Create warning sound - 띠띠띠 (buzzer)"""
    sample_rate = 44100
    
    # 띠띠띠 - three sharp beeps
    beep_data = b""
    
    for i in range(3):  # 3 beeps
        tone_data = generate_sine_wave(400, 0.15, sample_rate, 0.4)[0]  # Lower, sharper tone
        silence_data = generate_sine_wave(0, 0.05, sample_rate, 0)[0]   # Brief silence
        beep_data += tone_data + silence_data
    
    total_frames = len(beep_data) // 4  # 4 bytes per float32 sample
    
    # Write to WAV file  
    with wave.open('/Users/dragonship/파이썬/aptgoapp/app/src/main/res/raw/warning_alarm.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(4)  # 32-bit float
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(beep_data)
    
    print("✅ Warning sound created: warning_alarm.wav")

if __name__ == "__main__":
    print("🔊 Generating sound files for ANPR app...")
    try:
        create_success_sound()
        create_warning_sound()
        print("🎉 All sound files generated successfully!")
    except Exception as e:
        print(f"❌ Error generating sound files: {e}")