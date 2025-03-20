"Handle uploaded files in Streamlit"
import os
import tempfile
from pathlib import Path

class FileHandler:
    """Class to handle file operations for Streamlit uploads."""
    @staticmethod
    def save_uploaded_file(uploaded_file):
        "Save the uploaded file to a temporary directory"
        try:
            temp_dir = Path(tempfile.gettempdir()) / "streamlit_uploads"
            temp_dir.mkdir(parents=True, exist_ok=True)

            file_extension = Path(uploaded_file.name).suffix
            temp_file_path = temp_dir / f"temp_upload_{hash(uploaded_file.name)}{file_extension}"

            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            temp_file_path.chmod(0o644)
            return str(temp_file_path.absolute())
        except (OSError, IOError):
            return None

    @staticmethod
    def cleanup_temp_files(file_path):
        "Remove the temporary file"
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass