from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import os
import mux_python
from mux_python.rest import ApiException
import time
import requests
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from typing import Literal
import subprocess
import cv2 as cv
#processes the clip with an AI summary from gemini
# ensure you have enviroment variables 
# GEMINI_API_KEY 

prompt = """
You are analyzing a short video clip to determine whether a meaningful incident occurred.

Your task is to produce a single IncidentReport object that strictly matches the following schema:

- summary (string):
  A concise 1–3 sentence summary of what happened in the video. If nothing significant occurs, briefly state that the scene shows normal activity.

- extended_summary (string):
  A detailed natural-language description of the event, including:
  • What happened and how it unfolded
  • Who was involved (describe people by appearance or actions, not IDs)
  • Relevant objects or environment
  • Why the event matters
  • Any reasonable follow-up actions if applicable
  If no meaningful incident occurred, explain clearly why the activity is considered normal or insignificant.

- severity (integer: 0–3):
  Assign exactly one numeric severity:
    0 = No incident / normal activity
    1 = Minor (routine or low-risk activity worth noting)
    2 = Medium (unusual or suspicious activity requiring review)
    3 = High (critical incident requiring immediate attention)

- incident_type (IncidentType enum):
  Choose exactly one category that best describes the situation:
    Crime
    Medical Emergency
    Traffic Incident
    Property Damage
    Safety Hazard
    Suspicious Activity
    Normal Activity
    Camera Interference

IMPORTANT RULES:
- If no meaningful or noteworthy incident occurs, set:
    severity = 0
    incident_type = Normal Activity
- Only escalate severity when there is clear visual evidence.
- Do not invent actions, intent, or outcomes that cannot be observed.
- Do not include tags, timestamps, object lists, or multiple events.
- Output must conform exactly to the IncidentReport schema.
"""

class IncidentType(str, Enum):
    SHOPLIFTING = "Shoplifting"
    FIGHT = "Fight"
    TRESPASSING = "Trespassing"
    VANDALISM = "Vandalism"
    SUSPICIOUS_BEHAVIOR = "Suspicious_Behavior"
    NONE = "None"
    OTHER = "Other"

class IncidentReport(BaseModel):
    summary: str = Field(
        description="Text summary describing what happened in the video incident."
    )

    extended_summary: str = Field(
        description="Extended summmary of the current event, providing more details what occurs in the given clip, details about the suspect, and future actions that should be taken."
    )

    severity: Literal[0, 1, 2, 3] = Field(
        description="Incident severity level from 1 (low) to 3 (high). Return 0 if no major incident occurs."
    )
    incident_type: IncidentType = Field(
        description="Classifier describing the type of incident."
    )

def clipProcessing(video_file_path):
    # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    video_bytes = open(video_file_path, 'rb').read()
    load_dotenv()
    client = genai.Client(api_key= os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model='models/gemini-3-flash-preview',
        contents=types.Content(
            parts=[
                types.Part(
                    inline_data=types.Blob(data=video_bytes, mime_type='video/mp4')
                ),
                types.Part(text=prompt)
            ]
        ),
                config={
        "response_mime_type": "application/json",
        "response_json_schema": IncidentReport.model_json_schema(),
        },
    )
    print(f"This is response.text{response.text}")
    response = IncidentReport.model_validate_json(response.text)
    return(response)

# uploads clip to database
# ensure you have enviroment variables 
# MUX_TOKEN_ID
# MUX_TOKEN_SECRET
def uploadToMux(video_file_path):
    # Authentication Setup
    load_dotenv()
    configuration = mux_python.Configuration()
    configuration.username = os.environ["MUX_TOKEN_ID"]
    configuration.password = os.environ["MUX_TOKEN_SECRET"]
    # API Client Initialization
    uploads_api = mux_python.DirectUploadsApi(
        mux_python.ApiClient(configuration)
    )
    # ========== create-direct-upload ==========
    create_asset_request = mux_python.CreateAssetRequest(
        playback_policy=[mux_python.PlaybackPolicy.PUBLIC]
    )
    create_upload_request = mux_python.CreateUploadRequest(
        timeout=3600,
        new_asset_settings=create_asset_request,
        cors_origin="philcluff.co.uk"
    )
    create_upload_response = uploads_api.create_direct_upload(
        create_upload_request
    )
    upload_id = create_upload_response.data.id
    upload_url = create_upload_response.data.url
    print(f"Upload ID: {upload_id}")
    print(f"Upload URL: {upload_url}")
    print("create-direct-upload OK ✅")

    # ========== ACTUAL FILE UPLOAD ==========
    print("Uploading file to Mux...")
    with open(video_file_path, "rb") as f:
        upload_response = requests.put(
            upload_url,
            data=f,
            headers={
                "Content-Type": "application/octet-stream"
            }
        )

    upload_response.raise_for_status()
    print("File upload completed ✅")
    # ========== wait for Mux to process ==========
    print("Waiting for asset creation...")
    asset_id = None
    for _ in range(30):  # ~30 seconds max
        upload_status = uploads_api.get_direct_upload(upload_id)
        asset_id = upload_status.data.asset_id
        if asset_id:
            break
        time.sleep(1)

    assert asset_id is not None
    print(f"Asset created 🎉 Asset ID: {asset_id}")
    # OPTIONAL: fetch asset details
    assets_api = mux_python.AssetsApi(
        mux_python.ApiClient(configuration)
    )
    asset = assets_api.get_asset(asset_id)
    print(f"Asset status: {asset.data.status}")
    playback_id = asset.data.playback_ids[0].id
    print(f"Playback ID 🎬: {playback_id}")

    return playback_id

# Testing!!!

"""
classification = clipProcessing("shoplifting.mp4")
print(classification.summary)
print(classification.severity)
print(classification.incident_type)
"""

# print(clipProcessing('clips\clip_1768719951.mp4'))