from abc import ABC, abstractmethod
import fitz  # PyMuPDF for PDF
from docx import Document
from pptx import Presentation
import os
import pdfplumber
import io


class FileLoader(ABC):
    """Abstract base class for loading different file types."""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.validate_file()
        self.file_name = os.path.basename(file_path)
        self.file_extension = os.path.splitext(file_path)[1].lower()
        
    def validate_file(self):
        """Validate if file exists and has correct extension."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        file_extension = os.path.splitext(self.file_path)[1].lower()
        expected_extension = self.get_expected_extension()
        
        if file_extension != expected_extension:
            raise ValueError(f"Invalid file type. Expected {expected_extension}, got {file_extension}")
    
    @abstractmethod
    def get_expected_extension(self):
        """Return the expected file extension for this loader."""
        pass
    
    @abstractmethod
    def load_file(self):
        """Load the file and return a handle or object for data extraction."""
        pass


class PDFLoader(FileLoader):
    """Concrete class for loading and processing PDF files."""
    
    def get_expected_extension(self):
        return ".pdf"
    
    def load_file(self):
        """Load PDF file using PyMuPDF (fitz)."""
        try:
            # Use both libraries for complete extraction
            fitz_doc = fitz.open(self.file_path)
            plumber_doc = pdfplumber.open(self.file_path)
            
            return {
                "fitz_doc": fitz_doc,
                "plumber_doc": plumber_doc,
                "file_name": self.file_name
            }
        except Exception as e:
            raise RuntimeError(f"Error loading PDF file: {str(e)}")


class DOCXLoader(FileLoader):
    """Concrete class for loading and processing DOCX files."""
    
    def get_expected_extension(self):
        return ".docx"
    
    def load_file(self):
        """Load DOCX file using python-docx."""
        try:
            doc = Document(self.file_path)
            return {
                "doc": doc,
                "file_name": self.file_name
            }
        except Exception as e:
            raise RuntimeError(f"Error loading DOCX file: {str(e)}")


class PPTLoader(FileLoader):
    """Concrete class for loading and processing PPT/PPTX files."""
    
    def get_expected_extension(self):
        return ".pptx"  # Supporting PPTX format (modern PowerPoint)
    
    def load_file(self):
        """Load PPTX file using python-pptx."""
        try:
            presentation = Presentation(self.file_path)
            return {
                "presentation": presentation,
                "file_name": self.file_name
            }
        except Exception as e:
            raise RuntimeError(f"Error loading PPTX file: {str(e)}")