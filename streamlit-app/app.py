import streamlit as st
import boto3
import json
import os
from io import BytesIO
import tempfile
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# --- AWS and OpenSearch Config ---
region = 'us-east-1'
service = 'es'
bucket_name = 'doc-engine-bucket-risbur'
model_key = 'lambda-models/saved_model_miniLM_v2/'
host = 'search-doc-engine-domain-qyqfyw22tidthpfu7cgcattlwq.us-east-1.es.amazonaws.com'
index_name = 'documents-index'

# --- Authentication ---
session = boto3.Session()
credentials = session.get_credentials().get_frozen_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

# --- Load Model from S3 ---
def load_model_from_s3():
    s3 = boto3.client('s3')
    with tempfile.TemporaryDirectory() as tmpdir:
        model_dir = os.path.join(tmpdir, 'saved_model_miniLM_v2')
        os.makedirs(model_dir, exist_ok=True)
        
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=model_key)
        for obj in response.get('Contents', []):
            key = obj['Key']
            if key.endswith('/'):
                continue
            target_path = os.path.join(model_dir, os.path.relpath(key, model_key))
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            s3.download_file(bucket_name, key, target_path)
        
        return SentenceTransformer(model_dir)

# --- OpenSearch Client ---
client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# --- Financial Keywords ---
financial_keywords = [
    "net profit", "net income", "revenue", "expenses", "loss", "gain",
    "total sales", "EBITDA", "operating income", "income before tax",
    "earnings", "fiscal", "gross margin", "quarterly result"
]

# --- Search Logic ---
def search_financial_info(query):
    query_embedding = model.encode(query).tolist()

    search_query = {
        "size": 3,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding,
                    "k": 3
                }
            }
        },
        "_source": ["text", "fileName"]
    }

    try:
        response = client.search(index=index_name, body=search_query)
        hits = response['hits']['hits']
        if not hits:
            return "⚠️ No relevant documents found."

        all_lines = []
        for hit in hits:
            text = hit['_source']['text']
            lines = text.split('\n')
            all_lines.extend(lines)

        best_line = None
        for line in all_lines:
            if any(keyword in line.lower() for keyword in financial_keywords):
                if "net profit" in query.lower() and "net profit" in line.lower():
                    return f"📌 Most Relevant Line: {line.strip()}"
                elif "revenue" in query.lower() and "revenue" in line.lower():
                    return f"📌 Most Relevant Line: {line.strip()}"
                elif any(word in query.lower() for word in ["loss", "expenses", "income"]) and any(k in line.lower() for k in financial_keywords):
                    return f"📌 Most Relevant Line: {line.strip()}"
                elif not best_line:
                    best_line = line

        return f"📎 Related Line: {best_line.strip()}" if best_line else "🔍 No relevant lines found."

    except Exception as e:
        return f"❌ OpenSearch error: {str(e)}"

# --- Streamlit UI ---
st.set_page_config(page_title="📊 Financial Document QA", layout="centered")
st.title("📑 Ask Questions About Financial Documents")

st.markdown("📘 This tool intelligently searches all indexed financial reports for answers to your questions.")

# Load model from S3
with st.spinner("🔁 Loading SentenceTransformer model from S3..."):
    model = load_model_from_s3()

# Ask a question
query = st.text_input("❓ Enter your question about financials")
if st.button("🔍 Search"):
    if not query.strip():
        st.warning("⚠️ Please enter a valid question.")
    else:
        with st.spinner("🔎 Searching documents..."):
            result = search_financial_info(query)
        st.success(result)
