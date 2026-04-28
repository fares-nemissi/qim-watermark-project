# QIM Watermark Project

This project hides an invisible binary watermark inside a grayscale image using:

- `DCT` (Discrete Cosine Transform)
- `QIM` (Quantization Index Modulation)

It also tests robustness with:

- Gaussian noise
- JPEG compression

Then it measures:

- `PSNR` for image quality
- `BER` for watermark extraction accuracy

## Files

- `main.py`: runs the whole demo
- `watermark.py`: watermark generation, embedding, and extraction
- `attacks.py`: image attacks
- `metrics.py`: PSNR and BER
- `images/host.png`: input image
- `results/`: generated outputs

## Very Simple VS Code Steps

1. Open the folder `qim-watermark-project` in Visual Studio Code.
2. On the top menu, click `Terminal`.
3. Click `New Terminal`.
4. In the terminal, activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

5. Install the libraries:

```powershell
pip install -r requirements.txt
```

6. Run the project:

```powershell
python main.py
```

7. Open the `results` folder to see:

- `watermarked.png`
- `attacked_noise.png`
- `attacked_jpeg.png`
- `watermark_reference.png`
- `extracted_clean.png`
- `extracted_noise.png`
- `extracted_jpeg.png`
- `report.txt`

## What the Program Does

1. Reads `images/host.png`
2. Crops it slightly so the size matches `8x8` blocks
3. Creates a random `16x16` binary watermark
4. Selects image blocks using a secret key
5. Inserts each watermark bit into several middle-frequency DCT coefficient pairs with QIM
6. Rebuilds the image
7. Applies noise and JPEG attacks
8. Extracts the watermark again
9. Calculates PSNR and BER

## Run With Custom Settings

```powershell
python main.py --input images/host.png --watermark-size 16 --delta 20 --key 1234 --repetitions 12 --noise-sigma 0.25 --jpeg-quality 80
```

## Useful Notes

- Bigger `delta` usually improves robustness but can reduce image quality.
- More `repetitions` usually improves robustness but uses more image blocks.
- Lower JPEG quality usually makes extraction harder.
- Stronger Gaussian noise can increase BER very quickly.
- Lower BER is better.
- Higher PSNR is better.

## GitHub And Docker

This project is also ready for:

- Git version control
- GitHub repository hosting
- Docker image packaging
- GitHub Actions CI/CD
- Optional Azure Web App deployment

Important files:

- `.gitignore`
- `Dockerfile`
- `.github/workflows/ci-cd.yml`
- `tests/test_watermark_pipeline.py`

### Local Docker Commands

Build the image:

```powershell
docker build -t qim-watermark-project .
```

Run the container:

```powershell
docker run --rm qim-watermark-project
```

### GitHub Secrets And Variables

For the workflow to push to Docker Hub and deploy to Azure, add these in GitHub:

- Repository variable: `DOCKERHUB_USERNAME`
- Repository variable: `AZURE_WEBAPP_NAME`
- Repository secret: `DOCKERHUB_TOKEN`
- Repository secret: `AZURE_CREDENTIALS`

If these are missing, the workflow still tests the code and builds the Docker image locally in GitHub Actions, but it skips the push and deploy steps.
