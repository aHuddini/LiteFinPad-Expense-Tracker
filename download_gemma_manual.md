# Manual Download Instructions for Gemma 1B

Since automatic download requires authentication, please follow these steps:

## Option 1: Download from Hugging Face (Recommended)

1. **Visit the repository**:
   - Go to: https://huggingface.co/bartowski/gemma-1b-it-GGUF
   - Or search for "gemma-1b-it GGUF" on Hugging Face

2. **Find the Q4_K_M file**:
   - Click "Files and versions" tab
   - Look for: `gemma-1b-it-q4_k_m.gguf` (~1.7GB)
   - Or any file with "q4_k_m" in the name

3. **Download**:
   - Click the download button
   - Save to: `C:\Users\asad2\OneDrive\Documents\LiteFinPad\models\`
   - Rename to: `gemma-1b-it-q4_k_m.gguf` (if different)

## Option 2: Use Hugging Face CLI (if authenticated)

```bash
huggingface-cli download bartowski/gemma-1b-it-GGUF gemma-1b-it-q4_k_m.gguf --local-dir models
```

## Option 3: Direct Download URL

If you have a direct download link, you can use:

```powershell
# In PowerShell
Invoke-WebRequest -Uri "DIRECT_DOWNLOAD_URL" -OutFile "models\gemma-1b-it-q4_k_m.gguf"
```

## Verification

After downloading, verify the file:
- Location: `models/gemma-1b-it-q4_k_m.gguf`
- Size: ~1.7GB (1,700-1,800 MB)
- Extension: `.gguf`

## Next Steps

Once downloaded:
1. Restart the application
2. The app will automatically detect Gemma 1B
3. Test with AI Chat queries

