# Create file: backend/services/file_service.py
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
import mimetypes
import hashlib

class FileService:
    """Service for handling file uploads and management"""
    
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip', 'jpg', 'jpeg', 'png'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file(file):
        """Validate file before upload"""
        if not file:
            return False, "No file provided"
        
        if file.filename == '':
            return False, "No file selected"
        
        if not FileService.allowed_file(file.filename):
            allowed = ', '.join(FileService.ALLOWED_EXTENSIONS)
            return False, f"File type not allowed. Allowed types: {allowed}"
        
        # Check file size (requires reading the file)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > FileService.MAX_FILE_SIZE:
            max_mb = FileService.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb}MB"
        
        return True, None
    
    @staticmethod
    def generate_file_path(student_id, assessment_id, filename):
        """Generate unique file path"""
        # Extract extension
        ext = filename.rsplit('.', 1)[1].lower()
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        new_filename = f"submission_{student_id}_{assessment_id}_{timestamp}_{unique_id}.{ext}"
        
        # Create directory structure: uploads/submissions/YYYY/MM/
        year = datetime.utcnow().strftime('%Y')
        month = datetime.utcnow().strftime('%m')
        relative_path = os.path.join('submissions', year, month, new_filename)
        
        return relative_path, new_filename
    
    @staticmethod
    def save_submission_file(file, student_id, assessment_id):
        """Save uploaded file and return file info"""
        try:
            # Validate file
            is_valid, error_msg = FileService.validate_file(file)
            if not is_valid:
                return None, error_msg
            
            # Get file info
            original_filename = secure_filename(file.filename)
            file_size = file.seek(0, os.SEEK_END)
            file.seek(0)
            mime_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'
            
            # Generate file path
            relative_path, new_filename = FileService.generate_file_path(
                student_id, assessment_id, original_filename
            )
            
            # Create full path
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            full_path = os.path.join(upload_folder, relative_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Save file
            file.save(full_path)
            
            # Calculate file hash for integrity
            file_hash = FileService.calculate_file_hash(full_path)
            
            return {
                'file_path': relative_path,
                'file_name': original_filename,
                'file_size': file_size,
                'mime_type': mime_type,
                'file_hash': file_hash
            }, None
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None, f"Failed to save file: {str(e)}"
    
    @staticmethod
    def calculate_file_hash(file_path):
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def delete_file(file_path):
        """Delete a file"""
        try:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            full_path = os.path.join(upload_folder, file_path)
            
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

# Create instance
file_service = FileService()