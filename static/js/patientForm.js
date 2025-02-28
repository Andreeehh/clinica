import Swal from 'sweetalert2';
import { validarCPF } from 'cpf-cnpj-validator'; // Biblioteca para validar CPF
import { validarCNPJ } from 'cpf-cnpj-validator'; // 

// Função de validação de CPF
async function checkPatient() {
    const cpfInput = document.getElementById('cpf').value;

    // Valida CPF utilizando a biblioteca
    if (!validarCPF(cpfInput)) {
        console.log("cpf inválido")
        // Exibe a mensagem de erro com SweetAlert2
        Swal.fire({
            icon: 'error',
            title: 'CPF Inválido',
            text: 'O CPF informado não é válido. Por favor, verifique e tente novamente.',
            confirmButtonText: 'OK'
        });
        return;
    }

    const response = await fetch(`/check_patient?cpf=${cpfInput}`);
    const patient = await response.json();

    if (patient) {
        document.getElementById('name').value = patient.name || '';
        document.getElementById('dob').value = patient.dob || '';
        document.getElementById('rg').value = patient.rg || '';
        document.getElementById('street').value = patient.street || '';
        document.getElementById('neighborhood').value = patient.neighborhood || '';
        document.getElementById('street_number').value = patient.street_number || '';
        document.getElementById('phone').value = patient.phone || '';
        document.getElementById('company_cnpj').value = patient.company_cnpj || '';
        if (patient.company_cnpj) {
            checkCompanyCnpj();
        }
    }

    document.querySelectorAll('#patientFields input').forEach(input => {
        input.disabled = false;
    });

    document.getElementById('submitButton').style.display = 'block';
}

// Função de validação de CNPJ
async function checkCompanyCnpj() {
    const cnpjInput = document.getElementById('company_cnpj').value;

    // Valida CNPJ utilizando a biblioteca
    if (!validarCNPJ(cnpjInput)) {
        // Exibe a mensagem de erro com SweetAlert2
        Swal.fire({
            icon: 'error',
            title: 'CNPJ Inválido',
            text: 'O CNPJ informado não é válido. Por favor, verifique e tente novamente.',
            confirmButtonText: 'OK'
        });
        return;
    }

    const response = await fetch(`/check_company?cnpj=${cnpjInput}`);
    const company = await response.json();

    if (company) {
        document.getElementById('company_name').value = company.name || '';
        document.getElementById('company_street').value = company.street || '';
        document.getElementById('company_phone').value = company.phone || '';
        document.getElementById('company_email').value = company.email || '';
    }

    document.querySelectorAll('#companyFields input').forEach(input => {
        input.disabled = false;
    });
}

// Função chamada quando uma tecla é pressionada enquanto digita o CPF
function checkCpfKeyDown(event) {
    // Verifica se a tecla pressionada foi Enter (13) ou Tab (9)
    if (event.key === 'Enter' || event.key === 'Tab') {
        event.preventDefault(); // Impede o envio do formulário
        checkPatient(); // Chama a função para verificar o CPF

        // Foca no campo de nome (caso o CPF seja válido)
        document.getElementById('name').focus();
    }
}

// Função chamada quando uma tecla é pressionada enquanto digita o CNPJ
function checkCnpjKeyDown(event) {
    // Verifica se a tecla pressionada foi Enter (13) ou Tab (9)
    if (event.key === 'Enter' || event.key === 'Tab') {
        event.preventDefault(); // Impede o envio do formulário
        checkCompanyCnpj(); // Chama a função para verificar o CNPJ

        // Foca no campo de nome da empresa (caso o CNPJ seja válido)
        document.getElementById('company_name').focus();
    }
}
