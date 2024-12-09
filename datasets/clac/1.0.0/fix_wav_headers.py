import os
import audiofile


# Function to repair the header of a .wav file
def repair_wav_header(input_path, output_path):
    try:
        signal, sampling_rate = audiofile.read(input_path)
        audiofile.write(output_path, signal, sampling_rate)
        print(f"Fixed header for {input_path}")
    except Exception as e:
        print(f"Error fixing header for {input_path}: {e}")


# Recursively traverse the directory and its subdirectories
for root, _, files in os.walk('./audio'):
    for file in files:
        if file.endswith(".wav"):
            input_path = os.path.join(root, file)
            repair_wav_header(input_path, input_path)
