"""Download Gemma 3 model from Hugging Face."""
import os
import sys

try:
    from huggingface_hub import hf_hub_download, list_repo_files
    print("[OK] huggingface_hub is available")
except ImportError:
    print("Installing huggingface_hub...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub", "-q"])
    from huggingface_hub import hf_hub_download, list_repo_files
    print("[OK] huggingface_hub installed")

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

print("\n[DOWNLOAD] Downloading Gemma 1B model...")
print("   Searching for GGUF format model...")

# Try to find the correct repository and file
repos_to_try = [
    ('bartowski/gemma-1b-it-GGUF', None),  # Common GGUF conversion
    ('google/gemma-1b-it', None),  # Original (may not have GGUF)
]

file_path = None
filename = None

for repo_id, _ in repos_to_try:
    try:
        print(f"\nChecking repository: {repo_id}...")
        files = list_repo_files(repo_id)
        
        # Look for Q4_K_M quantization
        q4_files = [f for f in files if 'q4' in f.lower() and 'k_m' in f.lower() and 'gguf' in f.lower()]
        if q4_files:
            filename = q4_files[0]
            print(f"Found: {filename}")
            break
        else:
            # Try any GGUF file
            gguf_files = [f for f in files if 'gguf' in f.lower()]
            if gguf_files:
                # Prefer Q4_K_M, then any Q4, then any
                for pref in ['q4_k_m', 'q4', 'q5_k_m', 'q8_0']:
                    for f in gguf_files:
                        if pref in f.lower():
                            filename = f
                            break
                    if filename:
                        break
                if not filename:
                    filename = gguf_files[0]
                print(f"Found: {filename}")
                break
    except Exception as e:
        print(f"  Error checking {repo_id}: {str(e)[:80]}")
        continue

if not filename:
    print("\n[ERROR] Could not find Gemma GGUF model automatically.")
    print("\nPlease download manually:")
    print("1. Visit: https://huggingface.co/bartowski/gemma-1b-it-GGUF")
    print("2. Find file: gemma-1b-it-q4_k_m.gguf (or similar)")
    print("3. Download and save to: models/gemma-1b-it-q4_k_m.gguf")
    sys.exit(1)

# Download the file
try:
    print(f"\nDownloading {filename} from {repo_id}...")
    print("   This may take a few minutes (~1.7GB download)...")
    
    file_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir='models'
    )
    
    # Rename to expected name if different
    expected_name = 'gemma-1b-it-q4_k_m.gguf'
    expected_path = os.path.join('models', expected_name)
    if file_path != expected_path and os.path.exists(file_path):
        if os.path.exists(expected_path):
            os.remove(expected_path)  # Remove old file if exists
        os.rename(file_path, expected_path)
        file_path = expected_path
        print(f"Renamed to: {expected_name}")
    
    # Get file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    print(f"\n[SUCCESS] Download complete!")
    print(f"   File: {file_path}")
    print(f"   Size: {file_size_mb:.2f} MB")
    print(f"\n[OK] Gemma 1B model is ready to use!")
    print(f"   Settings already updated: preferred_model = gemma:1b")
    
except Exception as e:
    print(f"\n[ERROR] Error downloading model: {e}")
    print("\nAlternative: Download manually from:")
    print("   https://huggingface.co/bartowski/gemma-1b-it-GGUF")
    print("   Save to: models/gemma-1b-it-q4_k_m.gguf")
    sys.exit(1)
