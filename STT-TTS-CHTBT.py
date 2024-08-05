import pyaudio
import wave
from openai import OpenAI

client = OpenAI()

def record_audio():
    # Set up audio recording parameters
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 10
    WAVE_OUTPUT_FILENAME = "output.wav"

    # Create a PyAudio object
    p = pyaudio.PyAudio()

    # Open the microphone stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")

    # Initialize an empty list to store the audio frames
    frames = []

    # Record audio for RECORD_SECONDS
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    # Close the microphone stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio to a WAV file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return WAVE_OUTPUT_FILENAME

def transcribe_audio(file_path):
    audio_file = open(file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    print(transcription.text)

def send_message(message_log):
    
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
        {"role": "user", "content": message_log}
        ]  
    )

    # If no response with text is found, return the first response's content (which may be empty)
    return completion.choices[0].message.content

def text_to_speech(text_input, filename):
    """Convert text to speech and save to a file."""
    model = 'tts-1'
    voice = 'alloy'

    response = client.audio.speech.create(
        model= model,
        input= text_input,
        voice= voice
    )

    response.write_to_file(filename)
    print("Speech saved to", filename)

def main():
    while True:
        print("\nOpenAI assistant \nPlease choose a service:")
        print("1. Start the chatbot")
        print("2. Convert text to speech")
        print("3. Speech to text")
        print("4. Quit")

        choice = input("Enter your choice (1/2/3/4): ")

        if choice == "1":
            print("Welcome to the chatbot! Type 'quit' to exit the chatbot.")
            while True:
                user_input = input("You: ")
                
                if user_input.lower() == "quit":
                    print("Goodbye! \nReturning to the main menu.")
                    break

                response = send_message(user_input)
                print(f"AI assistant: {response}")
        elif choice == "2":
            print("Options:")
            print("1. Enter text")
            print("2. Read from file")
            text_choice = input("Enter your choice: ")

            if text_choice == "1":
                text_input = input("Please enter the text you want to convert to speech: ")
                filename = input("Enter the filename (e.g. test.mp3): ")
                text_to_speech(text_input, filename)

            elif text_choice == "2":
                filename_text = input("Enter the filename of the text file (e.g. text.txt): ")
                file_path = input("Enter the path to your text file: ")
                with open(file_path, 'r') as file:
                    text_input = file.read()
                filename = input("Enter the filename (e.g. test.mp3): ")
                text_to_speech(text_input, filename)
            else:
                print("Invalid choice. Please try again.")

        elif choice == "3":
            print("Options:")
            print("1. Upload a voice file")
            print("2. Use the microphone")
            print("3. Return to main menu")

            speech_choice = input("Enter your choice: ")

            if speech_choice == "1":
                file_path = input("Enter the path to your voice file: ")
                transcribe_audio(file_path)
            elif speech_choice == "2":
                file_path = record_audio()
                transcribe_audio(file_path)
            elif speech_choice == "3":
                continue
            else:
                print("Invalid choice. Please try again.")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()