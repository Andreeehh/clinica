from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from pymongo import MongoClient
from models.patient import Patient
from models.queue import Queue
from models.company import Company
from models.exam import Exam
from datetime import datetime
import pytz
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from dotenv import load_dotenv
import os 
load_dotenv() 
MONGO_URI = os.getenv('MONGO_URI')

# Define o fuso horário de São Paulo
saopaulo_tz = pytz.timezone('America/Sao_Paulo')

app = Flask(__name__)

# Conexão com o MongoDB
client = MongoClient(MONGO_URI)
db = client['clinica_medica']
queue_collection = db['queue'] 
patients = db['patients']
companies = db['companies']  
exams = db['exams']

# Rota para a fila de atendimento
@app.route('/queue')
def queue_page():  # Alterado para evitar conflito com a variável do banco
    queue_list = list(queue_collection.find().sort("entry_time", 1))
    return render_template('queue.html', queue=queue_list)

def mask_cpf(cpf):
    """Mascarar CPF, deixando apenas os 3 primeiros e os 2 últimos números visíveis."""
    if len(cpf) == 14:
        return f"{cpf[:3]}.XXX.XXX-{cpf[-2:]}"
    return "CPF inválido"

@app.route('/attend_patient', methods=['POST'])
def attend_patient():
    # Busca o próximo paciente da fila e remove da collection
    next_patient = Queue.get_next_patient()

    if not next_patient:
        return jsonify({"message": "Nenhum paciente na fila"}), 400

    cpf = next_patient.get('patient_cpf')
    if not cpf:
        return jsonify({"message": "Erro: Paciente sem CPF"}), 500
    
    

    return redirect(url_for('exam_form', cpf=cpf))

@app.route('/exam_form')
def exam_form():
    cpf = request.args.get('cpf')

    if not cpf:
        return "Paciente não encontrado", 404

    patient = Patient.find_by_cpf(cpf)
    if not patient:
        return "Paciente não encontrado", 404
    
    company_cnpj = patient.get('company_cnpj')

    company = Company.find_by_cnpj(company_cnpj) if company_cnpj else None
    queuePatient = Queue.get_next_patient()
    Queue.remove_patient(cpf)

    return render_template('exam_form.html', patient=patient, company=company, queuePatient=queuePatient)

