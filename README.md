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
