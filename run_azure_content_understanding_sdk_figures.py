# Adapted from: https://github.com/Azure/azure-sdk-for-python/blob/6a690955c5dfefa8869c80a94bd83e2f947449f4/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_configs.py#L21

# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_configs.py

DESCRIPTION:
    This sample demonstrates how to extract additional features from documents such as charts,
    hyperlinks, formulas, and annotations using the prebuilt-documentSearch analyzer, which has
    formulas, layout, and OCR enabled by default.

ABOUT ANALYSIS CONFIGS:
    The prebuilt-documentSearch analyzer has the following configurations enabled by default:
    - ReturnDetails: true - Returns detailed information about document elements
    - EnableOcr: true - Performs OCR on documents
    - EnableLayout: true - Extracts layout information (tables, figures, hyperlinks, annotations)
    - EnableFormula: true - Extracts mathematical formulas from documents
    - EnableFigureDescription: true - Generates descriptions for figures
    - EnableFigureAnalysis: true - Analyzes figures including charts
    - ChartFormat: "chartjs" - Chart figures are returned in Chart.js format
    - TableFormat: "html" - Tables are returned in HTML format
    - AnnotationFormat: "markdown" - Annotations are returned in markdown format

    The following code snippets demonstrate extraction of features enabled by these configs:
    - Charts: Enabled by EnableFigureAnalysis - Chart figures with Chart.js configuration
    - Hyperlinks: Enabled by EnableLayout - URLs and links found in the document
    - Formulas: Enabled by EnableFormula - Mathematical formulas in LaTeX format
    - Annotations: Enabled by EnableLayout - PDF annotations, comments, and markup

    For custom analyzers, you can configure these options in ContentAnalyzerConfig when creating
    the analyzer.

PREREQUISITES:
    To get started you'll need a Microsoft Foundry resource. See sample_update_defaults.py
    for setup guidance.

USAGE:
    python sample_analyze_configs.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_update_defaults.py for setup instructions.
"""

import os
from typing import cast
import json

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisResult,
    DocumentContent,
    DocumentChartFigure,
    DocumentAnnotation,
    DocumentFormula,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint_base = "https://foundry-bjorn.services.ai.azure.com"
    key = os.environ["CONTENT_UNDERSTANDING_API_KEY"]

    analyzer_id = "my_custom_analyzer_1773144144"
    
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint_base, credential=credential)

    # [START analyze_with_configs]
    file_path = "sample_files/Gaskwaliteitsklasje - editie 2025, februari.pdf"

    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    print(f"Analyzing {file_path} with analyzer ID: {analyzer_id}...")
    print(
        "Note: This analyzer has formulas, layout, and OCR enabled by default."
    )

    # Analyze with the specified analyzer which has formulas, layout, and OCR enabled
    poller = client.begin_analyze_binary(
        analyzer_id=analyzer_id,
        binary_input=pdf_bytes,
    )
    result: AnalysisResult = poller.result()
    # [END analyze_with_configs]

    # [START extract_charts]
    # Extract charts from document content (enabled by EnableFigureAnalysis config)
    document_content = cast(DocumentContent, result.contents[0])
    if document_content.figures:
        for figure in document_content.figures:
            if isinstance(figure, DocumentChartFigure):
                print(f"  Chart ID: {figure.id}")
                print(f"    Description: {figure.description or '(not available)'}")
                print(
                    f"    Caption: {figure.caption.content if figure.caption else '(not available)'}"
                )
    # [END extract_charts]

    # [START extract_hyperlinks]
    # Extract hyperlinks from document content (enabled by EnableLayout config)
    doc_content = cast(DocumentContent, result.contents[0])
    print(
        f"Found {len(doc_content.hyperlinks) if doc_content.hyperlinks else 0} hyperlink(s)"
    )
    for hyperlink in doc_content.hyperlinks or []:
        print(f"  URL: {hyperlink.url or '(not available)'}")
        print(f"    Content: {hyperlink.content or '(not available)'}")
    # [END extract_hyperlinks]

    # [START extract_formulas]
    # Extract formulas from document pages (enabled by EnableFormula config)
    content = cast(DocumentContent, result.contents[0])
    all_formulas: list = []
    for page in content.pages or []:
        all_formulas.extend(page.formulas or [])

    print(f"Found {len(all_formulas)} formula(s)")
    for formula in all_formulas:
        print(f"  Formula Kind: {formula.kind}")
        print(f"    LaTeX: {formula.value or '(not available)'}")
        print(
            f"    Confidence: {f'{formula.confidence:.2f}' if formula.confidence else 'N/A'}"
        )
    # [END extract_formulas]

    # [START extract_annotations]
    # Extract annotations from document content (enabled by EnableLayout config)
    document = cast(DocumentContent, result.contents[0])
    print(
        f"Found {len(document.annotations) if document.annotations else 0} annotation(s)"
    )
    for annotation in document.annotations or []:
        print(f"  Annotation ID: {annotation.id}")
        print(f"    Kind: {annotation.kind}")
        print(f"    Author: {annotation.author or '(not available)'}")
        print(f"    Comments: {len(annotation.comments) if annotation.comments else 0}")
        for comment in annotation.comments or []:
            print(f"      - {comment.message}")
    # [END extract_annotations]

    print("Analysis complete!")
    # Here is your final result object
    # print(result_data)
    with open(os.path.join("data", "output", "content-understanding", f"output-{analyzer_id}-with-figure-sdk.json"), "w", encoding="utf-8") as output_file:
        output_file.write(json.dumps(document.as_dict(), indent=4))


if __name__ == "__main__":
    main()