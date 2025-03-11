import io
import os
import csv
import base64
from PIL import Image
import re
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataExtractor:
    """Class to extract data from various file types."""
    
    def __init__(self, file_loader):
        """Initialize with a FileLoader instance."""
        self.file_loader = file_loader
        self.file_data = file_loader.load_file()
        self.file_name = self.file_data.get("file_name", "unknown")
        self.file_type = os.path.splitext(self.file_name)[1].lower()[1:]  # Get file type without dot
    
    def extract_text(self):
        """Extract text with metadata from the loaded file."""
        if hasattr(self.file_loader, 'get_expected_extension'):
            extension = self.file_loader.get_expected_extension()
            
            if extension == ".pdf":
                return self._extract_pdf_text()
            elif extension == ".docx":
                return self._extract_docx_text()
            elif extension == ".pptx":
                return self._extract_pptx_text()
        
        return []  # Return empty list if file type not supported
    
    def extract_links(self):
        """Extract hyperlinks with metadata from the loaded file."""
        if hasattr(self.file_loader, 'get_expected_extension'):
            extension = self.file_loader.get_expected_extension()
            
            if extension == ".pdf":
                return self._extract_pdf_links()
            elif extension == ".docx":
                return self._extract_docx_links()
            elif extension == ".pptx":
                return self._extract_pptx_links()
        
        return []  # Return empty list if file type not supported
    
    def extract_images(self, output_dir="output/images"):
        """Extract images with metadata from the loaded file."""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        if hasattr(self.file_loader, 'get_expected_extension'):
            extension = self.file_loader.get_expected_extension()
            
            if extension == ".pdf":
                return self._extract_pdf_images(output_dir)
            elif extension == ".docx":
                return self._extract_docx_images(output_dir)
            elif extension == ".pptx":
                return self._extract_pptx_images(output_dir)
        
        return []  # Return empty list if file type not supported
    
    def extract_tables(self):
        """Extract tables with metadata from the loaded file."""
        if hasattr(self.file_loader, 'get_expected_extension'):
            extension = self.file_loader.get_expected_extension()
            
            if extension == ".pdf":
                return self._extract_pdf_tables()
            elif extension == ".docx":
                return self._extract_docx_tables()
            elif extension == ".pptx":
                return self._extract_pptx_tables()
        
        return []  # Return empty list if file type not supported
    
    # PDF extraction methods
    def _extract_pdf_text(self):
        """Extract text from PDF files."""
        text_data = []
        fitz_doc = self.file_data.get("fitz_doc")
        
        for page_num, page in enumerate(fitz_doc):
            blocks = page.get_text("dict").get("blocks", [])
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text_data.append({
                                "page_number": page_num + 1,
                                "text": span.get("text", ""),
                                "font": span.get("font", ""),
                                "size": span.get("size", 0),
                                "color": span.get("color", ""),
                                "is_bold": "bold" in span.get("font", "").lower(),
                                "is_italic": "italic" in span.get("font", "").lower(),
                                "file_type": "pdf",
                                "file_name": self.file_name
                            })
        
        return text_data
    
    def _extract_pdf_links(self):
        """Extract hyperlinks from PDF files."""
        links_data = []
        fitz_doc = self.file_data.get("fitz_doc")
        
        if not fitz_doc:
            logger.warning("Fitz document not available for link extraction")
            return links_data
            
        for page_num, page in enumerate(fitz_doc):
            try:
                links = page.get_links() or []
                for link in links:
                    if "uri" in link:
                        # Extract text near the link using rect coordinates
                        rect = link.get("rect")
                        try:
                            linked_text = page.get_textbox(rect) if rect else "Unknown"
                        except Exception:
                            linked_text = "Unknown"
                        
                        links_data.append({
                            "page_number": page_num + 1,
                            "url": link["uri"],
                            "linked_text": linked_text.strip() if linked_text else "Unknown",
                            "rect": [round(coord, 2) for coord in rect] if rect else [],
                            "file_type": "pdf",
                            "file_name": self.file_name
                        })
            except Exception as e:
                logger.error(f"Error extracting links from page {page_num}: {e}")
        
        return links_data
    
    def _extract_pdf_images(self, output_dir):
        """Extract images from PDF files."""
        images_data = []
        fitz_doc = self.file_data.get("fitz_doc")
        
        if not fitz_doc:
            logger.warning("Fitz document not available for image extraction")
            return images_data
            
        for page_num, page in enumerate(fitz_doc):
            try:
                image_list = page.get_images(full=True) or []
                
                for img_idx, img_info in enumerate(image_list):
                    try:
                        xref = img_info[0]
                        base_image = fitz_doc.extract_image(xref)
                        if not base_image:
                            continue
                            
                        image_bytes = base_image.get("image")
                        if not image_bytes:
                            continue
                            
                        image_ext = base_image.get("ext", "png")
                        
                        # Save image to file
                        filename = f"pdf_{self.file_name.replace('.pdf', '')}_{page_num+1}_{img_idx+1}.{image_ext}"
                        filepath = os.path.join(output_dir, filename)
                        
                        with open(filepath, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        # Get image dimensions
                        try:
                            img = Image.open(io.BytesIO(image_bytes))
                            width, height = img.size
                        except Exception:
                            width, height = 0, 0
                        
                        images_data.append({
                            "page_number": page_num + 1,
                            "image_index": img_idx + 1,
                            "width": width,
                            "height": height,
                            "format": image_ext,
                            "file_path": filepath,
                            "file_type": "pdf",
                            "file_name": self.file_name
                        })
                    except Exception as e:
                        logger.error(f"Error extracting image {img_idx} from page {page_num}: {e}")
            except Exception as e:
                logger.error(f"Error getting images from page {page_num}: {e}")
        
        return images_data
    
    def _extract_pdf_tables(self):
        """Extract tables from PDF files using pdfplumber."""
        tables_data = []
        plumber_doc = self.file_data.get("plumber_doc")
        
        if not plumber_doc:
            logger.warning("PDFPlumber document not available for table extraction")
            return tables_data
            
        for page_num, page in enumerate(plumber_doc.pages):
            tables = page.extract_tables() or []
            
            for table_idx, table in enumerate(tables):
                if table:  # Ensure table is not empty
                    tables_data.append({
                        "page_number": page_num + 1,
                        "table_index": table_idx + 1,
                        "rows": len(table),
                        "columns": len(table[0]) if table and table[0] else 0,
                        "content": table,
                        "file_type": "pdf",
                        "file_name": self.file_name
                    })
        
        return tables_data
    
    # DOCX extraction methods
    def _extract_docx_text(self):
        """Extract text from DOCX files."""
        text_data = []
        doc = self.file_data.get("doc")
        
        # We don't have direct page numbers in docx, so we'll use paragraph index
        for para_idx, paragraph in enumerate(doc.paragraphs):
            if paragraph.text.strip():
                # Extract style information
                style_name = paragraph.style.name if paragraph.style else "Normal"
                is_heading = style_name.startswith("Heading")
                
                # Check for formatting in runs
                for run_idx, run in enumerate(paragraph.runs):
                    text_data.append({
                        "paragraph_index": para_idx + 1,
                        "run_index": run_idx + 1,
                        "text": run.text,
                        "style": style_name,
                        "is_bold": run.bold,
                        "is_italic": run.italic,
                        "is_heading": is_heading,
                        "heading_level": int(style_name[7:]) if is_heading and len(style_name) > 7 else None,
                        "file_type": "docx",
                        "file_name": self.file_name
                    })
        
        return text_data
    
    def _extract_docx_links(self):
        """Extract hyperlinks from DOCX files."""
        links_data = []
        doc = self.file_data.get("doc")
        
        for para_idx, paragraph in enumerate(doc.paragraphs):
            # Parse the paragraph's XML to extract hyperlinks
            if "_element" in dir(paragraph):
                xml = paragraph._element.xml
                soup = BeautifulSoup(xml, "xml")
                hyperlinks = soup.find_all("hyperlink")
                
                for link_idx, hyperlink in enumerate(hyperlinks):
                    # Get the relationship ID
                    rel_id = hyperlink.get("r:id")
                    if rel_id:
                        # Get the URL from relationships
                        target_url = ""
                        for rel in paragraph.part.rels:
                            if rel == rel_id:
                                target_url = paragraph.part.rels[rel].target_ref
                        
                        # Get the text of the hyperlink
                        link_text = ""
                        text_elements = hyperlink.find_all("t")
                        if text_elements:
                            link_text = " ".join([t.get_text() for t in text_elements])
                        
                        links_data.append({
                            "paragraph_index": para_idx + 1,
                            "link_index": link_idx + 1,
                            "url": target_url,
                            "linked_text": link_text,
                            "file_type": "docx",
                            "file_name": self.file_name
                        })
        
        return links_data
    
    def _extract_docx_images(self, output_dir):
        """Extract images from DOCX files."""
        images_data = []
        doc = self.file_data.get("doc")
        
        for rel_id, rel in doc.part.rels.items():
            if "image" in rel.target_ref:
                # Get image data
                image_part = rel.target_part
                image_bytes = image_part.blob
                
                # Determine image type from content_type
                img_format = image_part.content_type.split("/")[-1]
                if img_format == "jpeg":
                    img_format = "jpg"
                
                # Save image to file
                filename = f"docx_{self.file_name.replace('.docx', '')}_{rel_id}.{img_format}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, "wb") as img_file:
                    img_file.write(image_bytes)
                
                # Get image dimensions
                img = Image.open(io.BytesIO(image_bytes))
                width, height = img.size
                
                images_data.append({
                    "rel_id": rel_id,
                    "width": width,
                    "height": height,
                    "format": img_format,
                    "file_path": filepath,
                    "file_type": "docx",
                    "file_name": self.file_name
                })
        
        return images_data
    
    def _extract_docx_tables(self):
        """Extract tables from DOCX files."""
        tables_data = []
        doc = self.file_data.get("doc")
        
        for table_idx, table in enumerate(doc.tables):
            rows_data = []
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                rows_data.append(row_data)
            
            tables_data.append({
                "table_index": table_idx + 1,
                "rows": len(table.rows),
                "columns": len(table.rows[0].cells) if table.rows else 0,
                "content": rows_data,
                "file_type": "docx",
                "file_name": self.file_name
            })
        
        return tables_data
    
    # PPTX extraction methods
    def _extract_pptx_text(self):
        """Extract text from PPTX files."""
        text_data = []
        presentation = self.file_data.get("presentation")
        
        for slide_idx, slide in enumerate(presentation.slides):
            # Extract text from shapes
            for shape_idx, shape in enumerate(slide.shapes):
                if hasattr(shape, "text") and shape.text.strip():
                    # Check if it's a title or regular text
                    is_title = shape.name.startswith("Title") if hasattr(shape, "name") else False
                    
                    text_data.append({
                        "slide_number": slide_idx + 1,
                        "shape_index": shape_idx + 1,
                        "text": shape.text,
                        "is_title": is_title,
                        "shape_type": shape.name if hasattr(shape, "name") else "Unknown",
                        "file_type": "pptx",
                        "file_name": self.file_name
                    })
        
        return text_data
    
    def _extract_pptx_links(self):
        """Extract hyperlinks from PPTX files."""
        links_data = []
        presentation = self.file_data.get("presentation")
        
        for slide_idx, slide in enumerate(presentation.slides):
            for shape_idx, shape in enumerate(slide.shapes):
                # Check if shape has hyperlink
                if hasattr(shape, "click_action") and shape.click_action.hyperlink.address:
                    links_data.append({
                        "slide_number": slide_idx + 1,
                        "shape_index": shape_idx + 1,
                        "url": shape.click_action.hyperlink.address,
                        "linked_text": shape.text if hasattr(shape, "text") else "Unknown",
                        "file_type": "pptx",
                        "file_name": self.file_name
                    })
                
                # Check text runs for hyperlinks (for text with partial hyperlinks)
                if hasattr(shape, "text_frame") and hasattr(shape.text_frame, "paragraphs"):
                    for para_idx, paragraph in enumerate(shape.text_frame.paragraphs):
                        for run_idx, run in enumerate(paragraph.runs):
                            if hasattr(run, "hyperlink") and run.hyperlink.address:
                                links_data.append({
                                    "slide_number": slide_idx + 1,
                                    "shape_index": shape_idx + 1,
                                    "paragraph_index": para_idx + 1,
                                    "run_index": run_idx + 1,
                                    "url": run.hyperlink.address,
                                    "linked_text": run.text,
                                    "file_type": "pptx",
                                    "file_name": self.file_name
                                })
        
        return links_data
    
    def _extract_pptx_images(self, output_dir):
        """Extract images from PPTX files."""
        images_data = []
        presentation = self.file_data.get("presentation")
        
        for slide_idx, slide in enumerate(presentation.slides):
            for shape_idx, shape in enumerate(slide.shapes):
                # Check if shape is a picture
                if hasattr(shape, "image"):
                    # Get image data
                    image_bytes = shape.image.blob
                    
                    # Determine image type from content_type
                    img_format = "png"  # Default to png if can't determine
                    if shape.image.content_type:
                        img_format = shape.image.content_type.split("/")[-1]
                        if img_format == "jpeg":
                            img_format = "jpg"
                    
                    # Save image to file
                    filename = f"pptx_{self.file_name.replace('.pptx', '')}_{slide_idx+1}_{shape_idx+1}.{img_format}"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    # Get image dimensions
                    img = Image.open(io.BytesIO(image_bytes))
                    width, height = img.size
                    
                    images_data.append({
                        "slide_number": slide_idx + 1,
                        "shape_index": shape_idx + 1,
                        "width": width,
                        "height": height,
                        "format": img_format,
                        "file_path": filepath,
                        "file_type": "pptx",
                        "file_name": self.file_name
                    })
        
        return images_data
    
    def _extract_pptx_tables(self):
        """Extract tables from PPTX files."""
        tables_data = []
        presentation = self.file_data.get("presentation")
        
        for slide_idx, slide in enumerate(presentation.slides):
            table_idx = 0
            for shape in slide.shapes:
                if hasattr(shape, "table"):
                    table = shape.table
                    rows_data = []
                    for row in table.rows:
                        row_data = []
                        for cell in row.cells:
                            if cell.text_frame:
                                row_data.append(cell.text_frame.text)
                            else:
                                row_data.append("")
                        rows_data.append(row_data)
                    
                    tables_data.append({
                        "slide_number": slide_idx + 1,
                        "table_index": table_idx + 1,
                        "rows": len(table.rows),
                        "columns": len(table.columns),
                        "content": rows_data,
                        "file_type": "pptx",
                        "file_name": self.file_name
                    })
                    
                    table_idx += 1
        
        return tables_data