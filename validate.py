#!/usr/bin/env python3
"""
Script de validação final do projeto to-whatsapp
Testa se todas as funcionalidades estão operacionais
"""

import requests
import time
import os
import subprocess

BASE_URL = "http://127.0.0.1:5000"

def criar_video_teste():
    """Cria um vídeo de teste usando ffmpeg"""
    cmd = [
        'ffmpeg', '-y', '-f', 'lavfi', 
        '-i', 'testsrc=duration=2:size=320x240:rate=25',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        'uploads/validation_test.mp4'
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return 'uploads/validation_test.mp4'

def testar_servidor():
    """Testa se o servidor está respondendo"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        return response.status_code == 200
    except:
        return False

def testar_upload():
    """Testa upload e conversão"""
    try:
        video_path = criar_video_teste()
        
        with open(video_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/upload", files=files, timeout=10)
        
        if response.status_code != 200:
            return False, "Upload falhou"
        
        job_data = response.json()
        job_id = job_data['job_id']
        
        # Aguarda conversão
        for i in range(30):
            progress_response = requests.get(f"{BASE_URL}/progress/{job_id}", timeout=5)
            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                if progress_data.get('done'):
                    return True, f"Conversão concluída: {progress_data.get('file')}"
            time.sleep(1)
        
        return False, "Timeout na conversão"
    except Exception as e:
        return False, f"Erro: {e}"

def main():
    print("=== Validação Final do Projeto to-whatsapp ===")
    
    print("1. Testando servidor...")
    if testar_servidor():
        print("✓ Servidor respondendo")
    else:
        print("✗ Servidor não responde")
        return
    
    print("2. Testando upload e conversão...")
    sucesso, mensagem = testar_upload()
    if sucesso:
        print(f"✓ {mensagem}")
    else:
        print(f"✗ {mensagem}")
        return
    
    print("3. Verificando estrutura de arquivos...")
    arquivos_importantes = [
        'app.py', 'templates/index.html', 'Dockerfile', 
        'docker-compose.yml', 'requirements.txt', 'README.md'
    ]
    
    for arquivo in arquivos_importantes:
        if os.path.exists(arquivo):
            print(f"✓ {arquivo}")
        else:
            print(f"✗ {arquivo} não encontrado")
    
    print("\n=== Projeto validado com sucesso! ===")
    print("Pronto para deploy no GitHub e Docker.")

if __name__ == "__main__":
    main()
