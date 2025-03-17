# Script para Backup de BD MySQL em Python

## Pontos de atenção para bom funcionamento do Script:

- Por padrão ele vem com a variável ``tabela_excluida`` preenchida, essa variável tem o propósito de não trazer uma tabela específica caso seja do interesse do usuário, a lógica não se aplica a muitas tabelas e deve ser readaptada pra caso hajam mais tabelas a serem ignoradas. O que de fato acontece é que trazemos a tabela vazia ao invés de somente ignora-la. A lógica é a seguinte, ele cria um dump pra tabela ignorada e outro para o restante das tabelas, no fim junta os dois. Se você cancelar a execução do script no meio do caminho haverão dois dumps. Fiz dessa forma pois ao utilizar a lógica de ``--no-data`` para a tabela ignorada junto com todas as outras tabelas e gerar um dump único atrasou a execução do script em no mínimo 10x, diante disso tive que adaptar a lógica.

- O valor da % que é exibida enquanto o backup está em execução não é tão preciso, o dump final pode ser um pouco maior ou menor do que o valor definido como **valor final estimado**.

- Abra um CMD e digite ``mysql --version`` caso ele retorne a versão de seu MySQL quer dizer que a ferramenta foi instalada e você pode prosseguir com a leitura abaixo, se retornar um erro instale o MySQL corretamente (com SQL Server), (esse passo é meio óbvio, mas as vezes quem trabalha com docker acaba esquecendo).

### Passo 1:
- Alterar corretamente os dados do banco, usuário, senha, conexão...

    ```
    usuario = 'usuario'
    senha = 'senha'
    host = 'host'
    banco = 'banco'
    tabela_excluida = 'jobs'
    diretorio_backup = 'C:\\pastaDestino' 
    ```

### Passo 2 (OPCIONAL):
- Alterar o nome do arquivo gerado pelo backup

    ```
    while True:
    caminho_backup = os.path.join(diretorio_backup, f'nome_do_backup_{numero}.sql')
    if not os.path.exists(caminho_backup):
        break
    numero += 1

    ```

    Altere:  ``f'nome_do_backup_{numero}.sql'``

### Passo 3:
- Alterar o caminho do seu SQL Server nos trechos exibidos abaixo, coloque o diretório onde seu MySQL Server for instalado. (já está com o diretório padrão do Windows).

    ```
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
    ```

    *(1 Linha)* - 
    Altere:  ``r'C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe'``

    *(2 Linhas)* - Altere:  ``r'C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe'``
