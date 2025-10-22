from deepgram import DeepgramClient, PrerecordedOptions
import os
import time
import glob

# Put your Deepgram API key here
API_KEY = "8f5b731f2b70da048a7d53896517ba86aed00927"

# Initialize Deepgram
deepgram = DeepgramClient(API_KEY)

def transcribe_and_export(audio_file_path, output_file_path):
    try:
        print(f"📞 Processing: {os.path.basename(audio_file_path)}")
        
        # Check file size
        file_size = os.path.getsize(audio_file_path) / (1024 * 1024)  # Size in MB
        print(f"   File size: {file_size:.2f} MB")
        
        # Transcribe the audio
        with open(audio_file_path, "rb") as file:
            buffer_data = file.read()

        payload = {"buffer": buffer_data}
        
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            punctuate=True,
            diarize=True,
            language="hi"
        )
        
        print("   Sending to Deepgram API...")
        start_time = time.time()
        
        # Use the rest API (this worked in your original code)
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        
        end_time = time.time()
        print(f"   API call completed in {end_time - start_time:.2f} seconds")
        
        # Extract conversation in terminal format
        conversation_lines = []
        
        if hasattr(response, 'results') and response.results['channels']:
            paragraphs = response.results['channels'][0]['alternatives'][0]['paragraphs']['paragraphs']
            
            for paragraph in paragraphs:
                speaker_id = paragraph['speaker']
                
                # Combine all sentences from this speaker segment
                full_text = ""
                for sentence in paragraph['sentences']:
                    full_text += sentence['text'] + " "
                
                # Add to conversation in simple format
                conversation_lines.append(f"User {speaker_id}: {full_text.strip()}")
        
        # Save to text file (not JSON)
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(f"Call Recording: {os.path.basename(audio_file_path)}\n")
            f.write("="*50 + "\n\n")
            
            for line in conversation_lines:
                f.write(line + "\n\n")
        
        print(f"   ✅ Saved to: {os.path.basename(output_file_path)}")
        print(f"   Total exchanges: {len(conversation_lines)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def process_all_files():
    # Your audio files folder - UPDATED PATH FOR SYMPHONY
    audio_folder = "/home/vedanta-hatti/Downloads/Symphony - calls-20251021T133532Z-1-001/Symphony - calls"
    
    # Create output folder for transcripts
    output_folder = os.path.join(audio_folder, "transcripts")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Created output folder: {output_folder}")
    
    # Get all MP3 files
    mp3_files = glob.glob(os.path.join(audio_folder, "*.mp3"))
    
    if not mp3_files:
        print("❌ No MP3 files found! Please check the folder path.")
        return
    
    print(f"🎵 Found {len(mp3_files)} MP3 files to process")
    print("="*60)
    
    successful = 0
    failed = 0
    
    for i, audio_file in enumerate(mp3_files, 1):
        print(f"\n[{i}/{len(mp3_files)}] Starting transcription...")
        
        # Create output filename
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        output_file = os.path.join(output_folder, f"{base_name}_transcript.txt")
        
        # Skip if already processed
        if os.path.exists(output_file):
            print(f"   ⏭️  Already exists, skipping: {base_name}_transcript.txt")
            successful += 1
            continue
        
        # Process the file
        success = transcribe_and_export(audio_file, output_file)
        
        if success:
            successful += 1
        else:
            failed += 1
        
        # Small delay between API calls to be nice to the API
        if i < len(mp3_files):  # Don't sleep after the last file
            print("   ⏳ Waiting 2 seconds before next file...")
            time.sleep(2)
    
    print("\n" + "="*60)
    print("🎉 PROCESSING COMPLETE!")
    print(f"✅ Successfully processed: {successful} files")
    print(f"❌ Failed: {failed} files")
    print(f"📂 All transcripts saved in: {output_folder}")

# Run the script
if __name__ == "__main__":
    print("🚀 Starting batch transcription of Symphony call recordings...")
    process_all_files()