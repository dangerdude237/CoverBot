from langchain_community.document_loaders import DataFrameLoader
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma
import chromadb
import spacy
import numpy as np
import pandas as pd
from langchain.prompts import PromptTemplate

class Retrival_Model_Class:
    def Transform_For_Embeddings(self,doc_text):
        nlp = spacy.load('en_core_web_md')
        for i in range(len(doc_text)):
            doc = nlp(doc_text[i])
            text = [token.text for token in doc if not token.is_stop and not token.is_punct]
            text = " ".join(text)
            doc_text[i] = text
        return doc_text

    def initialize_vector_database(self, resume_df):
        self.resume_df = resume_df
        self.loader = DataFrameLoader(self.resume_df, page_content_column="Resume")
        self.data = self.loader.load()
        self.doc_text = [doc.page_content for doc in self.data]
        self.doc_text_preprocessed = self.Transform_For_Embeddings(self.doc_text.copy())
        embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key = "<your_hugging_face_api_key>",
            model_name="avsolatorio/GIST-Embedding-v0"
        )
        query_result = embeddings.embed_documents(self.doc_text_preprocessed)
        query_numpy = np.array(query_result)
        query_list = query_numpy.tolist()
        ids = []
        for i in range(query_numpy.shape[0]):
            text = f"ids_{i+1}"
            ids.append(text)

        chroma_client = chromadb.Client()
        if "vector_collection_2" in [c.name for c in chroma_client.list_collections()]:
            chroma_client.delete_collection(name="vector_collection_2")
        collection = chroma_client.create_collection(name="vector_collection_2")

        collection.add(
        documents= self.doc_text,
        embeddings=query_list,
        ids=ids
        )

        langchainChroma = Chroma(client=chroma_client,embedding_function = embeddings, collection_name="vector_collection_2")
        retriever = langchainChroma.as_retriever(search_type='mmr', search_kwargs={"k": 3})

        return retriever
    
    def initialize_chain(self, llm):
        resume_df = pd.read_csv("gpt_dataset.csv")
        retriever = self.initialize_vector_database(resume_df)
        template = PromptTemplate(
        input_variables = ["context","job_description","resume"],
        template = """
        You are a chatbot that generates personalized cover letters. Your task is to create an effective and tailored cover letter based on the user’s resume, the provided job description, and a summary of what the role entails. The cover letter should be professional, concise, and align with the expectations for the role described in the job description. Make sure to highlight relevant skills, experiences, and qualifications from the resume, and structure the letter in a way that showcases the user's suitability for the job.

        Here is the required information:

        Job Description: {job_description}
        Resume: {resume}
        Context: {context}
        Using this information, craft a compelling cover letter that emphasizes the user's qualifications, aligns with the job description, and provides a strong narrative on why they are a great fit for the role.
        """
        )
        def format_docs(docs):
            return "\n".join([doc.page_content for doc in docs])


        def get_context(inputs):
            job_description = inputs["job_description"]
            retrieved_docs = retriever.get_relevant_documents(job_description)
            formatted_context = format_docs(retrieved_docs)
            return formatted_context
        
        chain = (
            {
                "context" : get_context,
                "job_description" : lambda inputs: inputs["job_description"],
                "resume" :  lambda inputs: inputs["resume"]
            }
            | template
            | llm
            | StrOutputParser()

        )

        return chain