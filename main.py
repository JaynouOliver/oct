#!/usr/bin/env python3
"""
Intelligent Document Parser - Comprehensive PDF Analysis with VLM Enhancement

This module combines traditional PDF parsing with advanced VLM capabilities to provide
intelligent document understanding, including:
- Text extraction and cleaning
- Table detection and extraction with VLM enhancement
- Image analysis and description generation (no metadata extraction)
- Structured data extraction for RAG pipelines
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass

# Add od-parse to path
current_dir = os.path.dirname(os.path.abspath(__file__))
od_parse_dir = os.path.join(current_dir, 'od-parse')
sys.path.insert(0, od_parse_dir)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")

@dataclass
class Config:
    """Configuration class for the intelligent document parser."""
    
    # VLM Configuration
    vlm_model_type: str = os.getenv('VLM_MODEL_TYPE', 'qwen')
    vlm_model_name: str = os.getenv('VLM_MODEL_NAME', 'qwen/qwen2.5-vl-32b-instruct:free')
    vlm_api_key: str = os.getenv('VLM_API_KEY', '')
    vlm_api_base: str = os.getenv('VLM_API_BASE', 'https://openrouter.ai/api/v1')
    vlm_max_tokens: int = int(os.getenv('VLM_MAX_TOKENS', '2048'))
    vlm_temperature: float = float(os.getenv('VLM_TEMPERATURE', '0.2'))
    vlm_system_prompt: str = os.getenv('VLM_SYSTEM_PROMPT', 'You are an expert document analyzer specializing in research papers.')
    
    # Document Processing Configuration
    pdf_file_path: str = os.getenv('PDF_FILE_PATH', 'financial_reasoning.pdf')
    output_directory: str = os.getenv('OUTPUT_DIRECTORY', 'intelligent_analysis_output')
    extract_images: bool = os.getenv('EXTRACT_IMAGES', 'true').lower() == 'true'
    generate_descriptions: bool = os.getenv('GENERATE_DESCRIPTIONS', 'true').lower() == 'true'
    
    # RAG Configuration
    text_chunk_size: int = int(os.getenv('TEXT_CHUNK_SIZE', '500'))
    enable_table_extraction: bool = os.getenv('ENABLE_TABLE_EXTRACTION', 'true').lower() == 'true'
    enable_image_analysis: bool = os.getenv('ENABLE_IMAGE_ANALYSIS', 'true').lower() == 'true'
    
    # Logging Configuration
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    enable_verbose_logging: bool = os.getenv('ENABLE_VERBOSE_LOGGING', 'false').lower() == 'true'
    
    # Rate Limiting Configuration
    enable_rate_limiting: bool = os.getenv('ENABLE_RATE_LIMITING', 'false').lower() == 'true'
    requests_per_minute: int = int(os.getenv('REQUESTS_PER_MINUTE', '16'))
    requests_per_day: int = int(os.getenv('REQUESTS_PER_DAY', '50'))
    
    def get_vlm_config(self) -> Dict[str, Any]:
        """Get VLM configuration dictionary."""
        return {
            "model_type": self.vlm_model_type,
            "model": self.vlm_model_name,
            "api_key": self.vlm_api_key,
            "api_base": self.vlm_api_base,
            "max_tokens": self.vlm_max_tokens,
            "temperature": self.vlm_temperature,
            "system_prompt": self.vlm_system_prompt
        }
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.vlm_api_key:
            print("Warning: VLM_API_KEY not set. VLM features will be disabled.")
            return False
        return True

class IntelligentDocumentParser:
    """
    Comprehensive document parser that combines traditional parsing with VLM enhancement.
    
    This class provides intelligent document analysis by:
    1. Extracting text, tables, and images using traditional methods
    2. Enhancing results with VLM analysis for better understanding
    3. Providing structured output suitable for RAG pipelines
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the intelligent document parser.
        
        Args:
            config: Configuration object. If None, loads from environment variables.
        """
        self.config = config or Config()
        self.logger = self._setup_logging()
        
        # Validate configuration
        self.config.validate()
        
        # Initialize VLM processor if config provided and valid
        self.vlm_processor = None
        if self.config.vlm_api_key:
            try:
                from od_parse.advanced.vlm_processor import VLMProcessor
                vlm_config = self.config.get_vlm_config()
                self.vlm_processor = VLMProcessor(vlm_config)
                self.logger.info("VLM processor initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize VLM processor: {e}")
        else:
            self.logger.info("VLM processor disabled - no API key provided")
        
        # Import core parsing functions
        try:
            from od_parse.parser.pdf_parser import parse_pdf, extract_tables, extract_text, extract_images
            self.parse_pdf = parse_pdf
            self.extract_tables = extract_tables
            self.extract_text = extract_text
            self.extract_images = extract_images
        except ImportError as e:
            self.logger.error(f"Failed to import core parsing functions: {e}")
            raise
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Suppress PDFBox warnings about Unicode mappings
        logging.getLogger('org.apache.pdfbox').setLevel(logging.ERROR)
        
        return logging.getLogger(__name__)
    
    def parse_document(self, pdf_path: Optional[Union[str, Path]] = None, 
                      extract_images: Optional[bool] = None,
                      generate_descriptions: Optional[bool] = None) -> Dict[str, Any]:
        """
        Parse a document with intelligent analysis and VLM enhancement.
        
        Args:
            pdf_path: Path to the PDF document (uses config if None)
            extract_images: Whether to extract and analyze images (uses config if None)
            generate_descriptions: Whether to generate image descriptions (uses config if None)
            
        Returns:
            Comprehensive document analysis results
        """
        # Use config values if not provided
        pdf_path = Path(pdf_path or self.config.pdf_file_path)
        extract_images = extract_images if extract_images is not None else self.config.extract_images
        generate_descriptions = generate_descriptions if generate_descriptions is not None else self.config.generate_descriptions
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        self.logger.info(f"Starting intelligent parsing of: {pdf_path}")
        
        # Initialize results structure
        results = {
            "document_info": {
                "file_path": str(pdf_path),
                "file_name": pdf_path.name,
                "file_size": pdf_path.stat().st_size,
                "parsed_at": datetime.now().isoformat(),
                "parser_version": "intelligent_document_parser_v1.0"
            },
            "extraction_methods": {
                "traditional_parsing": True,
                "vlm_enhancement": self.vlm_processor is not None,
                "image_analysis": extract_images
            },
            "content": {},
            "metadata": {}
        }
        
        try:
            # Step 1: Traditional PDF parsing
            self.logger.info("Step 1: Performing traditional PDF parsing...")
            start_time = time.time()
            traditional_results = self.parse_pdf(pdf_path)
            parsing_time = time.time() - start_time
            self.logger.info(f"Traditional PDF parsing completed in {parsing_time:.2f} seconds")
            
            # Extract and clean text
            text_content = traditional_results.get('text', '')
            cleaned_text = self._clean_text_for_rag(text_content)
            results["content"]["text"] = {
                "raw_text": text_content,
                "cleaned_text": cleaned_text,
                "word_count": len(text_content.split()),
                "character_count": len(text_content)
            }
            
            # Extract tables
            tables = traditional_results.get('tables', [])
            results["content"]["tables"] = {
                "count": len(tables),
                "data": tables
            }
            
            # Step 2: Image extraction and analysis
            if extract_images:
                self.logger.info("Step 2: Extracting and analyzing images...")
                start_time = time.time()
                image_results = self._extract_and_analyze_images(pdf_path)
                image_time = time.time() - start_time
                results["content"]["images"] = image_results
                self.logger.info(f"Image extraction and analysis completed in {image_time:.2f} seconds")
            
            # Step 3: Generate structured summary
            results["summary"] = self._generate_structured_summary(results)
            
            # Step 4: Prepare RAG-ready chunks
            self.logger.info("Step 4: Preparing RAG-ready chunks...")
            results["rag_chunks"] = self._prepare_rag_chunks(results)
            
            self.logger.info("Intelligent document parsing completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Error during intelligent parsing: {e}")
            results["error"] = str(e)
            return results
    
    def _extract_and_analyze_images(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract and analyze only actual document images (not page renders)."""
        try:
            # Extract all images using traditional method
            all_image_paths = self.extract_images(pdf_path)
            
            # Filter to identify only actual document images (not page renders)
            document_images = self._filter_document_images(all_image_paths)
            
            image_analysis = {
                "count": len(document_images),
                "paths": document_images,
                "descriptions": [],
                "filtering_stats": {
                    "total_images": len(all_image_paths),
                    "document_images": len(document_images),
                    "page_renders_filtered": len(all_image_paths) - len(document_images)
                }
            }
            
            # Analyze only the actual document images with VLM
            if self.vlm_processor and document_images and self.config.enable_image_analysis:
                for i, img_path in enumerate(document_images):
                    self.logger.info(f"Analyzing document image {i+1}/{len(document_images)}: {Path(img_path).name}")
                    
                    # Generate image description with timing
                    start_time = time.time()
                    description = self._generate_image_description(img_path)
                    processing_time = time.time() - start_time
                    
                    image_analysis["descriptions"].append({
                        "image_index": i,
                        "image_path": img_path,
                        "description": description,
                        "processing_time": processing_time
                    })
            
            return image_analysis
            
        except Exception as e:
            self.logger.error(f"Error extracting and analyzing images: {e}")
            return {"count": 0, "paths": [], "descriptions": [], "error": str(e)}
    

    
    def _filter_document_images(self, all_image_paths: List[str]) -> List[str]:
        """
        Filter out page renders and keep only actual document images.
        
        Based on the od-parse extract_images function:
        - Page renders are saved as: page_1.png, page_2.png, etc.
        - Actual document images are saved as: page_1_img_1.png, page_1_img_2.png, etc.
        """
        document_images = []
        
        for img_path in all_image_paths:
            filename = Path(img_path).name
            
            # Keep only images that contain "_img_" in their filename
            # These are the actual embedded document images, not page renders
            if "_img_" in filename:
                document_images.append(img_path)
        
        return document_images
    
    def _generate_image_description(self, image_path: str) -> Dict[str, Any]:
        """Generate detailed description of an image using VLM."""
        if not self.vlm_processor:
            return {"error": "VLM processor not available"}
        
        try:
            prompt = """
            Analyze this image from a research paper and provide a detailed description including:
            1. What type of content is shown (figure, table, diagram, chart, etc.)
            2. The main subject or topic
            3. Key elements and their relationships
            4. Any text, numbers, or labels visible
            5. The purpose or significance of this image in the context of a research paper
            
            Provide a comprehensive but concise description suitable for document understanding.
            """
            
            result = self.vlm_processor.process_document_image(image_path, prompt)
            
            if "error" in result:
                return {"error": result["error"]}
            
            return {
                "description": result.get("analysis", ""),
                "model": result.get("model", "unknown"),
                "confidence": 0.9  # High confidence for VLM analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error generating image description: {e}")
            return {"error": str(e)}

    
    def _clean_text_for_rag(self, text: str) -> str:
        """Clean text for RAG pipeline consumption."""
        if not text:
            return ""
        
        # Basic cleaning
        cleaned = text.strip()
        
        # Remove excessive whitespace
        cleaned = ' '.join(cleaned.split())
        
        # Replace problematic characters
        replacements = {
            '\u2013': '-',  # en dash
            '\u2014': '--',  # em dash
            '\u2019': "'",   # right single quotation
            '\u201c': '"',   # left double quotation
            '\u201d': '"',   # right double quotation
            '\u00a0': ' ',   # non-breaking space
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned
    
    def _generate_structured_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured summary of the document analysis."""
        content = results.get("content", {})
        
        summary = {
            "document_type": "research_paper",  # Could be enhanced with classification
            "total_pages": len(content.get("images", {}).get("paths", [])),
            "text_statistics": {
                "word_count": content.get("text", {}).get("word_count", 0),
                "character_count": content.get("text", {}).get("character_count", 0),
                "has_content": bool(content.get("text", {}).get("cleaned_text", ""))
            },
            "table_statistics": {
                "total_tables": content.get("tables", {}).get("count", 0),
                "has_tables": content.get("tables", {}).get("count", 0) > 0
            },
            "image_statistics": {
                "total_images": content.get("images", {}).get("count", 0),
                "described_images": len(content.get("images", {}).get("descriptions", [])),
                "has_images": content.get("images", {}).get("count", 0) > 0
            },


            "enhancement_status": {
                "vlm_applied": self.vlm_processor is not None,
                "images_analyzed": len(content.get("images", {}).get("descriptions", [])) > 0
            }
        }
        
        return summary
    
    def _prepare_rag_chunks(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare content chunks suitable for RAG pipeline."""
        chunks = []
        content = results.get("content", {})
        
        # Text chunks
        text_content = content.get("text", {}).get("cleaned_text", "")
        if text_content:
            # Split text into chunks (simplified - could be enhanced with semantic splitting)
            words = text_content.split()
            chunk_size = self.config.text_chunk_size
            
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_text = ' '.join(chunk_words)
                
                chunks.append({
                    "type": "text",
                    "content": chunk_text,
                    "chunk_id": f"text_{i//chunk_size + 1}",
                    "word_count": len(chunk_words),
                    "source": "traditional_parsing"
                })
        
        # Table chunks
        if self.config.enable_table_extraction:
            tables = content.get("tables", {}).get("data", [])
            for i, table in enumerate(tables):
                table_text = self._table_to_text(table)
                if table_text:
                    chunks.append({
                        "type": "table",
                        "content": table_text,
                        "chunk_id": f"table_{i + 1}",
                        "table_data": table,
                        "source": "traditional_parsing"
                    })
        

        
        # Image description chunks
        if self.config.enable_image_analysis:
            image_descriptions = content.get("images", {}).get("descriptions", [])
            for i, desc in enumerate(image_descriptions):
                if desc.get("description", {}).get("description"):
                    chunks.append({
                        "type": "image_description",
                        "content": desc["description"]["description"],
                        "chunk_id": f"image_{i + 1}",
                        "image_path": desc["image_path"],
                        "source": "vlm_enhancement"
                    })
        

        
        return chunks
    
    def _table_to_text(self, table: Dict[str, Any]) -> str:
        """Convert table data to readable text format."""
        try:
            data = table.get("data", [])
            if not data:
                return ""
            
            # Get headers from first row
            headers = list(data[0].keys()) if data else []
            
            # Build table text
            table_text = "Table:\n"
            
            # Add headers
            if headers:
                table_text += " | ".join(str(h) for h in headers) + "\n"
                table_text += "-" * (len(" | ".join(str(h) for h in headers))) + "\n"
            
            # Add data rows
            for row in data:
                row_values = [str(row.get(h, "")) for h in headers]
                table_text += " | ".join(row_values) + "\n"
            
            return table_text
            
        except Exception as e:
            self.logger.error(f"Error converting table to text: {e}")
            return ""
    
    def save_results(self, results: Dict[str, Any], output_dir: Optional[Union[str, Path]] = None) -> str:
        """Save parsing results to a single JSON file."""
        output_dir = Path(output_dir or self.config.output_directory)
        output_dir.mkdir(exist_ok=True)
        
        try:
            # Save complete results as single JSON file
            complete_results_path = output_dir / "document_analysis.json"
            with open(complete_results_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.logger.info(f"Results saved to: {complete_results_path}")
            return str(complete_results_path)
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            return str(e)
    



def main():
    """Main function to demonstrate the intelligent document parser."""
    
    # Load configuration from environment variables
    config = Config()
    
    # Initialize parser with configuration
    parser = IntelligentDocumentParser(config=config)
    
    print("Starting intelligent document analysis...")
    print("=" * 60)
    print(f"Configuration loaded:")
    print(f"- PDF File: {config.pdf_file_path}")
    print(f"- Output Directory: {config.output_directory}")
    print(f"- Extract Images: {config.extract_images}")
    print(f"- VLM Enabled: {bool(config.vlm_api_key)}")
    print("=" * 60)
    
    try:
        # Parse the document using configuration
        results = parser.parse_document()
        
        # Save results
        output_file = parser.save_results(results)
        
        # Print summary
        print("\nAnalysis completed successfully! \n\n")
        
        summary = results.get("summary", {})
        print(f"Document: {results.get('document_info', {}).get('file_name', 'Unknown')}")
        print(f"Pages: {summary.get('total_pages', 0)}")
        print(f"Words: {summary.get('text_statistics', {}).get('word_count', 0)}")
        print(f"Tables: {summary.get('table_statistics', {}).get('total_tables', 0)}")
        print(f"Images: {summary.get('image_statistics', {}).get('total_images', 0)}")
        print(f"RAG Chunks: {len(results.get('rag_chunks', []))}")
        

        
        print(f"\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
