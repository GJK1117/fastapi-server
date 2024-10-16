from langchain_openai.chat_models import ChatOpenAI
from langchain.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from app.service.prompt import make_problem_prompt
from langchain.schema import (
    HumanMessage,
    SystemMessage
)
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 각 옵션을 개별 매개변수로 받는 함수
async def request_prompt(contents: str, multiple_choice: int, short_answer: int, custom_prompt: str):
    try:
        # 비동기 OpenAI 모델 호출
        llm = ChatOpenAI(
            model_name="gpt-4o-2024-08-06", 
            temperature=0.7,
            streaming=False,
        )
        
        # 문제 생성 프롬프트
        prompt = make_problem_prompt(contents, multiple_choice, short_answer)
        prompt.set_custom_prompt(custom_prompt)
        
        # 시스템 프롬프트와 사용자 입력 가져오기
        system_prompt = prompt.get_system_prompt()
        user_input = prompt.get_user_input()

        output_parser = JsonOutputParser()

        # PromptTemplate 설정
        prompt_template = PromptTemplate(
            template="{system_prompt}\n\n{format_instructions}\n\n{user_input}",
            input_variables=["system_prompt", "user_input"],
            partial_variables={"format_instructions": output_parser.get_format_instructions()},
        )

        # 최종 프롬프트 생성
        _prompt = prompt_template.format(system_prompt=system_prompt, user_input=user_input)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=_prompt)
        ]

        # 비동기 처리
        response = await llm.agenerate(messages)
        parsed_response = output_parser.parse(response.content)

        return parsed_response

    except Exception as e:
        logging.error(f"Error during prompt request: {e}")
        raise RuntimeError("Error processing the request.")