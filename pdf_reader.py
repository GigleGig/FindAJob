import PyPDF2
import pdfplumber

class PDFReader:
    def __init__(self):
        pass
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """Extract text from PDF using PyPDF2"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as page_error:
                        print(f"Warning: Could not extract text from page {page_num + 1}: {page_error}")
                        continue
                
                return text.strip() if text.strip() else None
                
        except Exception as e:
            print(f"Error reading PDF with PyPDF2: {e}")
            return None
    
    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber (better for complex layouts)"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as page_error:
                        print(f"Warning: Could not extract text from page {page_num + 1} with pdfplumber: {page_error}")
                        continue
            
            return text.strip() if text.strip() else None
            
        except Exception as e:
            print(f"Error reading PDF with pdfplumber: {e}")
            return None
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF using the best available method"""
        print(f"Attempting to extract text from: {pdf_path}")
        
        # Try pdfplumber first (better for complex layouts)
        print("Trying pdfplumber...")
        text = self.extract_text_pdfplumber(pdf_path)
        
        # If pdfplumber fails, try PyPDF2
        if not text:
            print("pdfplumber failed, trying PyPDF2...")
            text = self.extract_text_pypdf2(pdf_path)
        
        if not text:
            raise Exception("Failed to extract text from PDF with both methods. The PDF might be image-based or corrupted.")
        
        print(f"Successfully extracted {len(text)} characters from PDF")
        return text