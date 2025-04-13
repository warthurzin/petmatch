
# 📦 Tutorial para Rodar o Projeto PetMatch Localmente

## 🔗 1. Clonar o repositório do GitHub

Abra o terminal (CMD, PowerShell ou Git Bash) e execute:

```bash
git clone https://github.com/warthurzin/petmatch
```

Depois entre na pasta do projeto:

```bash
cd petmatch
```

---



---

## 📦 2. Instalar o Flask

 instale o Flask manualmente:

```bash
pip install flask
```

---

## 🛢 3. Usar o SQLite (já vem embutido com o Python)

baixe o programa:

🔗 https://sqlitebrowser.org/dl/

Baixe o instalador “Standard installer for 64-bit Windows”.

---

## ▶️ 4. Rodar o projeto Flask

Com o ambiente ativado, execute o app:

```bash
python app.py
```

Se estiver tudo certo, verá algo como:

```
* Running on http://127.0.0.1:5000
```

Abra esse link no navegador para acessar o site.

---

## 🧪 5. Testar

- Acesse: http://127.0.0.1:5000/cadastro ou /login
- Faça um cadastro.
- Depois entre com o login.
- Você deve ser redirecionado para a página inicial.

---


# 🛢 Como Usar o DB Browser for SQLite para Consultar o Banco de Dados

## 1. Abrir o DB Browser for SQLite

- Abra o programa DB Browser for SQLite instalado no seu computador.
- Você pode procurar por “DB Browser” no menu Iniciar ou na área de trabalho.

---

## 2. Abrir o banco de dados do projeto

1. Clique em `File > Open Database…` (ou "Arquivo > Abrir Banco de Dados").
2. Vá até a pasta onde está o seu projeto `petmatch`.
3. Selecione o arquivo `banco.db`.
4. Clique em **Abrir**.

---

## 3. Visualizar os dados da tabela

1. Vá para a aba `Browse Data` (ou "Procurar Dados").
2. No menu suspenso chamado `Table`, selecione `usuarios` (ou o nome da tabela que você criou).
3. Os dados cadastrados vão aparecer na tela.

---

## 4. Fazer uma consulta SQL manual

1. Vá para a aba `Execute SQL` (ou "Executar SQL").
2. Escreva o seguinte comando:

```sql
SELECT * FROM usuarios;
```

3. Clique no botão `▶️ Execute All` (Executar Tudo).
4. O resultado da consulta aparecerá abaixo, mostrando os dados cadastrados.

---
