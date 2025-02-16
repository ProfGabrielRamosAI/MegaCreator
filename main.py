import csv
import subprocess
import time
import random
import string
import logging
from faker import Faker
import pymailtm
from pymailtm.pymailtm import CouldNotGetAccountException


# Configuração de logging
logging.basicConfig(
    filename="mega_account_check.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

fake = Faker()

# Função para gerar uma senha aleatória
def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Função para gerar um e-mail do Mail.tm
def generate_mail_tm_account():
    """Gera uma conta temporária no Mail.tm"""
    for _ in range(5):
        try:
            mail = pymailtm.MailTm()
            acc = mail.get_account()
            return acc.address, acc.id_, acc.password
        except CouldNotGetAccountException:
            print("> Tentando obter conta Mail.tm novamente...")
            time.sleep(5)
    return None, None, None

# Função para registrar a conta no MEGA
def register_account(email, password):
    """Registra uma conta MEGA utilizando um e-mail e senha."""
    registration = subprocess.run(
        [
            "megatools",
            "reg",
            "--scripted",
            "--register",
            "--email",
            email,
            "--password",
            password,
        ],
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return registration.stdout

# Função para verificar se a conta MEGA está ativa
def check_mega_account(email, password):
    """Verifica se a conta MEGA está ativa usando login."""
    login = subprocess.run(
        [
            "megatools",
            "ls",
            "-u",
            email,
            "-p",
            password,
        ],
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return "/Root" in login.stdout

# Função para gerar contas e salvar no CSV
def generate_and_save_accounts(num_accounts=5):
    """Gera várias contas e as salva em um arquivo CSV."""
    with open("accounts.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Email", "MEGA Password", "Usage", "Mail.tm Password", "Mail.tm ID", "Purpose"])

        for _ in range(num_accounts):
            email, mail_id, mail_password = generate_mail_tm_account()
            if email:
                mega_password = generate_random_string(12)
                csvwriter.writerow([email, mega_password, "-", mail_password, mail_id, "-"])
                print(f"Conta criada: {email} com senha {mega_password}")
            else:
                print("Erro ao gerar conta Mail.tm.")

# Função principal
def main():
    """Função principal que executa o fluxo de criação e manutenção de contas."""
    # Gerar contas novas
    action = input("Deseja (1) Criar novas contas ou (2) Verificar contas existentes? (1/2): ")
    
    if action == "1":
        num_accounts = int(input("Quantas contas deseja criar? "))
        generate_and_save_accounts(num_accounts)

    elif action == "2":
        # Manter as contas existentes ativas
        with open("accounts.csv") as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                if not row or row[0] == "Email":
                    continue

                email = row[0].strip()
                password = row[1].strip()

                # Verificar se a conta está ativa
                if check_mega_account(email, password):
                    print(f"Conta {email} está ativa.")
                    logging.info(f"Conta {email} está ativa.")
                else:
                    print(f"Conta {email} não está ativa.")
                    logging.error(f"Erro para a conta {email}: Conta inativa.")

                time.sleep(1)

    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()
