from pymongo import MongoClient
from dotenv import load_dotenv
import os 
load_dotenv() 
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['clinica_medica']
companies = db['companies']

class Company:
    def __init__(self, name, social_reason, cnpj, phone, address, email):
        self.name = name
        self.social_reason = social_reason
        self.cnpj = cnpj
        self.phone = phone
        self.address = address
        self.email = email

    def save(self):
        company_data = {
            "name": self.name,
            "social_reason": self.social_reason,
            "cnpj": self.cnpj,
            "phone": self.phone,
            "address": self.address,
            "email": self.email
        }
        companies.insert_one(company_data)

    @staticmethod
    def find_by_cnpj(cnpj):
        return companies.find_one({"cnpj": cnpj})