# Adapted from: https://github.com/Azure/azure-sdk-for-python/blob/6a690955c5dfefa8869c80a94bd83e2f947449f4/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_create_analyzer.py

# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_create_analyzer.py

DESCRIPTION:
    This sample demonstrates how to create a custom analyzer with a field schema to extract
    structured data from documents. While this sample shows document modalities, custom analyzers
    can also be created for video, audio, and image content. The same concepts apply across all
    modalities.

    ## About custom analyzers

    Custom analyzers allow you to define a field schema that specifies what structured data to
    extract from documents. You can:
    - Define custom fields (string, number, date, object, array)
    - Specify extraction methods to control how field values are extracted:
      - generate - Values are generated freely based on the content using AI models (best for
        complex or variable fields requiring interpretation)
      - classify - Values are classified against a predefined set of categories (best when using
        enum with a fixed set of possible values)
      - extract - Values are extracted as they appear in the content (best for literal text
        extraction from specific locations). Note: This method is only available for document
        content. Requires estimateSourceAndConfidence to be set to true for the field.

      When not specified, the system automatically determines the best method based on the field
      type and description.
    - Use prebuilt analyzers as a base. Supported base analyzers include:
      - prebuilt-document - for document-based custom analyzers
      - prebuilt-audio - for audio-based custom analyzers
      - prebuilt-video - for video-based custom analyzers
      - prebuilt-image - for image-based custom analyzers
    - Configure analysis options (OCR, layout, formulas)
    - Enable source and confidence tracking: Set estimateFieldSourceAndConfidence to true at the
      analyzer level (in ContentAnalyzerConfig) or estimateSourceAndConfidence to true at the field
      level to get source location (page number, bounding box) and confidence scores for extracted
      field values. This is required for fields with method = extract and is useful for validation,
      quality assurance, debugging, and highlighting source text in user interfaces. Field-level
      settings override analyzer-level settings.

USAGE:
    python sample_create_analyzer.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using custom analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_update_defaults.py for setup instructions.
"""

import os
import time

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    # ContentFieldSchema,
    # ContentFieldDefinition,
    # ContentFieldType,
    # GenerationMethod,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()

def main() -> None:
    # endpoint = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]
    endpoint_base = "https://foundry-bjorn.services.ai.azure.com"
    # key = os.environ["DOCUMENT_INTELLIGENCE_API_KEY"]
    api_key = os.environ["CONTENT_UNDERSTANDING_API_KEY"]

    # endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    # key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(api_key) if api_key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint_base, credential=credential)

    # [START create_analyzer]
    # Generate a unique analyzer ID
    analyzer_id = f"my_custom_analyzer_{int(time.time())}"

    print(f"Creating custom analyzer '{analyzer_id}'...")

    # Create analyzer configuration
    # See: https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/concepts/analyzer-reference
    config = ContentAnalyzerConfig(
        enable_formula=False,
        enable_layout=True,
        enable_ocr=False,
        # estimate_field_source_and_confidence=True,
        return_details=True,
        table_format="html", # default is "html", you may use "markdown"
        enable_figure_description=True
    )

    # Create the analyzer with field schema
    analyzer = ContentAnalyzer(
        base_analyzer_id="prebuilt-document",
        description="Custom analyzer for extracting company information",
        config=config,
        # field_schema=field_schema,
        models={
            "completion": "gpt-4.1",
            "embedding": "text-embedding-3-large",
        },  # Required when using field_schema
    )

    # Create the analyzer
    poller = client.begin_create_analyzer(
        analyzer_id=analyzer_id,
        resource=analyzer,
    )
    result = poller.result()  # Wait for creation to complete

    # Get the full analyzer details after creation
    result = client.get_analyzer(analyzer_id=analyzer_id)

    print(f"Analyzer '{analyzer_id}' created successfully!")
    


    # Clean up - delete the analyzer
    # print(f"\nCleaning up: deleting analyzer '{analyzer_id}'...")
    # client.delete_analyzer(analyzer_id=analyzer_id)
    # print(f"Analyzer '{analyzer_id}' deleted successfully.")


if __name__ == "__main__":
    main()