from pydantic import BaseModel
from typing import Optional

# ExamSetting 스키마 정의
class ExamSetting(BaseModel):
    multipleChoice: int
    shortAnswer: int
    essay: int
    examNumber: int
    custom_prompt: Optional[str] = ""
    custom_image_prompt: Optional[str] = ""
    isTextCentered: int
    isLectureOnly: int

# PDF 업로드 및 ExamSetting 스키마
class PDFUploadSchema(BaseModel):
    examSetting: ExamSetting