# SecureChain Audit

Plataforma de auditoria baseada em blockchain desenvolvida para a disciplina **Segurança de Sistemas com Blockchain, Criptografia e Auditoria de Eventos**.

---

## Estrutura do Projeto

```
securechain/
├── blockchain/
│   ├── blockchain.py     # Implementação dos blocos, encadeamento e validação
│   └── chain.json        # Persistência da blockchain (gerado automaticamente)
├── auditoria/
│   ├── auditor.py        # Coleta who, last, ss, ip a e gera relatório datado
│   └── relatorios/       # Relatórios gerados automaticamente
├── backup/
│   └── backup.sh         # Compactação tar.gz + criptografia AES-256-CBC
├── logs/                 # Log do backup e eventos do sistema
├── documentos/           # Arquivos monitorados por hash SHA-256
├── usuarios/
│   └── users.json        # Credenciais em hash bcrypt (gerado automaticamente)
├── auth.py               # Cadastro, login e gerenciamento de usuários
├── monitor.py            # Monitoramento de integridade de arquivos
├── main.py               # Ponto de entrada — menu interativo
└── baseline.json         # Hashes de referência dos documentos
```

---

## Requisitos

- Linux Debian 13 (VM)
- Python 3
- Biblioteca `bcrypt`: `pip3 install bcrypt --break-system-packages`
- OpenSSL (já incluso no Debian)
- Variável de ambiente `BACKUP_PASS` definida para o backup

---

## Como Rodar

### 1. Configuração inicial da VM

Execute o arquivo `setup.txt` como root para instalar dependências, criar usuários e aplicar permissões:

```bash
sudo bash setup.txt
```

### 2. Iniciar o sistema

```bash
cd securechain/
python3 main.py
```

Na primeira execução, o sistema pedirá para criar um **administrador inicial**.  
Após o login, o menu exibirá as opções disponíveis conforme o perfil do usuário.

---

## Módulos e Como Usar Cada Um

### Sistema de Autenticação (`auth.py`)

Gerencia usuários com perfis `admin`, `analista` e `visitante`.  
Senhas armazenadas com **bcrypt + salt** — nunca em texto puro.

```python
from auth import cadastrar, login, listar_usuarios

# Cadastrar
cadastrar("joao", "senha123", "analista")

# Login — retorna dict com perfil ou None
dados = login("joao", "senha123")

# Listar (sem expor senhas)
print(listar_usuarios())
```

### Blockchain (`blockchain/blockchain.py`)

```python
from blockchain.blockchain import Blockchain

bc = Blockchain()
bc.add_block("Evento de teste")

ok, bloco = bc.validate()
if ok:
    print("Cadeia íntegra")
else:
    print(f"Corrompido no bloco #{bloco}")

bc.exibir()
```

### Monitoramento de Integridade (`monitor.py`)

```python
from monitor import criar_baseline, verificar
from blockchain.blockchain import Blockchain

bc = Blockchain()

# 1ª vez: criar baseline de referência
criar_baseline()

# Verificações seguintes: passa a blockchain para registrar alertas
alteracoes = verificar(blockchain=bc)
```

### Auditoria do Sistema (`auditoria/auditor.py`)

```python
from auditoria.auditor import coletar

# Gera relatório datado em auditoria/relatorios/
caminho = coletar()
print(f"Relatório salvo em: {caminho}")
```

Ou diretamente pelo terminal:

```bash
cd securechain/
python3 auditoria/auditor.py
```

### Backup Seguro (`backup/backup.sh`)

```bash
cd securechain/
export BACKUP_PASS="SuaSenhaForteSuperSecreta123!"
bash backup/backup.sh
```

O script:
1. Compacta `documentos/` em `.tar.gz`
2. Criptografa com **AES-256-CBC** via OpenSSL
3. Remove o arquivo temporário não criptografado
4. Registra o evento na blockchain
5. Salva log em `logs/backup.log`

Para descriptografar (recuperação):

```bash
export BACKUP_PASS="SuaSenhaForteSuperSecreta123!"
openssl enc -d -aes-256-cbc -pbkdf2 \
    -in  logs/backup-YYYY-MM-DD-HH-MM-SS.tar.gz.enc \
    -out recuperado.tar.gz \
    -pass env:BACKUP_PASS
tar -xzf recuperado.tar.gz
```

---

## Divisão de Tarefas (equipe)

| Módulo | Responsável |
|---|---|
| Blockchain (`blockchain.py`) | — |
| Autenticação (`auth.py`) | — |
| Monitoramento (`monitor.py`) | — |
| Auditoria (`auditor.py`) | — |
| Backup (`backup.sh`) | — |
| Configuração da VM (`setup.txt`) | — |
| Relatório Técnico | — |

---

## Princípios de Segurança Aplicados

| Princípio | Como foi aplicado |
|---|---|
| Senhas em texto puro | bcrypt com salt em cada cadastro |
| Permissões excessivas | chmod 750 no projeto, 700 em dados sensíveis |
| Ausência de logs | Toda ação gera bloco na blockchain |
| Validação de entrada | Perfis validados no cadastro; tentativas de login limitadas a 3 |
| Senha hardcoded | Backup usa variável de ambiente `BACKUP_PASS` |
| Logs manipuláveis | Eventos em blockchain imutável (SHA-256 encadeado) |
