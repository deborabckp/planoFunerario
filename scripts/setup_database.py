#!/usr/bin/env python
"""
Script para configurar o banco de dados inicial
"""
import os
import sys
import django
from pathlib import Path

# Adicionar o diretório do projeto ao path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'funeraria_project.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from funeraria.models import FunerariaStatus, DependenteStatus, FunerariaTipos

def main():
    """Executa a configuração inicial do banco de dados"""
    print("🚀 Iniciando configuração do banco de dados...")
    
    # Criar migrações
    print("📝 Criando migrações...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # Aplicar migrações
    print("🔄 Aplicando migrações...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Carregar dados iniciais
    print("📊 Carregando dados iniciais...")
    execute_from_command_line(['manage.py', 'loaddata', 'funeraria/fixtures/initial_data.json'])
    
    # Criar superusuário se não existir
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        print("👤 Criando superusuário admin...")
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@funeraria.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema',
            cpf='000.000.000-00',
            data_nascimento='1990-01-01',
            telefone='(11) 99999-9999'
        )
        print(f"✅ Superusuário criado: {admin_user.username}")
    else:
        print("ℹ️  Superusuário admin já existe")
    
    print("✅ Configuração do banco de dados concluída!")
    print("\n📋 Resumo:")
    print(f"   • Status: {FunerariaStatus.objects.count()} registros")
    print(f"   • Status Dependentes: {DependenteStatus.objects.count()} registros")
    print(f"   • Tipos de Serviços: {FunerariaTipos.objects.count()} registros")
    print(f"   • Usuários: {User.objects.count()} registros")
    print("\n🔐 Credenciais do admin:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🌐 Para acessar o sistema:")
    print("   Admin: http://localhost:8000/admin/")
    print("   API: http://localhost:8000/api/")

if __name__ == '__main__':
    main()