@app.route('/save_exam', methods=['POST'])
def save_exam():
    eyes = {
        "Visão": {
            "Direito": {
                "Perto": request.form.get('visao_dir_perto'),
                "Longe": request.form.get('visao_dir_longe')
            },
            "Esquerdo": {
                "Perto": request.form.get('visao_esq_perto'),
                "Longe": request.form.get('visao_esq_longe')
            }
        },
        "Com óculos": {
            "Direito": {
                "Perto": request.form.get('oculos_dir_perto'),
                "Longe": request.form.get('oculos_dir_longe')
            },
            "Esquerdo": {
                "Perto": request.form.get('oculos_esq_perto'),
                "Longe": request.form.get('oculos_esq_longe')
            }
        }
    }

    examData = {
        "patient_cpf": request.form.get('cpf'),
        "company_cnpj": request.form.get('cnpj'),
        "exam_type": request.form.get('exam_type'),
        "job_type": request.form.get('job_type'),
        "personal_background": request.form.get('personal_background') if request.form.get('personal_background') else "Nada digno de nota",
        "absence_from_work": request.form.get('absence_from_work') if request.form.get('absence_from_work') else "Nada digno de nota",
        "surgery": request.form.get('surgery') if request.form.get('surgery') else "Não",
        "accidents": request.form.get('accidents') if request.form.get('accidents') else "Não",
        "pcd": request.form.get('pcd') if request.form.get('pcd') else "Não",
        "professional_background": request.form.get('professional_background') if request.form.get('professional_background') else "Nada digno de nota",
        "hv": request.form.get('hv') if request.form.get('hv') else "Nada digno de nota",
        "complaints": request.form.get('complaints') if request.form.get('complaints') else "Nada digno de nota",
        "fisical": request.form.get('fisical') if request.form.get('fisical') else "Nada digno de nota",
        "arterial_pressure": request.form.get('arterial_pressure'),
        "heart_rate": request.form.get('heart_rate'),
        "eyes": eyes,
        "respiratory_system": request.form.get('respiratory_system') if request.form.get('respiratory_system') else "Nada digno de nota",
        "circulatory_system": request.form.get('circulatory_system') if request.form.get('circulatory_system') else "Nada digno de nota",
        "abdomen": request.form.get('abdomen') if request.form.get('abdomen') else "Nada digno de nota",
        "osteoarticular_system": request.form.get('osteoarticular_system') if request.form.get('osteoarticular_system') else "Nada digno de nota",
        "result": request.form.get('result')
    }

    exam = Exam(
        examData["patient_cpf"], examData["company_cnpj"], examData["exam_type"],
        examData["job_type"], examData["personal_background"], examData["absence_from_work"],
        examData["surgery"], examData["accidents"], examData["pcd"], examData["professional_background"],
        examData["hv"], examData["complaints"], examData["fisical"], examData["arterial_pressure"],
        examData["heart_rate"], examData["eyes"], examData["respiratory_system"], examData["circulatory_system"],
        examData["abdomen"], examData["osteoarticular_system"], examData["result"]
    )

    # Salvar o exame
    exam.save()

    patient = Patient.find_by_cpf(examData["patient_cpf"])
    company = Company.find_by_cnpj(examData["company_cnpj"])

    # Formatar a data de hoje (ex: "2025-02-27")
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Criar o nome do arquivo usando o nome do paciente, CPF, CNPJ e data
    filename = f"{patient['name']}-{patient['cpf']}-{current_date}.pdf"

    # Criar o PDF na memória
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename={filename}'
    response.headers['X-Filename'] = filename

    # Gerar PDF
    pdf = canvas.Canvas(response.stream, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 50, "EXAME MÉDICO DE SAÚDE OCUPACIONAL")

    pdf.setFont("Helvetica", 12)
    y = height - 80
    line_height = 20
    exam_date = datetime.strptime(str(exam.date), "%Y-%m-%d %H:%M:%S.%f")

    # Formatar para dd/MM/yyyy
    formatted_date = exam_date.strftime("%d/%m/%Y")

    fields = [
        ("Nome da empresa:", company["name"]),
        ("CNPJ:", company["cnpj"]),
        ("Data:", formatted_date),
        ("Exame Médico Geral:", examData["exam_type"]),
        ("Nome:", patient["name"]),
        ("CPF:", patient["cpf"]),
        ("Data de nascimento:", patient["dob"]),
        ("Cargo/Função:", examData["job_type"]),
        ("Antecedentes pessoais:", examData["personal_background"]),
        ("Afastamento do trabalho:", examData["absence_from_work"]),
        ("Cirurgia:", examData["surgery"]),
        ("Acidentes:", examData["accidents"]),
        ("P.C.D.:", examData["pcd"]),
        ("Antecedentes trabalhistas:", examData["professional_background"]),
        ("H./V.:", examData["hv"]),
        ("Queixas e duração:", examData["complaints"]),
        ("Exame Físico:", examData["fisical"]),
        ("Pressão Arterial:", f"{examData['arterial_pressure']} mm Hg"),
        ("Frequência Cardíaca:", f"{examData['heart_rate']} BPM"),
        ("Olhos:", ""),
        ("Visão D. Perto:", examData["eyes"]["Visão"]["Direito"]["Perto"]),
        ("Visão D. Longe:", examData["eyes"]["Visão"]["Direito"]["Longe"]),
        ("Visão E. Perto:", examData["eyes"]["Visão"]["Esquerdo"]["Perto"]),
        ("Visão E. Longe:", examData["eyes"]["Visão"]["Esquerdo"]["Longe"]),
        ("Óculos D. Perto:", examData["eyes"]["Com óculos"]["Direito"]["Perto"]),
        ("Óculos D. Longe:", examData["eyes"]["Com óculos"]["Direito"]["Longe"]),
        ("Óculos E. Perto:", examData["eyes"]["Com óculos"]["Esquerdo"]["Perto"]),
        ("Óculos E. Longe:", examData["eyes"]["Com óculos"]["Esquerdo"]["Longe"]),
        ("Aparelho respiratório:", examData["respiratory_system"]),
        ("Aparelho circulatório:", examData["circulatory_system"]),
        ("Abdômen:", examData["abdomen"]),
        ("Aparelho Osteoarticular:", examData["osteoarticular_system"]),
        ("Resultado:", examData["result"]),
    ]

    for label, value in fields:
        pdf.drawString(50, y, f"{label} {value}")
        y -= line_height

    # Linha divisória
    y -= 30

    # Posição central na largura da página
    center_x = width / 2

    # Campo de Assinatura
    pdf.drawString(center_x - pdf.stringWidth("Dr. Roberto Ribeiro de Carvalho", "Helvetica", 12) / 2, y, "_________________________")

    # Texto da assinatura (Nome e CRM)
    pdf.drawString(center_x - pdf.stringWidth("Dr. Roberto Ribeiro de Carvalho", "Helvetica", 12) / 2, y - 20, "Dr. Roberto Ribeiro de Carvalho")
    pdf.drawString(center_x - pdf.stringWidth("Médico do Trabalho CRM 63783", "Helvetica", 12) / 2, y - 40, "Médico do Trabalho CRM 63783")

    pdf.showPage()
    pdf.save()

    return response



