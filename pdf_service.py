"""
PDF Service Layer – All PDF operations with proper error handling
"""

import os
import PyPDF2
from typing import List, Optional, Tuple
from pathlib import Path


class PDFError(Exception):
    """Custom exception for PDF operations"""
    pass


class PDFService:
    """Handles all PDF operations with validation and error handling"""

    @staticmethod
    def validate_file(path: str) -> Tuple[bool, str]:
        """
        Validate a PDF file exists and is readable
        Returns: (is_valid, error_message)
        """
        if not path:
            return False, "No file selected"

        if not os.path.exists(path):
            return False, f"File not found: {path}"

        if not path.lower().endswith('.pdf'):
            return False, "File is not a PDF"

        try:
            with open(path, 'rb') as f:
                PyPDF2.PdfReader(f)
            return True, ""
        except Exception as e:
            return False, f"Corrupt or invalid PDF: {str(e)}"

    @staticmethod
    def validate_files(paths: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate multiple PDFs
        Returns: (valid_paths, error_messages)
        """
        valid = []
        errors = []
        for path in paths:
            is_valid, error = PDFService.validate_file(path)
            if is_valid:
                valid.append(path)
            else:
                errors.append(f"{os.path.basename(path)}: {error}")
        return valid, errors

    @staticmethod
    def get_safe_output_dir(base_dir: str = "/sdcard") -> str:
        """Create a safe output directory with fallback"""
        output_dir = os.path.join(base_dir, "VishScan_Output")
        try:
            os.makedirs(output_dir, exist_ok=True)
            return output_dir
        except Exception:
            # Fallback to app directory
            fallback = "./output"
            os.makedirs(fallback, exist_ok=True)
            return fallback

    @staticmethod
    def get_safe_filename(base_name: str, extension: str = ".pdf") -> str:
        """Sanitize filename to avoid issues"""
        # Remove invalid characters
        import re
        safe_name = re.sub(r'[^\w\s-]', '', base_name)
        safe_name = safe_name.strip().replace(' ', '_')
        if not safe_name:
            safe_name = "output"
        return safe_name + extension

    @staticmethod
    def merge(pdf_paths: List[str], output_path: str) -> Tuple[bool, str]:
        """
        Merge multiple PDFs into one
        Returns: (success, message)
        """
        try:
            valid_paths, errors = PDFService.validate_files(pdf_paths)

            if len(valid_paths) < 2:
                return False, "Need at least 2 valid PDFs to merge"

            if errors:
                return False, f"Errors: {', '.join(errors)}"

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            merger = PyPDF2.PdfMerger()
            for p in valid_paths:
                merger.append(p)

            merger.write(output_path)
            merger.close()

            return True, f"Merged {len(valid_paths)} PDFs to {output_path}"

        except PyPDF2.errors.PdfReadError as e:
            return False, f"PDF read error: {str(e)}"
        except Exception as e:
            return False, f"Merge failed: {str(e)}"

    @staticmethod
    def split(pdf_path: str, output_folder: str) -> Tuple[bool, str]:
        """
        Split PDF into individual pages
        Returns: (success, message)
        """
        try:
            is_valid, error = PDFService.validate_file(pdf_path)
            if not is_valid:
                return False, error

            os.makedirs(output_folder, exist_ok=True)

            reader = PyPDF2.PdfReader(pdf_path)
            if len(reader.pages) == 0:
                return False, "PDF has no pages"

            base_name = os.path.splitext(os.path.basename(pdf_path))[0]

            for i, page in enumerate(reader.pages):
                writer = PyPDF2.PdfWriter()
                writer.add_page(page)
                output_path = os.path.join(
                    output_folder,
                    PDFService.get_safe_filename(f"{base_name}_page_{i+1}")
                )
                with open(output_path, "wb") as f:
                    writer.write(f)

            return True, f"Split {len(reader.pages)} pages to {output_folder}"

        except Exception as e:
            return False, f"Split failed: {str(e)}"

    @staticmethod
    def extract_text(pdf_path: str) -> Tuple[bool, str]:
        """
        Extract all text from PDF
        Returns: (success, text_or_error)
        """
        try:
            is_valid, error = PDFService.validate_file(pdf_path)
            if not is_valid:
                return False, error

            reader = PyPDF2.PdfReader(pdf_path)
            if len(reader.pages) == 0:
                return False, "PDF has no pages"

            text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {i+1} ---\n"
                    text += page_text

            if not text.strip():
                return False, "No text found in PDF (may be scanned image)"

            return True, text.strip()

        except Exception as e:
            return False, f"Extract failed: {str(e)}"

    @staticmethod
    def rename(pdf_path: str, new_name: str) -> Tuple[bool, str]:
        """
        Rename a PDF file
        Returns: (success, message)
        """
        try:
            is_valid, error = PDFService.validate_file(pdf_path)
            if not is_valid:
                return False, error

            if not new_name or not new_name.strip():
                return False, "Please enter a valid name"

            dir_path = os.path.dirname(pdf_path)
            safe_name = PDFService.get_safe_filename(new_name.strip())
            new_path = os.path.join(dir_path, safe_name)

            if os.path.exists(new_path):
                return False, f"File already exists: {safe_name}"

            os.rename(pdf_path, new_path)
            return True, f"Renamed to {safe_name}"

        except Exception as e:
            return False, f"Rename failed: {str(e)}"