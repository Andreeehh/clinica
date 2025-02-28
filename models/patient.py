from pymongo import MongoClient
from dotenv import load_dotenv
import os 
load_dotenv() 
MONGO_URI = os.getenv('MONGO_URI')

client = MongoClient(MONGO_URI)
db = client['clinica_medica']
patients = db['patients']

class Patient:
    def __init__(self, name, dob, cpf, rg, street, neighborhood, street_number, phone, company_cnpj):
        self.name = name
        self.dob = dob
        self.cpf = cpf
        self.rg = rg
        self.street = street
        self.neighborhood = neighborhood
        self.street_number = street_number
        self.phone = phone
        self.company_cnpj = company_cnpj

    def save(self):
        patient_data = {
            "name": self.name,
            "dob": self.dob,
            "cpf": self.cpf,
            "rg": self.rg,
            "street": self.street,
            "neighborhood": self.neighborhood,
            "street_number": self.street_number,
            "phone": self.phone,
            "company_cnpj": self.company_cnpj
        }
        patients.insert_one(patient_data)

    @staticmethod
    def find_by_cpf(cpf):
        return patients.find_one({"cpf": cpf})

    @staticmethod
    def update_patient(cpf, update_data):
        patients.update_one({"cpf": cpf}, {"$set": update_data})

    @staticmethod
    def delete_patient(cpf):
        patients.delete_one({"cpf": cpf})