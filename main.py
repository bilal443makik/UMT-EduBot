from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.embeddings import HuggingFaceEmbeddings
import firebase_admin
from firebase_admin import credentials, db
import csv
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
cred = credentials.Certificate("myFYP.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "YOUR_FIREBASE_CREDENTIALS"  # Replace with your database URL
})
ref = db.reference("SST")
UPLOAD_CSV_FOLDER = 'uploads_CSV'

def get_context_retriever_chain(vector_store):
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$")
    retriever = vector_store.as_retriever()
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$2")
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation.")
    ])

    model = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.3)
    retriever_chain = create_history_aware_retriever(model, retriever, prompt)
    return retriever_chain

def get_conversational_rag_chain(retriever_chain):
    llm = ChatOpenAI(api_key=OPENAI_API_KEY)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Edu-bot for University of Management And Technology. Answer the user's questions based on the below context:\n\n{context}. Give correct answer in detail. Do not apologize very frequently. Make sure to answer correctly and avoid suggesting the user visit the website."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

def get_response(user_input, vector_store):
    chat_history = [
        AIMessage(content="Hello, I am a bot for the University. How can I help you?")
    ]
    retriever_chain = get_context_retriever_chain(vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)

    response = conversation_rag_chain.invoke({
        "chat_history": chat_history,
        "input": user_input
    })
    return response['answer']

def get_or_create_vector_db(folder_path, course_name):
    db_faiss_path = course_name
    # print("#########",db_faiss_path)
    print("1234")
    if os.path.exists(db_faiss_path):
        print("5678")
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}
            )
            print("<5678>")
            vector_store = FAISS.load_local(db_faiss_path, embeddings, allow_dangerous_deserialization=True)
            print("Embeddings found and loaded.")
        except Exception as e:
            print(f"Error loading FAISS vector store: {e}")
            return None
    else:
        try:
            os.makedirs(db_faiss_path, exist_ok=True)
            print("9876")
            print("$$$$$$$$$$$$$$$",folder_path)
            loader = PyPDFLoader(folder_path)
            print("9876")
            print("Embeddings not found. Creating new embeddings.")
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
            print("#### ---- Starting")
            texts = text_splitter.split_documents(docs)
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}
            )
            vector_store = FAISS.from_documents(texts, embeddings)
            print("#### ---- Mid Point")
            vector_store.save_local(db_faiss_path)
            print(f"Vector store created and saved at {db_faiss_path}.")
        except Exception as e:
            print(f"Error creating FAISS vector store: {e}")
            return None

    return vector_store
