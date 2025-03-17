import subprocess
import os
import time

# Configurações do banco de dados
usuario = 'usuario'
senha = 'senha'
host = 'host'
banco = 'banco'
tabela_excluida = 'jobs'
diretorio_backup = 'C:\\pastaDestino'

# Criar diretório de backup se não existir
os.makedirs(diretorio_backup, exist_ok=True)

# Nome do arquivo de backup
numero = 1
while True:
    caminho_backup = os.path.join(diretorio_backup, f'nome_do_backup_{numero}.sql')
    if not os.path.exists(caminho_backup):
        break
    numero += 1

# Estimativa de tamanho do banco sem a tabela excluída
comando_tamanho = [
    r'C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe',  
    f'--user={usuario}',
    f'--password={senha}',
    '--host', host,
    '--batch',
    '--skip-column-names',
    '--execute', f"""
    SELECT 
        ROUND( SUM(data_length + index_length) / 1024 / 1024, 2) AS tamanho_total_MB
    FROM 
        information_schema.tables
    WHERE 
        table_schema = '{banco}'
        AND table_name != '{tabela_excluida}';
    """
]

resultado = subprocess.run(comando_tamanho, capture_output=True, text=True, check=True)
tamanho_estimado_mb = float(resultado.stdout.strip())
print(f'Estimativa de tamanho do backup: {tamanho_estimado_mb:.2f} MB')

try:
    resultado = subprocess.run(comando_tamanho, capture_output=True, text=True, check=True)
    tamanho_estimado_mb = float(resultado.stdout.strip())
    print(f'Estimativa de tamanho do backup: {tamanho_estimado_mb:.2f} MB')
except subprocess.CalledProcessError as e:
    print(f'Erro ao obter tamanho estimado: {e.stderr}')
    exit(1)

# Comandos para o dump
dump_schema_jobs = [
    r'C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe',
    '--no-data',
    f'--user={usuario}',
    f'--password={senha}',
    '--host', host,
    banco,
    tabela_excluida
]

dump_restante = [
    r'C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe',
    '--set-gtid-purged=OFF',
    '--single-transaction',
    f'--user={usuario}',
    f'--password={senha}',
    '--host', host,
    f'--ignore-table={banco}.{tabela_excluida}',
    banco
]

# Marca o tempo inicial de execução
tempo_inicial = time.time()

try:
    # Dump apenas da estrutura da tabela jobs
    temp_schema = f"{caminho_backup}_schema.sql"
    with open(temp_schema, 'w') as file:
        subprocess.run(dump_schema_jobs, stdout=file, stderr=subprocess.PIPE, check=True)

    # Dump do resto do banco, ignorando jobs
    temp_data = f"{caminho_backup}_data.sql"
    with open(temp_data, 'w') as file:
        processo = subprocess.Popen(dump_restante, stdout=file, stderr=subprocess.PIPE)

        # Monitorar progresso
        while processo.poll() is None:
            if os.path.exists(temp_data):
                tamanho_atual_mb = os.path.getsize(temp_data) / (1024 * 1024)
                progresso = (tamanho_atual_mb / tamanho_estimado_mb) * 100 if tamanho_estimado_mb > 0 else 0
                tempo_decorrido_segundos = time.time() - tempo_inicial
                minutos = int(tempo_decorrido_segundos // 60)
                segundos = int(tempo_decorrido_segundos % 60)

                print(f'Progresso: {tamanho_atual_mb:.2f} MB / {tamanho_estimado_mb:.2f} MB ({progresso:.2f}%)')
                print(f'Tempo decorrido: {minutos} minutos e {segundos} segundos', end='\r')

            time.sleep(1)  # Atualiza a cada 1 segundo

    # Junta os arquivos
    with open(caminho_backup, 'w', encoding='utf-8', errors='ignore') as final_file:
        for temp_file in [temp_schema, temp_data]:
            with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
                final_file.write(f.read())

    # Remove arquivos temporários
    # os.remove(temp_schema)
    os.remove(temp_data)

    # Tempo total de execução
    tempo_final = time.time()
    tempo_execucao_segundos = tempo_final - tempo_inicial
    minutos = int(tempo_execucao_segundos // 60)
    segundos = int(tempo_execucao_segundos % 60)

    print(f'\nBackup concluído: {caminho_backup}')
    print(f'Tempo total de execução: {minutos} minutos e {segundos} segundos')

except subprocess.CalledProcessError as e:
    print(f'Erro ao realizar o backup: {e.stderr}')
    exit(1)
