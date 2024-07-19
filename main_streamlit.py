import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
import qdrant_client
from langchain_community.vectorstores import Qdrant

load_dotenv()
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_CLOUD_URL = os.getenv('QDRANT_CLOUD_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# helosassaß
st.title("Stickball STAR Handbook Chatbot")
with st.expander(label='Disclaimer',
            expanded=False) as s:
    st.markdown('''This chatbot is developed to assist with queries related to the Stickball STAR Handbook. It is designed to help you find information and answer questions specific to the content of the handbook. Please note that the responses are based on the information contained within the handbook and may not cover every possible scenario or query. For detailed guidance or specific issues, please refer directly to the handbook or consult with a Stickball representative.''')

client = OpenAI(api_key=OPENAI_API_KEY)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    # print(prompt)
    # print(prompt := st.chat_input("What is up?"))
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        
        # create embeddings of the user query
        embeddings_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        embedded_query = embeddings_model.embed_query(prompt)

        # get reference, context
        # qdrant_client = QdrantClient(
        #     api_key = QDRANT_API_KEY,
        #     url = QDRANT_CLOUD_URL
        # )
        
        # query_results = qdrant_client.search(collection_name="star_handbook", query_vector=embedded_query, limit=5)
        from langchain_qdrant import QdrantVectorStore
        qclient = qdrant_client.QdrantClient(url=QDRANT_CLOUD_URL, api_key=QDRANT_API_KEY)
        qdrant = Qdrant(client=qclient, collection_name="star_handbook", embeddings=embeddings_model)
        query_results = qdrant.similarity_search(prompt)

        # qdrant = QdrantVectorStore.from_existing_collection(
        #     client=client,
        #     embeddings=embeddings_model,
        #     collection_name="star_handbook",
        #     url=QDRANT_CLOUD_URL,
        #     api_key=QDRANT_API_KEY
        # )

        # query_results = qdrant.similarity_search(prompt)


        references = 'Page '
        context = ''
        for doc in query_results:
            print(doc)
            references += f"{str(doc.metadata['page'])}, "
            context += doc.page_content #payload['page_content']
        
        system_prompt = f'''You are an intelligent Question Answering system for a Participant Handout. The user has asked you a question from the handbook and the most relevant snippet of the handbook related to the question
has been extracted for you and reference page number is also provided. Given the handout context, chat history, refernces and the user query, provide a brief and accurate answer to the user query.
Do not respond on your own if you do not know the answer. Do not respond to queries that are not found in the context. If query is not found in the handout then politely tell the user about it.
You have to include the references that you use in your response. References are the page numbers on which the context is found.

Context : 
{context}

References :
{references}'''

        all_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        all_messages.extend([
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ])
        
        # print(all_messages)
        
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=all_messages,
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})