"""
This code sample shows Prebuilt Layout operations with the Azure AI Document Intelligence client library.
The async versions of the samples require Python 3.8 or later.

To learn more, please visit the documentation - Quickstart: Document Intelligence (formerly Form Recognizer) SDKs
https://learn.microsoft.com/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?pivots=programming-language-python
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

from azure.storage.blob import BlobClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv
load_dotenv()

import json

"""
Remember to remove the key from your code when you're done, and never post it publicly. For production, use
secure methods to store and access your credentials. For more information, see 
https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-security?tabs=command-line%2Ccsharp#environment-variables-and-application-configuration
"""
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

# formUrl = f"https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"
formUrl = f"https://{storage_account}.blob.core.windows.net/{container_name}/{blob_name}?"#{sas_token}"

print("Processing blob: ", formUrl)

document_intelligence_client  = DocumentIntelligenceClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

poller = document_intelligence_client.begin_analyze_document(
    "prebuilt-layout", AnalyzeDocumentRequest(url_source=formUrl), output_content_format="markdown"
)
result = poller.result()

# print("Results: ", result)

save_name = formUrl.split("https://")[1].split("/")[0]

# save intermediate results to debug
with open(f"output-{save_name}.json", "w", encoding="utf-8") as output_file:
    output_file.write(json.dumps(result.as_dict(), indent=4))

print("Processing PDF document.")
for page in result.pages:
    for line_idx, line in enumerate(page.lines):
        print(
            "...Line # {} has text content '{}'".format(
        line_idx,
        line.content.encode("utf-8")
        )
    )

    for selection_mark in page.selection_marks:
        print(
            "...Selection mark is '{}' and has a confidence of {}".format(
            selection_mark.state,
            selection_mark.confidence
            )
    )

for table_idx, table in enumerate(result.tables):
    print(
        "Table # {} has {} rows and {} columns".format(
        table_idx, table.row_count, table.column_count
        )
    )
        
    for cell in table.cells:
        print(
            "...Cell[{}][{}] has content '{}'".format(
            cell.row_index,
            cell.column_index,
            cell.content.encode("utf-8"),
            )
        )


for idx, style in enumerate(result.styles):
    print(
        "Document contains {} content".format(
         "handwritten" if style.is_handwritten else "no handwritten"
        )
    )



print("----------------------------------------")

