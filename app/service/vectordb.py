from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging

# 로그 설정
logging.basicConfig(level=logging.INFO)

# 사용자별로 컬렉션 생성 및 임베딩/벡터 저장 (비동기 처리)
async def create_or_load_user_vectorstore(user_id: str, docs: list):
    try:
        # 사용자 ID에 맞는 컬렉션 생성/로드
        collection_name = f"user_{user_id}_collection"

        # 문자열 리스트를 Document 객체 리스트로 변환
        documents = [Document(page_content=doc) for doc in docs]

        # 텍스트 분할기 사용
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)

        # 비동기 OpenAI 임베딩 모델 사용
        embeddings = OpenAIEmbeddings()

        # Chroma 벡터 저장소 생성 (await 제거)
        vectorstore = Chroma(
            persist_directory=f"./chroma_vectorstore/{user_id}",
            embedding_function=embeddings,
            collection_name=collection_name
        )

        # 비동기 문서 추가
        await vectorstore.aadd_documents(splits)
        logging.info(f"Documents successfully added for user {user_id}.")
        
        return vectorstore

    except ValueError as ve:
        logging.error(f"ValueError occurred for user {user_id}: {ve}")
        raise ve  # 필요에 따라 오류 재발생 가능
    except Exception as e:
        logging.error(f"Unexpected error occurred for user {user_id}: {e}")
        raise e  # 다른 모든 예외를 캐치하여 로깅
    finally:
        logging.info(f"Finished processing user {user_id}'s documents.")

# 사용자별로 벡터 검색 수행 (비동기 처리)
async def search_in_user_collection(user_id: str, query: str):
    try:
        collection_name = f"user_{user_id}_collection"

        # 비동기 OpenAI 임베딩 모델 사용
        embeddings = OpenAIEmbeddings()

        # Chroma 벡터 저장소 불러오기 (await 제거)
        vectorstore = Chroma(
            persist_directory=f"./chroma_vectorstore/{user_id}",
            embedding_function=embeddings,
            collection_name=collection_name
        )

        # 질문에 대한 유사도 검색 비동기 처리
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        results = await retriever.aget_relevant_documents(query)

        # 검색된 문서 출력
        logging.info(f"Search successfully performed for user {user_id}.")
        return [{"result_idx": idx + 1, "content": doc.page_content} for idx, doc in enumerate(results)]

    except ValueError as ve:
        logging.error(f"ValueError during search for user {user_id}: {ve}")
        raise ve
    except Exception as e:
        logging.error(f"Unexpected error occurred during search for user {user_id}: {e}")
        raise e
    finally:
        logging.info(f"Search operation completed for user {user_id}.")