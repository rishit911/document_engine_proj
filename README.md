
# 🧠 Intelligent Document Engine

An **end-to-end serverless document intelligence pipeline** built on AWS. This project enables organizations to extract, process, and search financial documents using modern AI techniques, semantic search, and scalable cloud infrastructure.

---

## 📌 Project Summary

This project automates intelligent document understanding in two parts:

### 🔹 Part 1: Document Upload & Text Extraction

Users upload documents (PDFs, scanned files) to an **S3 bucket**. This triggers a Lambda function `doc-upload-processor`, which uses **Amazon Textract** to extract the text and store the results in **DynamoDB**.

| Component           | Description |
|---------------------|-------------|
| **Input**           | PDF/Scanned Financial Reports uploaded to S3 |
| **Trigger**         | S3 PUT Event triggers Lambda |
| **Text Extraction** | **Amazon Textract** extracts printed or handwritten text |
| **Storage**         | Text + Document Name → Stored in DynamoDB Table    `DocumentTextTable` |

### Why Textract?
- ✅ Extracts text from scanned documents, tables, and forms
- ✅ No templates or configuration required
- ✅ Handles low-quality scanned reports
- ✅ Output is structured and accurate

---

### 🔹 Part 2: Semantic Search and Q&A

After extraction, the documents are embedded using a **SentenceTransformer MiniLM model**. This is done using a **SageMaker Notebook** (`generate_embeddings.ipynb`), and the embeddings are pushed to **OpenSearch**.

| Component        | Description |
|------------------|-------------|
| **Model**        | SentenceTransformer MiniLM v2 (loaded from S3) |
| **Embedding**    | Generated for each document text |
| **Vector DB**    | Embeddings stored in OpenSearch index `documents-index` |
| **UI**           | Streamlit App for semantic Q&A |
| **Query**        | Encoded query is matched to most relevant text using KNN search |

---

## 🧰 Technologies Used

- **AWS Lambda** – Document processing trigger
- **Amazon Textract** – Extracts text from PDFs/scanned docs
- **Amazon S3** – File storage (user uploads + ML model)
- **Amazon DynamoDB** – Stores extracted document text
- **Amazon SageMaker** – Embedding generation
- **OpenSearch** – Vector store + KNN search
- **Streamlit** – User interface
- **SentenceTransformers** – MiniLM for encoding documents and queries
- **Boto3, opensearch-py** – Python SDKs for AWS + OpenSearch

---
