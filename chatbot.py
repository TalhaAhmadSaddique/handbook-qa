import os
import dotenv
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient


dotenv.load_dotenv()
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_CLOUD_URL = os.getenv('QDRANT_CLOUD_URL')
openai_api_key = os.getenv('OPENAI_API_KEY')

def get_llm_resposne(user_input, _):
    query = user_input['text']
    
    # create embeddings of the user query
    embeddings_model = OpenAIEmbeddings(api_key=openai_api_key)
    embedded_query = embeddings_model.embed_query(query)

    # get reference, context
    qdrant_client = QdrantClient(
        api_key = QDRANT_API_KEY,
        url = QDRANT_CLOUD_URL
    )
    
    query_results = qdrant_client.search(collection_name="star_handbook", query_vector=embedded_query, limit=5)
    
    references = 'Page '
    context = ''
    for doc in query_results:
        references += f"{str(doc.payload['metadata']['page'])}, "
        context += doc.payload['page_content']
    
    # LLM integration Open AI
    client = OpenAI()

    prompt = f'''You are an intelligent Question Answering system for a Participant Handout. The user has asked you a question from the handbook and the most relevant snippet of the handbook related to the question
    has been extracted for you and reference page number is also provided. Given the handout context, refernces and the user query, provide a brief and accurate answer to the user query.
    Do not respond on your own if you do not know the answer. Do not respond to queries that are not found in the context. If query is not found in the handout then politely tell the user about it.
    You have to include the references that you use in your response. References are the page numbers on which the context is found.

    Context : 
    {context}
    
    References :
    {references}'''

    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
    )

    return response.choices[0].message.content