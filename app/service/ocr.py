import pdf2image
import io
import asyncio
from PIL import Image
from google.cloud import vision

client = vision.ImageAnnotatorClient()

# Google Cloud Vision API 비동기 요청을 위한 httpx 비동기 클라이언트
async def async_vision_request(image_content: bytes) -> str:
    """
    비동기 방식으로 Google Cloud Vision API를 호출하여 텍스트를 추출합니다.
    :param image_content: 이미지 파일의 내용 (bytes)
    :return: 추출된 텍스트
    """
    image = vision.Image(content=image_content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    # 텍스트가 감지되었으면 반환
    if texts:
        return texts[0].description
    else:
        return "No text found"

async def OCR_image_byte(image_content: bytes) -> str:
    """
    이미지 파일의 내용에서 비동기 방식으로 텍스트를 추출합니다.
    :param image_content: 이미지 파일의 내용 (bytes)
    :return: 추출된 텍스트
    """
    return await async_vision_request(image_content)

async def OCR_images_byte(images_content: list[bytes]) -> str:
    """
    여러 이미지 파일의 내용에서 비동기 방식으로 텍스트를 추출합니다.
    :param images_content: 여러 이미지 파일의 내용 (bytes 리스트)
    :return: 각 이미지에서 추출된 텍스트의 리스트
    """
    tasks = [async_vision_request(image) for image in images_content]
    
    # asyncio.gather를 통해 여러 요청을 병렬로 비동기 처리
    results = await asyncio.gather(*tasks)
    return " ".join(results)

async def OCR_PDF(pdf_content: bytes) -> str:
    """
    PDF 파일의 내용에서 비동기 방식으로 텍스트를 추출합니다.
    PDF의 내용을 이미지로 변환한 후 비동기 방식으로 이미지에서 텍스트를 추출합니다.
    :param pdf_content: PDF 파일의 내용 (bytes)
    :return: 추출된 텍스트 (string)
    """
    images = pdf2image.convert_from_bytes(pdf_content)

    # 이미지를 바이트로 변환
    def image_to_bytes(image: Image.Image) -> bytes:
        image_content = io.BytesIO()
        image.save(image_content, format='JPEG')
        return image_content.getvalue()

    # 모든 이미지를 바이트로 변환 후 비동기 OCR 요청 실행
    images_bytes = [image_to_bytes(image) for image in images]
    return await OCR_images_byte(images_bytes)