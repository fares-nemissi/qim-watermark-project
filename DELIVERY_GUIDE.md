# Delivery Guide

This file helps you finish the GitHub, Docker Hub, and optional Azure parts after the code is done.

## Part 1: Put The Project On GitHub

### What I already did

- I initialized Git in this folder.
- I created the first commit.
- I added:
  - `.gitignore`
  - `Dockerfile`
  - `.github/workflows/ci-cd.yml`
  - `tests/test_watermark_pipeline.py`

### What you do in the browser

1. Open `https://github.com`
2. Sign in.
3. Click the `+` icon at the top right.
4. Click `New repository`.
5. In `Repository name`, type:

```text
qim-watermark-project
```

6. Leave it as `Public` if your teacher wants to see it easily.
7. Do not check `Add a README file`.
8. Click `Create repository`.

### What you do in VS Code terminal

Open the terminal in the project folder and run these commands one by one.

Replace `YOUR_GITHUB_USERNAME` with your real GitHub username.

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/qim-watermark-project.git
git push -u origin main
```

If GitHub asks you to sign in, complete the sign-in window and come back.

## Part 2: Check GitHub Actions

### What should happen

After the push:

1. Go to your repository on GitHub.
2. Click the `Actions` tab.
3. You should see a workflow named `CI-CD`.

### What it does

- installs Python
- installs the project libraries
- runs the test
- runs the watermark demo
- builds the Docker image
- uploads the `results` folder as an artifact

If Docker Hub and Azure secrets are not added yet, push and deploy are skipped automatically.

## Part 3: Install Docker Desktop

Docker is not installed on your computer yet, so do this first.

1. Open `https://www.docker.com/products/docker-desktop/`
2. Download `Docker Desktop for Windows`.
3. Run the installer.
4. Keep the default options.
5. Finish the install.
6. Restart the computer if Docker asks.
7. Open `Docker Desktop`.
8. Wait until it says Docker is running.

### Test Docker

In the project terminal, run:

```powershell
docker --version
```

If you see a version number, Docker is ready.

## Part 4: Build The Docker Image

In the project terminal, run:

```powershell
docker build -t qim-watermark-project .
```

When it finishes, run:

```powershell
docker run --rm qim-watermark-project
```

This should print the watermark report in the terminal.

## Part 5: Create Docker Hub Account And Token

### Create the account

1. Open `https://hub.docker.com`
2. Sign in or create an account.

### Create the access token

1. Click your profile picture.
2. Click `Account settings`.
3. Click `Personal access tokens`.
4. Click `Generate new token`.
5. Give it a name like:

```text
github-actions-qim
```

6. Copy the token and keep it safe.

## Part 6: Add GitHub Secrets And Variables

Open your GitHub repository in the browser.

1. Click `Settings`.
2. In the left menu, click `Secrets and variables`.
3. Click `Actions`.

### Add repository variable 1

1. Click `Variables`.
2. Click `New repository variable`.
3. Name:

```text
DOCKERHUB_USERNAME
```

4. Value: your Docker Hub username
5. Click `Add variable`.

### Add repository secret 1

1. Click `Secrets`.
2. Click `New repository secret`.
3. Name:

```text
DOCKERHUB_TOKEN
```

4. Value: paste your Docker Hub personal access token
5. Click `Add secret`.

## Part 7: Push Again To Trigger Docker Push

After adding the secret and variable, make a small change, then push again.

Example:

1. Open `README.md`
2. Add one small line like:

```text
Project ready for GitHub Actions and Docker.
```

3. Save the file.
4. In the terminal run:

```powershell
git add README.md
git commit -m "Update README for delivery"
git push
```

Now go back to GitHub:

1. Click `Actions`
2. Open the latest workflow run
3. Check that:
  - `test` passed
  - `docker` passed

## Part 8: Check Docker Hub

After the workflow finishes:

1. Open Docker Hub.
2. Create a repository named:

```text
qim-watermark-project
```

3. Wait for GitHub Actions to push the image.
4. Refresh the page.

You should see tags like:

- `latest`
- a long tag matching the Git commit SHA

## Part 9: Optional Azure Deployment

Only do this if your teacher really wants Azure deployment.

### Create the Azure Web App

1. Open `https://portal.azure.com`
2. Sign in.
3. Search for `App Services`.
4. Click `Create`.
5. Choose a `Web App`.
6. Fill in:
  - subscription
  - resource group
  - app name
  - publish: `Docker Container`
  - operating system: `Linux`

Finish the creation.

### Create Azure credentials for GitHub

You need one GitHub secret named:

```text
AZURE_CREDENTIALS
```

You also need one GitHub variable named:

```text
AZURE_WEBAPP_NAME
```

The workflow file already expects those names.

### Add Azure variable

In GitHub repository settings:

1. Click `Settings`
2. Click `Secrets and variables`
3. Click `Actions`
4. Click `Variables`
5. Click `New repository variable`
6. Name:

```text
AZURE_WEBAPP_NAME
```

7. Value: your Azure Web App name

### Add Azure secret

1. Click `Secrets`
2. Click `New repository secret`
3. Name:

```text
AZURE_CREDENTIALS
```

4. Paste the Azure JSON credentials
5. Click `Add secret`

After that, every push to `main` can:

- test the project
- build the Docker image
- push it to Docker Hub
- deploy it to Azure

## Part 10: If Your Teacher Wants Pull Requests

You can practice the GitHub lab like this:

1. In VS Code, create a new branch:

```powershell
git checkout -b feature-readme-update
```

2. Change one file, for example `README.md`.
3. Save it.
4. Run:

```powershell
git add README.md
git commit -m "Small README update"
git push -u origin feature-readme-update
```

5. Open your GitHub repository.
6. Click the button that says `Compare & pull request`.
7. Add a title.
8. Click `Create pull request`.
9. Review it.
10. Click `Merge pull request`.

## Very Important

If one step fails, do not guess.

Send me:

- a screenshot, or
- the exact error message, or
- the exact step number where you got stuck

and I will guide you from there.
