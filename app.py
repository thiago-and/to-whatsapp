import uuid
import threading
import subprocess
import re
import os
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
LOG_FOLDER = "logs"

os.makedirs(LOG_FOLDER, exist_ok=True)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

# Dicionário para armazenar progresso
jobs = {}
# Mapear job_id -> processo (Popen) para permitir cancelamento
job_procs = {}

# Função para excluir vídeos antigos da pasta output
import time
def limpar_videos_antigos(pasta=OUTPUT_FOLDER, dias=1, max_files=200):
    """
    Remove arquivos mais antigos por tempo (dias) e mantém no máximo `max_files` arquivos (remove os mais antigos além deste limite).
    """
    agora = time.time()
    limite = agora - dias * 86400
    try:
        files = [os.path.join(pasta, f) for f in os.listdir(pasta)]
    except FileNotFoundError:
        return

    # remove por tempo
    for caminho in files:
        if os.path.isfile(caminho) and os.path.getmtime(caminho) < limite:
            try:
                os.remove(caminho)
            except Exception as e:
                print(f"Erro ao remover {caminho}: {e}")

    # mantém no máximo max_files (remove mais antigos)
    all_files = [os.path.join(pasta, f) for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
    if len(all_files) > max_files:
        all_files.sort(key=lambda p: os.path.getmtime(p))
        for caminho in all_files[0:len(all_files)-max_files]:
            try:
                os.remove(caminho)
            except Exception as e:
                print(f"Erro ao remover por excesso {caminho}: {e}")

# Thread para limpeza periódica
def agendar_limpeza():
    def loop():
        while True:
            limpar_videos_antigos()
            time.sleep(3600)  # Executa a cada 1 hora
    t = threading.Thread(target=loop, daemon=True)
    t.start()

agendar_limpeza()

def obter_duracao(video):
    comando = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video
    ]
    result = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return None

def calcular_bitrate_para_tamanho(tamanho_mb, duracao_seg):
    # Protege contra duracao inválida e entradas malformadas
    try:
        if not duracao_seg or float(duracao_seg) <= 0:
            return 800_000
        tamanho_bits = float(tamanho_mb) * 8 * 1024 * 1024
        bitrate_total = tamanho_bits / float(duracao_seg)
        # subtrai margem para áudio e overhead, garante mínimo
        bitrate_video = max(64_000, bitrate_total - 128000)
        return int(bitrate_video)
    except Exception:
        return 800_000

def converter_video(job_id, entrada, saida, inicio, fim, tamanho_max, resolucao):
    jobs[job_id] = {"progress": 0, "done": False, "file": None}

    duracao_original = obter_duracao(entrada)
    duracao_final = duracao_original
    if inicio and fim:
        try:
            t1 = sum(int(x) * 60 ** i for i, x in enumerate(reversed(inicio.split(":"))))
            t2 = sum(int(x) * 60 ** i for i, x in enumerate(reversed(fim.split(":"))))
            duracao_final = max(1, t2 - t1)
        except:
            pass

    if tamanho_max:
        bitrate_num = calcular_bitrate_para_tamanho(float(tamanho_max), duracao_final)
    else:
        bitrate_num = 800_000  # padrão

    comando = ["ffmpeg", "-y", "-i", entrada]

    if inicio and fim:
        comando.extend(["-ss", inicio, "-to", fim])

    comando.extend([
        "-vf", f"scale={resolucao}",
        "-b:v", f"{bitrate_num}",
        "-minrate", f"{bitrate_num}",
        "-maxrate", f"{bitrate_num}",
        "-bufsize", f"{bitrate_num // 2}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        "-progress", "pipe:1",
        saida
    ])

    # abre log por job
    log_path = os.path.join(LOG_FOLDER, f"{job_id}.log")
    with open(log_path, 'w', encoding='utf-8') as logf:
        process = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        job_procs[job_id] = process

        for line in iter(process.stdout.readline, ''):
            logf.write(line)
            logf.flush()
            # tenta parsear progresso do ffmpeg
            if 'out_time_ms' in line:
                match = re.search(r"out_time_ms=(\d+)", line)
                if match and duracao_final:
                    ms = int(match.group(1))
                    progresso = min(100, int((ms / 1_000_000) / duracao_final * 100))
                    jobs[job_id]['progress'] = progresso
            # outra forma: linhas do tipo 'progress=end' etc
            if line.startswith('progress='):
                # ignora, já tratamos out_time_ms
                pass

        process.wait()
        # remover proc do mapeamento quando terminar
        job_procs.pop(job_id, None)
    jobs[job_id]["progress"] = 100
    jobs[job_id]["done"] = True
    jobs[job_id]["file"] = os.path.basename(saida)

def cancelar_job(job_id):
    proc = job_procs.get(job_id)
    if proc and proc.poll() is None:
        try:
            proc.terminate()
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    # aceitar tanto 'file' (frontend atual) quanto 'video' (código legacy)
    file = request.files.get("file") or request.files.get("video")
    inicio = request.form.get("inicio")
    fim = request.form.get("fim")
    tamanho_max = request.form.get("tamanho_max")
    resolucao = request.form.get("resolucao") or "1280x720"

    if not file or file.filename == "":
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    job_id = str(uuid.uuid4())
    saida_path = os.path.join(app.config["OUTPUT_FOLDER"], filename.rsplit(".", 1)[0] + "_whatsapp.mp4")

    thread = threading.Thread(target=converter_video, args=(job_id, filepath, saida_path, inicio, fim, tamanho_max, resolucao))
    thread.start()

    return jsonify({"job_id": job_id})

@app.route("/progress/<job_id>")
def progress(job_id):
    if job_id in jobs:
        return jsonify(jobs[job_id])
    return jsonify({"error": "Job não encontrado"}), 404

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)


@app.route('/cancel/<job_id>', methods=['POST'])
def cancel(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Job não encontrado'}), 404
    cancelar_job(job_id)
    jobs[job_id]['done'] = True
    jobs[job_id]['progress'] = 0
    return jsonify({'cancelled': True})

if __name__ == "__main__":
    # Detecta se está em ambiente de produção (Docker)
    is_production = os.environ.get('FLASK_ENV') == 'production' or os.path.exists('/.dockerenv')
    
    if is_production:
        # Produção: sem debug, host 0.0.0.0 para aceitar conexões externas
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    else:
        # Desenvolvimento: com debug
        app.run(debug=True, threaded=True, use_reloader=False)
