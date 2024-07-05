<img width="700" alt="EmailRejection" src="https://github.com/bilal443makik/UMT-EduBot/assets/141304031/63b19d1c-3904-48ec-bac3-b5f1c67df128">**#University of Management and Technology Edu-Bot**
# UMT-EduBot
I have Developed Edu-Bot for UMT (for my University in my FYP) in which Teacher Can Add Course Content in the form pdfs and add a List of Student Ids (Students Enrolled in the Respective Course) and then those Students log-in with their University IDs (University Emails) and Select the Course in which they are enrolled and then chat with the bot. 

#Creating Embeddings by using Sentence Transformer 
I have Used Langchian_Embdedings for creating the Embeddings and save this to the FAISS (Facebook Artificial Intelligence Semilarity Search) 

#Saving the Embeddings Locally 
I have save these embeddings locally in my repository with the name of that Document (In my case I have Used the Course Code by which Folder is created and embeddings are saved there)
-My Future Approach will be: I'll host these embeddings on firebase or mongoDB, so that embeddings will secure and no fear of container crash (during Production)

#Teancher and Students Approached
-Teacher: Teacher will input their UniqueID, Course_Code, list of Students enrolled in that specific Course and the pdfs of Documents from which Students will Query. Teacher can also query and can Make Quiz and Assignments from that Bot
-Students: Students will input their Student_ID that will be used for checking wherater he have th access of not respective to the Course Code he will also input and then they can Query the ChatBot and start their prepration of their respective course.

#Architecture of RAG Model We Use
<img width="732" alt="ffff" src="https://github.com/bilal443makik/UMT-EduBot/assets/141304031/6f2a9a36-c734-430b-bf13-3e710fe39993">

#Prompt Engineering
<img width="362" alt="promptDia" src="https://github.com/bilal443makik/UMT-EduBot/assets/141304031/6e4202cd-76fb-4bbf-b8fc-84e66af5ef32">
