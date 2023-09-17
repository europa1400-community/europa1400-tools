# Python Tools for Europa 1400: The Guild / Die Gilde

## Setup

### Windows (using PowerShell)

1. Install VS Code

`winget install Microsoft.VisualStudioCode`

2. Install python

`winget install Python.Python.3.11`

3. Install ffmpeg

`winget install "FFmpeg (Shared)"`

4. Install poetry

`(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`

5. Open this project in VS Code and run the following commands in the integrated terminal:

`poetry config virtualenvs.in-project true`
`poetry install`

6. You're good to go!