def add_teacher_course_with_files(teacher_id, course_code, pdf_path, csv_path, pdf_path_for_embed):
    
    vector_store = get_or_create_vector_db(pdf_path_for_embed, course_code)
    if not vector_store:
        print("Failed to create or load the vector store...")
        return
    else:
        print ("Success in Loading or Creating Vector Store, 200")
    ref = db.reference("SST")
    print("Let's Add Data to Database")
    course_ref = ref.child(teacher_id).child(course_code)
    students = []
    with open(csv_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            students.extend(row)
    print("*********************")
    students_dict = {student: "" for student in students}
    course_ref.set(students_dict)
    pdf_filename = os.path.basename(pdf_path)
    pdf_ref = course_ref.child("pdfFile")
    pdf_ref.set(pdf_filename)
    
    print(f"Course '{course_code}' and associated data added under TeacherID '{teacher_id}'")

def fetch_pdf_for_student(teacher_id, course_code, student_id):
    ref = db.reference("SST")
    course_ref = ref.child(teacher_id).child(course_code)
    
    if course_ref.get() is None:
        print("Course not found")
        return "Your Bot isn't Created"

    student_ref = course_ref.child(student_id)
    if student_ref.get() is None:
        print("Student ID not found")
        return "Your Bot isn't Created"
    
    pdf_filename = course_ref.child("pdfFile").get()
    if pdf_filename:
        pdf_path = f"{pdf_filename}"
        print(f"PDF Path: {pdf_path}")
        pdf_path = os.path.splitext(os.path.basename(pdf_path))[0]
        return pdf_path
    else:
        print("PDF file not found")
        return "Your Bot isn't Created"

def process_student_pdf_and_query(user_query, vector_store):
    response = get_response(user_query, vector_store)
    return response


@app.route('/add_teacher_course', methods=['POST'])
def add_teacher_course():
    # data = request.get_json()
    teacher_id = request.form.get('teacher_id')
    course_code = request.form.get('course_code')
    pdf_file = request.files['pdf_file']
    csv_file = request.files['csv_path']
    #################################3
    # Create the uploads folder if it doesn't exist
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    # Save the PDF file to the uploads folder
    pdf_path = os.path.join("uploads", pdf_file.filename)
    pdf_file.save(pdf_path)
    pdf_path_for_embed = f"uploads\{pdf_file.filename}"
    #################
    os.makedirs(UPLOAD_CSV_FOLDER, exist_ok=True)
    if csv_file:
        csv_path = os.path.join(UPLOAD_CSV_FOLDER, csv_file.filename)
        csv_file.save(csv_path)
        csv_path_for = f"uploads_CSV\{csv_file.filename}"
    else:
        return ("Please Try to Upload the CSV Again"), 404

    add_teacher_course_with_files(teacher_id, course_code, pdf_path, csv_path_for, pdf_path_for_embed)

    return jsonify({'message': f"Course '{course_code}' and associated data added under TeacherID '{teacher_id}'"}), 200

# @app.route('/add_teacher_course', methods=['POST'])
# def add_teacher_course():
#     # data = request.get_json()
#     teacher_id = request.form.get('teacher_id')
#     course_code = request.form.get('course_code')
#     pdf_path = request.form.get('pdf_path')
#     csv_path = request.form.get('csv_path')
    
#     add_teacher_course_with_files(teacher_id, course_code, pdf_path, csv_path)
    
#     return jsonify({'message': f"Course '{course_code}' and associated data added under TeacherID '{teacher_id}'"}), 200


@app.route('/process_query', methods=['POST'])
def process_query():
    # data = request.get_json()
    user_query = request.form.get('user_query')
    teacher_id = request.form.get('teacher_id')
    course_code = request.form.get('course_code')
    student_id = request.form.get('student_id')
    print ("#######1")
    student_pdf_path = fetch_pdf_for_student(teacher_id, course_code, student_id)
    print ("#######2")
    if student_pdf_path == "Your Bot isn't Created":
        return jsonify({'error': "Your Bot isn't Create or You Do not have the Access"}), 404
    print ("#######3")   
    print("####$$$$", student_pdf_path)
    vector_store = get_or_create_vector_db(student_pdf_path, course_code)
    # retriever_chain = get_context_retriever_chain(vector_store)
    print("#################################################", vector_store)
    
    if not vector_store:
        return jsonify({'error': 'Failed to create or load the vector store'}), 500
    print ("#######4")
    response = process_student_pdf_and_query(user_query, vector_store)
    
    return jsonify({'response': response}), 200

# def main():
#     pdf_file = "Doc1.pdf"
#     teacher_id = "v1020"
#     course_code = "Pk101"
#     csv_file = "students.csv"

#     add_teacher_course_with_files(teacher_id, course_code, pdf_file, csv_file)
    
#     student_id = "f2020376041"
#     student_pdf_path = fetch_pdf_for_student(teacher_id, course_code, student_id)
#     if student_pdf_path == "Your Bot isn't Created":
#         print(student_pdf_path)
#         return

#     vector_store = get_or_create_vector_db(student_pdf_path, course_code)
#     if not vector_store:
#         print("Failed to create or load the vector store. Exiting.")
#         return

#     user_query = "What is the name of the course and who is the course instructor?"

#     if user_query:
#         response = process_student_pdf_and_query(user_query, vector_store)
#         print("************************", response)


if __name__ == "__main__":
    app.run(port=8000, debug=True)