# vods-uploader

## Prerequisites
- Python 3.8 or higher
- pip
- install the requirements.txt

## Usage
1. Create a `.env` file in the root directory of the project.
2. Add the following environment variables to the `.env` file:
```env
GOOGLE_CLIENT_SECRETS_FILE=client_secrets.json
```
3. Drag the `client_secrets.json` file (downloaded from the google cloud console or given to you) into this directory/folder.
4. Run the script:
```
python youtube_v3_video_uploader.py
```
