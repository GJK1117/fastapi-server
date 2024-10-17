from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from app.core.firebase import token_required
from app.schemas.upload_schemas import PDFUploadSchema
from app.service.prompt_generator import request_prompt
from app.service.ocr import OCR_PDF
from app.service.vision import process_files_and_analyze
from app.service.vectordb import create_or_load_user_vectorstore

router = APIRouter()

@router.post("/", dependencies=[Depends(token_required)])
async def pdf(requestbody: PDFUploadSchema, file: UploadFile = File(...)):
    """
    POST /upload/pdf
    PDF 학습자료를 기반으로 문제 생성 및 vectordb 생성
    
    Request Body:
        {
            "file": "file object",                  # 업로드된 PDF 파일
            "examSetting":                          # JSON 형식의 시험 설정 옵션, TODO: 안 쓰는 옵션은 수정 필요
            {
                {
                    multipleChoice: int,            # 객관식 수
                    shortAnswer: int,               # 단답형 수 
                    essay: int,                     # 서술형 수
                    examNumber: int,                # 문제 총 수
                    custom_prompt: "stirng",        # 사용자 커스텀 프롬프트
                    custom_image_prompt: "string",  # 이미지 처리에 대한 추가적인 커스텀 프롬프트
                    isTextCentered: int,            # 이미지 기반으로 자료를 인식하면 1, OCR 기반으로 자료를 인식하면 0
                    isLectureOnly: int,             # 문제 생성 시 지식 범위를 자료에 한정하면 1, 외부 추가적인 지식을 사용하면 0
                }
            }   
        }
    
    Returns:
        json: 
        {
            "case": int,                            # 문제 유형, 0이면 객관식, 1이면 주관식
            "question": "string",                   # 문제 명(제목)
            "choices": array of string or "string", # 문제 선지, 객관식의 경우 선택지 string이 배열로 주어지고, 주관식의 경우 "빈칸"으로 반환
            "correct_answer": int or "string",      # 문제의 답, 객관식의 경우 선택지 번호(int), 주관식의 경우 정답 string 반환  
            "explanation": "string",                # 문제의 답에 대한 해설
            "intent": "string"                      # 문제 생성 의도
        }
        
    Exceptions:
        400: 
            - {"error": "No file part"}: 요청에 'file' 부분이 없는 경우.
            - {"error": "No selected file"}: 파일이 선택되지 않은 경우.
            - {"error": "No examSetting found in the form data"}: 폼 데이터에 'examSetting'이 없는 경우.
            - {"error": "Invalid JSON format in examSetting"}: 'examSetting'이 유효한 JSON 형식이 아닌 경우.
    """
    if not file:
        return JSONResponse(content={"error": "No file part"}, status_code=400)
    
    try:
        # 파일을 비동기 방식으로 읽어들임
        pdf_content = await file.read()
        
        # OCR 또는 Vision 인식 방식 선택
        process_method = requestbody.examSetting.isTextCentered
        text = await OCR_PDF(pdf_content) if process_method == 0 else await process_files_and_analyze(pdf_content, file_type="pdf", is_pdf=True)
        
        # TEXT를 vectordb에 저장
        await create_or_load_user_vectorstore(user_id="example_user", text=text)
        
        # 문제 생성로직 작동
        result = await request_prompt(
            text,
            requestbody.examSetting.multipleChoice,
            requestbody.examSetting.shortAnswer,
            requestbody.examSetting.custom_prompt
        )
        
        # 문제 생성 결과를 저장할 리스트 초기화
        quiz_data = []
        for item in result["quiz_questions"]:
            quiz_data.append({
                "case": item["case"],
                "question": item["question"],
                "choices": item["choices"],
                "correct_answer": item["correct_answer"],
                "explanation": item["explanation"],
                "intent": item["intent"]
            })
        
        # 결과를 json구조로 생성하여 반환
        return JSONResponse(content={"quiz_data": quiz_data}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": f"Processing failed: {str(e)}"}, status_code=500)