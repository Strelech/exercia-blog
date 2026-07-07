#!/usr/bin/env python3
"""
Upload les PNG générés vers Google Drive.
Lit les variables d'env GDRIVE_CREDENTIALS (JSON Service Account) et GDRIVE_FOLDER_ID.
"""

import os
import json
import glob
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_slides():
    # Récupérer les credentials depuis la variable d'env
    credentials_json = os.environ["GDRIVE_CREDENTIALS"]
    folder_id = os.environ["GDRIVE_FOLDER_ID"]

    credentials_info = json.loads(credentials_json)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=credentials)

    # Chercher les PNG dans social/output/
    output_dir = Path(__file__).parent / "output"
    png_files = sorted(glob.glob(str(output_dir / "*.png")))

    if not png_files:
        print("Aucun PNG trouvé dans social/output/")
        return

    uploaded = []
    for png_path in png_files:
        filename = Path(png_path).name
        print(f"Upload {filename}...")

        file_metadata = {
            "name": filename,
            "parents": [folder_id]
        }
        media = MediaFileUpload(png_path, mimetype="image/png", resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id,name,webViewLink"
        ).execute()

        uploaded.append({
            "name": file["name"],
            "id": file["id"],
            "url": file["webViewLink"]
        })
        print(f"  ✓ {file['name']} → {file['webViewLink']}")

    # Écrire un manifest JSON pour que GAS puisse récupérer les IDs
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(uploaded, f, indent=2)

    # Uploader aussi le manifest
    manifest_metadata = {
        "name": "manifest.json",
        "parents": [folder_id]
    }
    media = MediaFileUpload(str(manifest_path), mimetype="application/json")
    manifest_file = service.files().create(
        body=manifest_metadata,
        media_body=media,
        fields="id,name"
    ).execute()

    print(f"\n✓ manifest.json uploadé (id: {manifest_file['id']})")
    print(f"Done — {len(uploaded)} slides uploadées dans Drive")

if __name__ == "__main__":
    upload_slides()