@app.route('/get_queue', methods=['GET'])
def get_queue():
    patients_queue = list(queue_collection.find().sort("entry_time", 1))  
    queue_list = []

    for p in patients_queue:
        patient_info = patients.find_one({"cpf": p["patient_cpf"]}, {"name": 1, "_id": 0})
        masked_cpf = mask_cpf(p["patient_cpf"])  # Aplicar máscara no CPF

        queue_list.append({
            "cpf": masked_cpf,
            "name": patient_info["name"] if patient_info else "Nome não encontrado",
            "entry_time": p["entry_time"]
        })

    return jsonify(queue_list)


@app.route('/')
def home():
    return render_template('index.html')

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_company')
def add_company():
    return render_template('company_form.html')

@app.route('/doctor')
def doctor():
    return render_template('doctor.html')

@app.route('/check_patient', methods=['GET'])
def check_patient():
    cpf = request.args.get('cpf')
    
    if not cpf:
        return jsonify({"error": "CPF não fornecido"}), 400
    
    patient = patients.find_one({"cpf": cpf}, {"_id": 0})  # Busca pelo CPF, sem retornar o _id
    
    if patient:
        return jsonify(patient)  # Retorna os dados do paciente encontrado
    else:
        return jsonify(None)  # Retorna None para indicar que o paciente não foi encontrado
    
@app.route('/check_company', methods=['GET'])
def check_company():
    cnpj = request.args.get('cnpj')
    
    if not cnpj:
        return jsonify({"error": "CNPJ não fornecido"}), 400
    
    company = companies.find_one({"cnpj": cnpj}, {"_id": 0})  # Busca pelo CPF, sem retornar o _id
    
    if company:
        return jsonify(company)  # Retorna os dados do paciente encontrado
    else:
        return jsonify(None)  # Retorna None para indicar que o paciente não foi encontrado

@app.route('/patient_form', methods=['GET', 'POST'])
def patient_form():
    if request.method == 'POST':
        # Lógica para salvar ou atualizar os dados do paciente no banco
        cpf = request.form.get('cpf')
        name = request.form.get('name')
        dob = request.form.get('dob')
        rg = request.form.get('rg')
        street = request.form.get('street')
        neighborhood = request.form.get('neighborhood')
        street_number = request.form.get('street_number')
        phone = request.form.get('phone')
        company_cnpj = request.form.get('company_cnpj')
        
        # Verificar se o paciente já existe (por CPF)
        existing_patient = patients.find_one({"cpf": cpf})
        if existing_patient:
            # Se o paciente já existir, atualiza os dados
            patients.update_one(
                {"cpf": cpf},
                {"$set": {
                    "name": name,
                    "dob": dob,
                    "rg": rg,
                    "street": street,
                    "neighborhood": neighborhood,
                    "street_number": street_number,
                    "phone": phone,
                    "company_cnpj": company_cnpj
                }}
            )
        else:
            # Se o paciente não existir, cria um novo
            new_patient = Patient(
                cpf=cpf,
                name=name,
                dob=dob,
                rg=rg,
                street=street,
                neighborhood=neighborhood,
                street_number=street_number,
                phone=phone,
                company_cnpj=company_cnpj
            )
            patients.insert_one(new_patient.__dict__)  # Armazena no MongoDB
        
        # Verificar se a empresa já existe (por CNPJ)
        existing_company = companies.find_one({"cnpj": company_cnpj})
        if existing_company:
            # Se a empresa já existir, atualiza os dados
            companies.update_one(
                {"cnpj": company_cnpj},
                {"$set": {
                    "name": request.form.get('company_name'),
                    "corporate_name": request.form.get('company_corporate_name'),
                    "phone": request.form.get('company_phone'),
                    "address": request.form.get('company_address')
                }}
            )
        else:
            # Se a empresa não existir, cria uma nova
            new_company = {
                "cnpj": company_cnpj,
                "name": request.form.get('company_name'),
                "corporate_name": request.form.get('company_corporate_name'),
                "phone": request.form.get('company_phone'),
                "address": request.form.get('company_address')
            }
            companies.insert_one(new_company)  # Armazena no MongoDB

        # Adicionar o paciente à fila
        queue_entry = {
            "patient_cpf": cpf,
            "exam_type": request.form.get('exam_type'),
            "job_type": request.form.get('job_type'),
            "entry_time": datetime.now(saopaulo_tz)  # Armazena a hora da entrada na fila
        }
        queue_collection.insert_one(queue_entry)  # Insere na coleção 'queue'
        
        # Redireciona para a página de sucesso ou fila após a inserção, passando um parâmetro de sucesso
        return redirect(url_for('index', success="true"))
    
    return render_template('patient_form.html')

# Rota para o formulário de empresa
@app.route('/company', methods=['GET', 'POST'])
def company_form():
    if request.method == 'POST':
        data = request.form
        company = {
            "cnpj": data['cnpj'],
            "name": data['name'],
            "corporate_name": data['corporate_name'],
            "phone": data['phone'],
            "address": data['address']
        }
        db.companies.insert_one(company)
        return redirect(url_for('index'))
    return render_template('company_form.html')

# Executar a aplicação
if __name__ == '__main__':
    app.run(debug=True)
