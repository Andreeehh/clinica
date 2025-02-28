from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os 
load_dotenv() 
MONGO_URI = os.getenv('MONGO_URI')

client = MongoClient(MONGO_URI)
db = client['clinica_medica']
exams = db['exams']

class Exam:
    def __init__(self, patient_cpf, company_cnpj, exam_type, job_type, personal_background, absence_from_work, surgery, accidents, pcd, professional_background, hv, complaints, fisical, arterial_pressure, heart_rate, eyes, respiratory_system, circulatory_system, abdomen, osteoarticular_system, result):
        self.patient_cpf = patient_cpf
        self.company_cnpj = company_cnpj
        self.exam_type = exam_type
        self.job_type = job_type
        self.personal_background = personal_background
        self.absence_from_work = absence_from_work
        self.surgery = surgery
        self.accidents = accidents
        self.pcd = pcd
        self.professional_background = professional_background
        self.hv = hv
        self.complaints = complaints
        self.fisical = fisical
        self.arterial_pressure = arterial_pressure
        self.heart_rate = heart_rate
        self.eyes = eyes
        self.respiratory_system = respiratory_system
        self.circulatory_system = circulatory_system
        self.abdomen = abdomen
        self.osteoarticular_system = osteoarticular_system
        self.result = result
        self.date = datetime.now()

    def save(self):
        exam_data = {
            "patient_cpf": self.patient_cpf,
            "company_cnpj": self.company_cnpj,
            "exam_type": self.exam_type,
            "job_type": self.job_type,
            "personal_background": self.personal_background,
            "absence_from_work": self.absence_from_work,
            "surgery": self.surgery,
            "accidents": self.accidents,
            "pcd": self.pcd,
            "professional_background": self.professional_background,
            "hv": self.hv,
            "complaints": self.complaints,
            "fisical": self.fisical,
            "arterial_pressure": self.arterial_pressure,
            "heart_rate": self.heart_rate,
            "eyes": self.eyes,
            "respiratory_system": self.respiratory_system,
            "circulatory_system": self.circulatory_system,
            "abdomen": self.abdomen,
            "osteoarticular_system": self.osteoarticular_system,
            "result": self.result,
            "date": self.date
        }
        exams.insert_one(exam_data)

    @staticmethod
    def find_by_patient_cpf(patient_cpf):
        return exams.find({"patient_cpf": patient_cpf})