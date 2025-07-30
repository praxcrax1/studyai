import cloudinary
import cloudinary.uploader
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

def upload_to_cloudinary(file_path: str, public_id: str) -> dict:
    return cloudinary.uploader.upload(
        file_path,
        public_id=public_id,
        resource_type="auto"
    )   