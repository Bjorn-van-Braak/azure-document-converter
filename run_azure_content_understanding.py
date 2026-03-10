import os
import time
import requests
import json

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

from azure.storage.blob import BlobClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

# Load credentials from environment
api_key = os.environ["CONTENT_UNDERSTANDING_API_KEY"]
endpoint_base = "https://foundry-bjorn.services.ai.azure.com/contentunderstanding"
analyzer_id = "prebuilt-documentSearch"
api_version = "2025-11-01"

endpoint = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENT_INTELLIGENCE_API_KEY"]

# sample document
storage_account = "gasuniebjorn"
container_name = "gasunie-kennis-chatbot-uc1-bjorn"
blob_name = "Gaskwaliteitsklasje - editie 2025, februari.docx"

# Generate SAS token
# sas_token = generate_blob_sas(
#     account_name=storage_account,
#     container_name=container_name,
#     blob_name=blob_name,
#     account_key=os.environ["STORAGE_ACCOUNT_KEY"],
#     permission=BlobSasPermissions(read=True),
#     expiry=datetime.utcnow() + timedelta(hours=1)
# )

# 1. Start the Analysis (POST)
analyze_url = f"{endpoint_base}/analyzers/{analyzer_id}:analyze?api-version={api_version}"
# document_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"
document_url = f"https://{storage_account}.blob.core.windows.net/{container_name}/{blob_name}"#?{sas_token}"

print("Submitting analysis request...")
response = requests.post(
    analyze_url, 
    headers=
        {
            "Ocp-Apim-Subscription-Key": api_key,
            "Content-Type": "application/json"
        }, 
    json=
        {
            "inputs": [
                {"url": document_url}
            ],
            "config": {
                # "enableLayout": True,
                # "returnDetails": True,
                "enableFigureDescription": True
            }
        }
)

response.raise_for_status()

# The Operation-Location header contains the URL for the GET request
operation_url = response.headers.get("Operation-Location")
if not operation_url:
    # Fallback: manually construct result URL if header is missing
    # (Though Azure usually provides the full path in the header)
    print("Warning: Operation-Location not found in headers.")
    # You would parse the ID from response.json() if available
    raise Exception("Not implemented")

# 2. Poll for Results (GET)
print(f"Polling for results at: {operation_url}")

while True:
    result_response = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": api_key})
    result_response.raise_for_status()
    result_data = result_response.json()
    
    status = result_data.get("status")
    print(f"Current status: {status}")
    
    if status == "Succeeded":
        print("Analysis complete!")
        # Here is your final result object
        # print(result_data)
        with open(f"output-{analyzer_id}-with-figure.json", "w", encoding="utf-8") as output_file:
            output_file.write(json.dumps(result_data, indent=4))
        break
    elif status == "Failed":
        print("Analysis failed.")
        print(result_data.get("error"))
        break
    
    # Wait before polling again to avoid rate limiting
    time.sleep(2)