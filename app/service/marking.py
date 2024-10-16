import asyncio
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.pipeline import PipelinePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from prompt import marking_problem
from app.core.config import OPENAI_API_KEY
import logging

# OpenAI API 설정
chat = ChatOpenAI(
    model_name="gpt-4o",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.1,
    streaming=True
)

async def initialize_feedback():
    feedback = marking_problem()
    
    # 객관식 및 주관식 문제에 대한 프롬프트 설정
    objective_prompts = [
        ("intro", PromptTemplate.from_template(feedback.objective_intro)),
        ("start", PromptTemplate.from_template(feedback.start))
    ]
    
    subjective_prompts = [
        ("intro", PromptTemplate.from_template(feedback.subjective_intro)),
        ("start", PromptTemplate.from_template(feedback.start))
    ]

    # PipelinePromptTemplate 구성
    objective_full_prompt = PipelinePromptTemplate(
        final_prompt=PromptTemplate.from_template(feedback.final),
        pipeline_prompts=objective_prompts
    )
    
    subjective_full_prompt = PipelinePromptTemplate(
        final_prompt=PromptTemplate.from_template(feedback.final),
        pipeline_prompts=subjective_prompts
    )

    output_parser = JsonOutputParser()
    
    return objective_full_prompt, subjective_full_prompt, output_parser

# 문제 채점을 수행하는 비동기 함수
async def feedback_main(thread_count, input_json):
    # 초기 설정을 비동기적으로 수행
    objective_full_prompt, subjective_full_prompt, output_parser = await initialize_feedback()

    # 문제 수만큼 비동기적으로 응답 생성 (API 요청을 비동기 처리)
    tasks = [feedback_split(x, objective_full_prompt, subjective_full_prompt, output_parser) for x in input_json]
    response = await asyncio.gather(*tasks)
    
    return response

async def feedback_split(input_json, objective_full_prompt, subjective_full_prompt, output_parser):
    # 주관식 문제 채점 (비동기 API 요청)
    if input_json["choices"] == "빈칸":
        return await feedback_subjective(input_json, subjective_full_prompt, output_parser)
    # 객관식 문제 채점 (비동기 API 요청)
    else:
        return await feedback_objective(input_json, objective_full_prompt, output_parser)

# 객관식 문제 채점 함수 (비동기 처리)
async def feedback_objective(input_json, full_prompt, output_parser):
    chain = full_prompt | chat
    try:
        result = await chain.agenerate({"question": input_json})
        parsed_response = output_parser.parse(result.content)
        return parsed_response
    except Exception as e:
        logging.error(f"Error during objective feedback processing: {e}")
        raise RuntimeError("Objective feedback processing failed")

# 주관식 문제 채점 함수 (비동기 처리)
async def feedback_subjective(input_json, full_prompt, output_parser):
    chain = full_prompt | chat
    try:
        result = await chain.agenerate({"question": input_json})
        parsed_response = output_parser.parse(result.content)
        return parsed_response
    except Exception as e:
        logging.error(f"Error during subjective feedback processing: {e}")
        raise RuntimeError("Subjective feedback processing failed")