#!/usr/bin/env python3
"""
Test Basic Table Extraction using od-parse library
"""

import os
import sys
import json
from pathlib import Path

# Add od-parse to path
current_dir = os.path.dirname(os.path.abspath(__file__))
od_parse_dir = os.path.join(current_dir, 'od-parse')
sys.path.insert(0, od_parse_dir)

def test_basic_table_extraction():
    """Test the basic table extraction using extract_tables function."""
    
    # Create output directory
    output_dir = Path("basic_table_extraction_output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        from od_parse.parser.pdf_parser import extract_tables
        
        print("Testing Basic Table Extraction")
        print("=" * 50)
        
        # Test with PDF file - entire document
        pdf_path = "financial_reasoning.pdf"
        print(f"1. Testing table extraction from entire PDF: {pdf_path}")
        
        # Extract tables from entire PDF using extract_tables function
        tables = extract_tables(pdf_path)
        
        print(f"Extraction completed successfully!")
        print(f"Number of tables found: {len(tables)}")
        
        # Process each table
        tables_data = []
        for i, table in enumerate(tables):
            print(f"\nTable {i+1}:")
            print(f"  Shape: {table.get('shape', 'unknown')}")
            print(f"  Confidence: {table.get('confidence', 0.8):.3f}")
            
            # Show table data
            data = table.get('data', [])
            if data:
                print(f"  Number of rows: {len(data)}")
                print(f"  First row: {data[0] if len(data) > 0 else 'No data'}")
                
                # Show sample data
                if len(data) > 0:
                    print(f"  Sample data (first 3 rows):")
                    for j, row in enumerate(data[:3]):
                        print(f"    Row {j+1}: {row}")
            
            tables_data.append(table)
        
        # Save results to files
        print(f"\n2. Saving results to files...")
        
        # Save complete results
        complete_results = {
            "pdf_path": pdf_path,
            "tables_found": len(tables),
            "tables_data": tables_data
        }
        
        with open(output_dir / "basic_extraction_results.json", "w") as f:
            json.dump(complete_results, f, indent=2, default=str)
        
        # Save detailed table data
        with open(output_dir / "extracted_tables.json", "w") as f:
            json.dump(tables_data, f, indent=2, default=str)
        
        # Create summary report
        with open(output_dir / "basic_extraction_report.md", "w") as f:
            f.write("# Basic Table Extraction Report\n\n")
            
            f.write("## Document Information\n")
            f.write(f"- PDF File: {pdf_path}\n")
            f.write(f"- Tables Found: {len(tables)}\n\n")
            
            f.write("## Extracted Tables\n")
            for i, table in enumerate(tables):
                f.write(f"### Table {i+1}\n")
                f.write(f"- Shape: {table.get('shape', 'unknown')}\n")
                f.write(f"- Confidence: {table.get('confidence', 0.8):.3f}\n")
                
                # Show table data
                data = table.get('data', [])
                if data:
                    f.write(f"- Number of Rows: {len(data)}\n")
                    f.write(f"- Sample Data:\n")
                    for j, row in enumerate(data[:5]):  # Show first 5 rows
                        f.write(f"  Row {j+1}: {row}\n")
                
                f.write("\n")
        
        print(f"Results saved to: {output_dir}")
        print(f"- Complete results: {output_dir / 'basic_extraction_results.json'}")
        print(f"- Extracted tables: {output_dir / 'extracted_tables.json'}")
        print(f"- Summary report: {output_dir / 'basic_extraction_report.md'}")
        
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
    
    print("Testing Basic Table Extraction")
    print("=" * 60)
    
    success = test_basic_table_extraction()
    
    if success:
        print("\nTest completed successfully!")
        print("Check the output files for detailed results.")
    else:
        print("\nTest failed. Check error messages above.")

if __name__ == "__main__":
    main()
