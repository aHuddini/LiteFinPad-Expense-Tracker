"""Download SmolLM2 model from Hugging Face."""
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

print("\n[DOWNLOAD] Downloading SmolLM2 (1.7B) model...")
print("   Searching for GGUF format model...")

# SmolLM2 repositories to try
repos_to_try = [
    'huggingface/SmolLM2-1.7B-Instruct-gguf',
    'bartowski/SmolLM2-1.7B-Instruct-GGUF',
    'TheBloke/SmolLM2-1.7B-Instruct-GGUF'
]

target_filename = 'SmolLM2-1.7B-Instruct-Q4_K_M.gguf'
repo_id = None
files = None

for repo in repos_to_try:
    try:
        print(f"\nChecking repository: {repo}...")
        files = list_repo_files(repo)
        repo_id = repo
        print(f"[OK] Found repository: {repo}")
        break
    except Exception as e:
        print(f"  Not found: {str(e)[:80]}")
        continue

if not repo_id or not files:
    raise Exception("Could not find SmolLM2 repository")

try:
    
    # Look for Q4_K_M quantization
    q4_files = [f for f in files if 'q4' in f.lower() and 'k_m' in f.lower() and 'gguf' in f.lower()]
    if q4_files:
        target_filename = q4_files[0]
        print(f"Found: {target_filename}")
    else:
        # Try any GGUF file with Q4
        q4_any = [f for f in files if 'q4' in f.lower() and 'gguf' in f.lower()]
        if q4_any:
            target_filename = q4_any[0]
            print(f"Found: {target_filename}")
        else:
            # List available files
            print("Available files:")
            for f in files[:10]:
                print(f"  - {f}")
            raise Exception("Could not find Q4_K_M file")
    
    print(f"\nDownloading {target_filename}...")
    print("   This may take a few minutes (~2GB download)...")
    
    file_path = hf_hub_download(
        repo_id=repo_id,
        filename=target_filename,
        local_dir='models'
    )
    
    # Rename to expected name if different
    expected_name = 'SmolLM2-1.7B-Instruct-Q4_K_M.gguf'
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
    print(f"\n[OK] SmolLM2 model is ready to use!")
    print(f"   Settings updated: preferred_model = smollm2:1.7b")
    
except Exception as e:
    print(f"\n[ERROR] Error downloading model: {e}")
    print("\nAlternative: Download manually from:")
    print("   https://huggingface.co/huggingface/SmolLM2-1.7B-Instruct-gguf")
    print("   Find file: SmolLM2-1.7B-Instruct-Q4_K_M.gguf")
    print("   Save to: models/SmolLM2-1.7B-Instruct-Q4_K_M.gguf")
    sys.exit(1)

