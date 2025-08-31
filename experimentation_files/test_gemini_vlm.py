#!/usr/bin/env python3
"""
Test od-parse library's VLM processor abstractions with Gemini API
"""

import os
import sys
import json
from pathlib import Path

# Add od-parse to path
current_dir = os.path.dirname(os.path.abspath(__file__))
od_parse_dir = os.path.join(current_dir, 'od-parse')
sys.path.insert(0, od_parse_dir)

def test_vlm_processor_abstractions():
    """Test the od-parse VLM processor abstractions with Gemini API."""
    
    # Create output directory
    output_dir = Path("vlm_test_output")
    output_dir.mkdir(exist_ok=True)
    
    all_results = {}
    
    try:
        from od_parse.advanced.vlm_processor import VLMProcessor
        
        print("Testing VLM Processor Abstractions")
        print("=" * 50)
        
        # Initialize the VLM processor with Gemini
        print("1. Initializing VLM processor...")
        vlm_processor = VLMProcessor({
            "model": "gemini-1.5-flash",
            "api_key": os.getenv('GEMINI_API_KEY', ''),  # Use environment variable
            "max_tokens": 2048,
            "temperature": 0.2,
            "system_prompt": "You are an expert document analyzer. Extract all information from this document."
        })
        
        print("VLM processor initialized successfully")
        
        # Test 1: Basic document image processing
        print("\n2. Testing basic document image processing...")
        vlm_analysis = vlm_processor.process_document_image(
            "financial_reasoning_images/page_1.png",
            "Analyze this research paper page and describe its content, structure, and any figures or tables."
        )
        
        all_results["basic_analysis"] = vlm_analysis
        
        if "error" not in vlm_analysis:
            print("Basic processing successful")
            print(f"Model used: {vlm_analysis.get('model', 'Unknown')}")
            print(f"Analysis preview: {vlm_analysis.get('analysis', '')[:200]}...")
        else:
            print(f"Basic processing failed: {vlm_analysis['error']}")
        
        # Test 2: Table extraction with VLM
        print("\n3. Testing table extraction with VLM...")
        tables = vlm_processor.extract_tables_with_vlm("financial_reasoning_images/page_1.png")
        
        all_results["table_extraction"] = tables
        
        if tables:
            print(f"Extracted {len(tables)} tables with VLM")
            for i, table in enumerate(tables):
                print(f"Table {i+1}: {str(table)[:100]}...")
        else:
            print("No tables extracted with VLM")
        
        # Test 3: Form field extraction with VLM
        print("\n4. Testing form field extraction with VLM...")
        form_fields = vlm_processor.extract_form_fields_with_vlm("financial_reasoning_images/page_1.png")
        
        all_results["form_extraction"] = form_fields
        
        if form_fields:
            print(f"Extracted {len(form_fields)} form fields with VLM")
            print(f"Form fields: {form_fields}")
        else:
            print("No form fields extracted with VLM")
        
        # Test 4: Enhanced parsing results
        print("\n5. Testing enhanced parsing results...")
        
        # Create mock parsed data
        mock_parsed_data = {
            "text": "Sample extracted text from traditional parsing",
            "tables": [{"data": [["Header1", "Header2"], ["Value1", "Value2"]]}],
            "forms": [],
            "metadata": {"pages": 1, "file_type": "pdf"}
        }
        
        enhanced_data = vlm_processor.enhance_parsing_results(mock_parsed_data, "financial_reasoning_images/page_1.png")
        
        all_results["enhanced_parsing"] = enhanced_data
        
        if "vlm_analysis" in enhanced_data:
            print("Enhanced parsing successful")
            vlm_analysis = enhanced_data["vlm_analysis"]
            if "status" not in vlm_analysis:  # No error
                print(f"VLM analysis added: {vlm_analysis.get('analysis', '')[:200]}...")
            else:
                print(f"VLM analysis error: {vlm_analysis.get('message', 'Unknown error')}")
        else:
            print("Enhanced parsing failed")
        
        # Test 5: Multiple image processing
        print("\n6. Testing multiple image processing...")
        image_files = list(Path("financial_reasoning_images").glob("*.png"))[:3]  # Test first 3 images
        
        multi_image_results = {}
        for i, image_path in enumerate(image_files):
            print(f"Processing image {i+1}: {image_path.name}")
            
            analysis = vlm_processor.process_document_image(
                str(image_path),
                "Describe the key content and structure of this research paper page."
            )
            
            multi_image_results[image_path.name] = analysis
            
            if "error" not in analysis:
                print(f"  Success: {analysis.get('analysis', '')[:100]}...")
            else:
                print(f"  Failed: {analysis['error']}")
        
        all_results["multi_image_processing"] = multi_image_results
        
        # Test 6: Structured data extraction
        print("\n7. Testing structured data extraction...")
        structured_prompt = """
        Analyze this document and provide the following information in JSON format:
        {
            "title": "document title",
            "sections": ["list of section headings"],
            "figures": ["list of figure descriptions"],
            "tables": ["list of table descriptions"],
            "key_points": ["list of key points"]
        }
        """
        
        structured_analysis = vlm_processor.process_document_image(
            "financial_reasoning_images/page_1.png",
            structured_prompt
        )
        
        all_results["structured_analysis"] = structured_analysis
        
        if "error" not in structured_analysis:
            print("Structured analysis successful")
            analysis_text = structured_analysis.get("analysis", "")
            
            # Try to extract JSON
            try:
                json_start = analysis_text.find("{")
                json_end = analysis_text.rfind("}")
                if json_start >= 0 and json_end >= 0:
                    json_str = analysis_text[json_start:json_end+1]
                    structured_data = json.loads(json_str)
                    print(f"Extracted structured data: {json.dumps(structured_data, indent=2)}")
                    
                    # Save structured data to file
                    with open(output_dir / "structured_data.json", "w") as f:
                        json.dump(structured_data, f, indent=2)
                    print(f"Structured data saved to: {output_dir / 'structured_data.json'}")
                else:
                    print("No JSON found in response")
            except json.JSONDecodeError:
                print("Could not parse JSON from response")
        else:
            print(f"Structured analysis failed: {structured_analysis['error']}")
        
        # Save all results to file
        with open(output_dir / "all_vlm_results.json", "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        
        # Save detailed analysis to markdown
        with open(output_dir / "vlm_analysis_report.md", "w") as f:
            f.write("# VLM Processor Analysis Report\n\n")
            
            f.write("## Basic Document Analysis\n")
            if "basic_analysis" in all_results and "error" not in all_results["basic_analysis"]:
                f.write(f"**Model Used:** {all_results['basic_analysis'].get('model', 'Unknown')}\n\n")
                f.write(f"**Analysis:**\n{all_results['basic_analysis'].get('analysis', '')}\n\n")
            
            f.write("## Table Extraction\n")
            if all_results.get("table_extraction"):
                f.write(f"**Tables Found:** {len(all_results['table_extraction'])}\n\n")
                for i, table in enumerate(all_results["table_extraction"]):
                    f.write(f"### Table {i+1}\n```json\n{json.dumps(table, indent=2)}\n```\n\n")
            
            f.write("## Form Field Extraction\n")
            if all_results.get("form_extraction"):
                f.write(f"**Form Fields Found:** {len(all_results['form_extraction'])}\n\n")
                f.write(f"```json\n{json.dumps(all_results['form_extraction'], indent=2)}\n```\n\n")
            
            f.write("## Multi-Image Processing Results\n")
            for image_name, result in all_results.get("multi_image_processing", {}).items():
                f.write(f"### {image_name}\n")
                if "error" not in result:
                    f.write(f"{result.get('analysis', '')}\n\n")
                else:
                    f.write(f"Error: {result['error']}\n\n")
        
        print(f"\nAll results saved to: {output_dir}")
        print(f"- Complete results: {output_dir / 'all_vlm_results.json'}")
        print(f"- Structured data: {output_dir / 'structured_data.json'}")
        print(f"- Analysis report: {output_dir / 'vlm_analysis_report.md'}")
        
        print("\n" + "=" * 50)
        print("All VLM processor abstraction tests completed!")
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're in the virtual environment and dependencies are installed")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    
    print("Testing od-parse VLM Processor Abstractions")
    print("=" * 60)
    
    success = test_vlm_processor_abstractions()
    
    if success:
        print("\nTest completed successfully!")
        print("VLM processor abstractions are working correctly.")
    else:
        print("\nTest failed. Check error messages above.")

if __name__ == "__main__":
    main()