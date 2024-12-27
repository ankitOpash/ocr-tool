"""Image preprocessing module."""
import cv2
import numpy as np

class ImagePreprocessor:
    def preprocess(self, image):
        """Apply preprocessing steps to improve OCR accuracy."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, binary = cv2.threshold(gray, 0, 255, 
                                cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary)
        
        # Deskew if needed
        deskewed = self._deskew(denoised)
        
        return deskewed
    
    def _deskew(self, image):
        """Deskew the image if needed."""
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = 90 + angle
            
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h),
                                flags=cv2.INTER_CUBIC,
                                borderMode=cv2.BORDER_REPLICATE)
        
        return rotated