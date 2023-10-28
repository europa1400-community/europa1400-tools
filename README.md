![GitHub release (latest by date)](https://img.shields.io/github/v/release/europa1400-community/europa1400-tools)
[![Discord](https://img.shields.io/discord/824534227927171092?color=7389D8&label=%20&logo=discord&logoColor=ffffff)](https://discord.gg/CPPAKarms2)

[![Publish](https://github.com/europa1400-community/europa1400-tools/actions/workflows/publish.yml/badge.svg)](https://github.com/europa1400-community/europa1400-tools/actions/workflows/publish.yml)
[![Code Quality](https://github.com/europa1400-community/europa1400-tools/actions/workflows/quality.yml/badge.svg)](https://github.com/europa1400-community/europa1400-tools/actions/workflows/quality.yml)

[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=europa1400-community_europa1400-tools&metric=bugs)](https://sonarcloud.io/summary/new_code?id=europa1400-community_europa1400-tools)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=europa1400-community_europa1400-tools&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=europa1400-community_europa1400-tools)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=europa1400-community_europa1400-tools&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=europa1400-community_europa1400-tools)

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
