from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os 
load_dotenv() 
MONGO_URI = os.getenv('MONGO_URI')

client = MongoClient(MONGO_URI)
db = client['clinica_medica']
queue = db['queue']

class Queue:
    def __init__(self, patient_cpf, exam_type, job_type):
        self.patient_cpf = patient_cpf
        self.exam_type = exam_type
        self.job_type = job_type
        self.entry_time = datetime.now()

    def save(self):
        queue_data = {
            "patient_cpf": self.patient_cpf,
            "entry_time": self.entry_time
        }
        queue.insert_one(queue_data)

    @staticmethod
    def get_next_patient():
        return queue.find_one(sort=[("entry_time", 1)])

    @staticmethod
    def remove_patient(patient_cpf):
        queue.delete_one({"patient_cpf": patient_cpf})