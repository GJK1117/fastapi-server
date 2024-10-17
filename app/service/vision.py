import base64
import io
import pdf2image
import asyncio
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.schema import HumanMessage, SystemMessage
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# PDF 또는 이미지 파일을 변환하고 OpenAI API를 호출하는 통합 함수
async def process_files_and_analyze(file_content: bytes, is_pdf: bool = False, custom_prompt: str = ""):
    """
    PDF 또는 이미지 파일을 변환하여 OpenAI API를 통해 분석하는 함수
    Args:
        file_content (bytes): 업로드된 파일(PDF 또는 이미지)의 내용
        is_pdf (bool): PDF 여부
        custom_prompt (str): 사용자 정의 프롬프트
    Returns:
        str: 분석된 결과
    """
    try:
        # PDF 파일인 경우 이미지를 추출하고 비동기적으로 처리
        if is_pdf:
            images = await convert_pdf_to_images_async(file_content)
        else:
            images = [file_content]

        # 비동기적으로 OpenAI API를 호출하여 분석
        tasks = [analyze_image_with_openai(image, is_pdf=is_pdf, custom_prompt=custom_prompt) for image in images]
        results = await asyncio.gather(*tasks)
        return " ".join(results)

    except Exception as e:
        logging.error(f"Error during file processing: {e}")
        raise RuntimeError("File processing failed")

# PDF 파일을 비동기적으로 이미지로 변환하는 함수
async def convert_pdf_to_images_async(pdf_content: bytes):
    loop = asyncio.get_event_loop()
    images = await loop.run_in_executor(None, pdf2image.convert_from_bytes, pdf_content)
    return images

# 이미지를 base64로 인코딩하고 OpenAI API를 비동기적으로 호출하는 함수
async def analyze_image_with_openai(image, is_pdf=False, custom_prompt=""):
    try:
        # 이미지가 PDF에서 추출된 것인지 여부에 따라 처리
        if is_pdf:
            image_content = io.BytesIO()
            image.save(image_content, format='JPEG')
            image_content = image_content.getvalue()
        else:
            image_content = image

        base64_image = base64.b64encode(image_content).decode('utf-8')

        # OpenAI 프롬프트 생성 및 요청
        return await request_prompt_img_detecting_async(base64_image, custom_prompt)

    except Exception as e:
        logging.error(f"Error during image analysis: {e}")
        raise RuntimeError("Image analysis failed")

# OpenAI API에 프롬프트를 비동기적으로 요청하는 함수
async def request_prompt_img_detecting_async(contents: str, custom_prompt=""):
    try:
        # OpenAI 모델 생성
        llm = ChatOpenAI(
            model_name="gpt-4o-2024-08-06",
            temperature=0.2,
            streaming=False,
        )

        # 프롬프트 생성
        system_prompt = f"Analyze the following image:\n{custom_prompt}"
        message = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=[
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{contents}"}}
            ])
        ]

        # OpenAI API 호출 및 응답 파싱
        response = await llm.agenerate(message)
        output_parser = JsonOutputParser()
        parsed_response = output_parser.parse(response.content)
        return parsed_response['image_detections']

    except Exception as e:
        logging.error(f"Error during OpenAI request: {e}")
        raise RuntimeError("Failed to process image prompt")