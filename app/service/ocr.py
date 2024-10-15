import pdf2image
import io
import asyncio
from PIL import Image
from google.cloud import vision
import logging

# Google Cloud Vision 클라이언트
client = vision.ImageAnnotatorClient()

# 로그 설정
logging.basicConfig(level=logging.INFO)

async def async_vision_request(image_content: bytes) -> str:
    """
    비동기 방식으로 Google Cloud Vision API를 호출하여 텍스트를 추출합니다.
    :param image_content: 이미지 파일의 내용 (bytes)
    :return: 추출된 텍스트
    """
    try:
        image = vision.Image(content=image_content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if response.error.message:
            logging.error(f"Error during Vision API call: {response.error.message}")
            return "Error during Vision API call."

        # 텍스트가 감지되었으면 반환
        if texts:
            return texts[0].description
        else:
            return "No text found"
    
    except Exception as e:
        logging.error(f"Unexpected error during Vision API call: {e}")
        return "Error processing the image."

async def OCR_image_byte(image_content: bytes) -> str:
    """
    이미지 파일의 내용에서 비동기 방식으로 텍스트를 추출합니다.
    :param image_content: 이미지 파일의 내용 (bytes)
    :return: 추출된 텍스트
    """
    try:
        return await async_vision_request(image_content)
    except Exception as e:
        logging.error(f"Error during image OCR: {e}")
        return "Error during image OCR."

async def OCR_images_byte(images_content: list[bytes]) -> str:
    """
    여러 이미지 파일의 내용에서 비동기 방식으로 텍스트를 추출합니다.
    :param images_content: 여러 이미지 파일의 내용 (bytes 리스트)
    :return: 각 이미지에서 추출된 텍스트의 리스트
    """
    try:
        tasks = [async_vision_request(image) for image in images_content]
        results = await asyncio.gather(*tasks)
        return " ".join(results)
    except Exception as e:
        logging.error(f"Error during multi-image OCR: {e}")
        return "Error during multi-image OCR."

async def OCR_PDF(pdf_content: bytes) -> str:
    """
    PDF 파일의 내용에서 비동기 방식으로 텍스트를 추출합니다.
    PDF의 내용을 이미지로 변환한 후 비동기 방식으로 이미지에서 텍스트를 추출합니다.
    :param pdf_content: PDF 파일의 내용 (bytes)
    :return: 추출된 텍스트 (string)
    """
    try:
        images = pdf2image.convert_from_bytes(pdf_content)

        # 이미지를 바이트로 변환
        def image_to_bytes(image: Image.Image) -> bytes:
            try:
                image_content = io.BytesIO()
                image.save(image_content, format='JPEG')
                return image_content.getvalue()
            except Exception as e:
                logging.error(f"Error converting image to bytes: {e}")
                raise e

        # 모든 이미지를 바이트로 변환 후 비동기 OCR 요청 실행
        images_bytes = [image_to_bytes(image) for image in images]
        return await OCR_images_byte(images_bytes)

    except pdf2image.exceptions.PDFInfoNotInstalledError as e:
        logging.error(f"PDF processing error (PDFInfo not installed): {e}")
        return "PDF processing error: PDFInfo not installed."
    except Exception as e:
        logging.error(f"Error during PDF OCR: {e}")
        return "Error during PDF OCR."