import json
import os
import random
import string
import re
import textwrap
import sys
import builtins
import time

from time import sleep
from random import randint
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

ADM_PATH = "administradores.json"
PROF_PATH = "professores.json"
ALUNO_PATH = "alunos.json"
DISCIPLINAS_PATH = "disciplinas.json"

TEXTO_VELOCIDADE = 0.002

print_original = print

# 1) Funções de Suporte

def carregar_json(caminho):
    if not os.path.exists(caminho):
        return {}

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
            if not conteudo:  # se o arquivo estiver vazio
                return {}
            return json.loads(conteudo)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"⚠️ Erro ao ler {caminho}. O arquivo estava vazio ou corrompido. Será recriado.")
        return {}

def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def gerar_ra_admin(dados):
    admins = dados.get("administradores", [])
    max_n = 1
    for a in admins:
        ra = a.get("ra", "")
        if ra.startswith("ADM"):
            try:
                n = int(ra.replace("ADM", ""))
                if n > max_n:
                    max_n = n
            except ValueError:
                pass
    return f"ADM{str(max_n + 1).zfill(4)}"

def gerar_ra_professor(dados):
    profs = dados.get("professores", [])
    max_n = 0
    for p in profs:
        ra = p.get("ra", "")
        if ra.startswith("PROF"):
            try:
                n = int(ra.replace("PROF", ""))
                if n > max_n:
                    max_n = n
            except ValueError:
                pass
    return f"PROF{str(max_n + 1).zfill(4)}"

def gerar_ra_aluno():
    numero = random.randint(1000, 9999)
    return f"CSA{numero}"

def menu_login():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("=" * 45)
        print("🔐 LOGIN DE USUÁRIO")
        print("=" * 45)
        print("1. Administrador")
        print("2. Professor")
        print("3. Aluno")
        print("4. Voltar")
        print("-" * 45)

        op = input("Escolha uma opção: ").strip()

        if op == "1":
            login_administrador()
        elif op == "2":
            login_professor()
        elif op == "3":
            login_aluno()
        elif op == "4":
            break
        else:
            print("\n❌ Opção inválida.")
            input("Pressione ENTER para continuar...")

def print_lento(*args, **kwargs):
    sep = kwargs.pop("sep", " ")
    end = kwargs.pop("end", "\n")
    texto = sep.join(str(a) for a in args) + end

    for ch in texto:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(TEXTO_VELOCIDADE)

builtins.print = print_lento

# 2) ConexaBot

PERSONALIDADE = {
    "nome": "ConexaBot",
    "descricao": "Sou uma assistente virtual do sistema ConexaAcademy!",
    "respostas": {
        "saudacao": "Olá! 👋 Eu sou o ConexaBot, sua assistente virtual acadêmica.",
        "ajuda": "Posso te ajudar com login, cadastro, disciplinas e dúvidas gerais sobre o sistema.",
        "erro": "Desculpe, não entendi sua pergunta. Pode reformular?",
        "login": "Para fazer login, escolha a opção '1' no menu principal e insira seu RA e senha.",
        "cadastro": "Para se cadastrar, escolha a opção '2' no menu e selecione se é aluno ou professor.",
        "sobre": "O ConexaAcademy é um sistema acadêmico colaborativo que conecta alunos, professores e administradores.",
    }
}

def conexa_bot():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 45)
    print("🤖  CONEXABOT — ASSISTENTE VIRTUAL DO CONEXAACADEMY")
    print("=" * 45)
    print("Digite 'sair' a qualquer momento para voltar ao menu.\n")

    contexto = []
    print(PERSONALIDADE["respostas"]["saudacao"])

    while True:
        user_input = input("\nVocê: ").strip().lower()
        if user_input in ["sair", "exit"]:
            print("\nConexaBot: Até logo! Retornando ao menu principal...\n")
            break

        contexto.append({"role": "user", "content": user_input})

        if "login" in user_input:
            resposta = PERSONALIDADE["respostas"]["login"]
        elif "cadastro" in user_input:
            resposta = PERSONALIDADE["respostas"]["cadastro"]
        elif "ajuda" in user_input or "duvida" in user_input:
            resposta = PERSONALIDADE["respostas"]["ajuda"]
        elif "conexabot" in user_input or "você" in user_input:
            resposta = PERSONALIDADE["respostas"]["sobre"]
        elif "conexaacademy" in user_input or "sistema" in user_input:
            resposta = PERSONALIDADE["respostas"]["sobre"]
        else:
            resposta = PERSONALIDADE["respostas"]["erro"]

        print(f"ConexaBot: {resposta}")
        contexto.append({"role": "assistant", "content": resposta})

# 3) Login

def login_administrador():
    try:
        with open(ADM_PATH, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        print("⚠️ Arquivo de administradores não encontrado!")
        return None

    admins = dados.get("administradores", [])
    if not admins:
        print("⚠️ Nenhum administrador cadastrado no sistema.")
        return None

    print("\n=== LOGIN ADMINISTRADOR ===")
    ra = input("RA: ").strip().upper()
    senha = input("Senha: ").strip()

    for adm in admins:
        if adm["ra"] == ra:
            if adm.get("bloqueado", False):
                print(f"\n🚫 Acesso negado! O administrador {adm['nome']} está bloqueado.")
                sleep(1.5)
                print("Entre em contato com um administrador!")
                sleep(1.5)
                return
            if adm["senha"] == senha:
                tipo = adm.get("tipo", "limitado")
                nome = adm.get("nome", "Administrador")

                print(f"\n✅ Login bem-sucedido! Bem-vindo, {nome}.")
                print(f"Permissão: {tipo.upper()}")
                sleep(1.2)

                if tipo == "godmode":
                    painel_admin_godmode()
                elif tipo == "limitado":
                    painel_admin_limitado()
                else:
                    print("⚠️ Tipo de administrador não reconhecido.")
                return

    print("\n❌ RA ou senha incorretos.")
    sleep(1.2)

def login_professor():
    print("\n=== LOGIN PROFESSOR ===")

    try:
        with open(PROF_PATH, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        print("⚠️ Arquivo de professores não encontrado!")
        return

    professores = dados.get("professores", [])
    if not professores:
        print("⚠️ Nenhum professor cadastrado.")
        return

    ra = input("RA: ").strip().upper()
    senha = input("Senha: ").strip()

    for prof in professores:
        if prof["ra"] == ra:
            if prof.get("bloqueado", False):
                print(f"\n🚫 Conta bloqueada. Contate o administrador do sistema.")
                sleep(1.5)
                return

            # Verifica senha
            if prof["senha"] == senha:
                print(f"\n✅ Login bem-sucedido! Bem-vindo(a), Professor {prof['nome']}.")
                print(f"📘 Disciplina: {prof.get('disciplina', 'N/A')}")
                sleep(1.2)
                painel_professor(prof)
                return
            else:
                print("\n❌ Senha incorreta.")
                sleep(1.2)
                return

    print("\n❌ RA não encontrado.")
    sleep(1.2)

def login_aluno():
    print("\n=== LOGIN ALUNO ===")

    try:
        with open(ALUNO_PATH, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        print("⚠️ Arquivo de alunos não encontrado!")
        return

    alunos = dados.get("alunos", [])
    if not alunos:
        print("⚠️ Nenhum aluno cadastrado no sistema.")
        return

    ra = input("RA: ").strip().upper()
    senha = input("Senha: ").strip()

    for aluno in alunos:
        if aluno["ra"] == ra and aluno["senha"] == senha:

            if aluno.get("bloqueado", False):
                print("\n🚫 Esta conta está bloqueada. Contate o administrador.")
                sleep(1.5)
                return

            print(f"\n✅ Login bem-sucedido! Bem-vindo(a), {aluno['nome']}.")
            sleep(1.2)

            painel_aluno(aluno)   
            return

    print("\n❌ RA ou senha incorretos.")
    sleep(1.2)

# 4) Cadastro

def cadastro_usuario():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 45)
    print("📝 CADASTRO DE USUÁRIO")
    print("=" * 45)
    print("1. Administrador (requer código de acesso)")
    print("2. Professor (requer código de acesso)")
    print("3. Aluno")
    print("4. Voltar")
    print("-" * 45)

    op = input("Escolha uma opção: ").strip()

    if op == "1":
        cadastro_admin_limitado()

    elif op == "2":
        cadastro_professor()

    elif op == "3":
        cadastro_aluno()

    elif op == "4":
        return
    else:
        print("\n❌ Opção inválida.")
        input("Pressione ENTER para voltar.")

def cadastro_admin_limitado(token):
    dados = carregar_json(ADM_PATH)
    tokens = dados.get("tokens_pendentes", [])
    valido = None

    for t in tokens:
        if t["token"] == token and not t["usado"]:
            valido = t
            break

    if not valido:
        print("\n❌ Token inválido ou já utilizado.")
        input("Pressione ENTER para continuar...")
        return

    nome = input("Nome completo: ").strip()
    senha = input("Crie sua senha: ").strip()

    # gerar RA automaticamente
    novo_ra = gerar_ra_admin(dados)

    novo_admin = {
        "ra": novo_ra,
        "senha": senha,
        "nome": nome,
        "tipo": "limitado",
        "bloqueado": False
    }

    if "administradores" not in dados:
        dados["administradores"] = []

    dados["administradores"].append(novo_admin)
    valido["usado"] = True
    salvar_json(ADM_PATH, dados)

    print(f"\n✅ Cadastro concluído com sucesso!")
    print(f"Seu RA de administrador é: {novo_ra}")
    input("Pressione ENTER para continuar...")

def cadastro_professor():
    disciplinas = carregar_json(DISCIPLINAS_PATH)

    token = input("Digite o código de acesso da disciplina: ").strip().upper()

    disciplina_encontrada = None
    for nome, dados in disciplinas.items():
        if dados.get("codigo_acesso") == token:
            disciplina_encontrada = nome
            break

    if not disciplina_encontrada:
        print("\n❌ Código inválido ou já utilizado.")
        input("Pressione ENTER para continuar...")
        return

    print(f"\n✅ Código válido! Disciplina: {disciplina_encontrada}")
    print("Agora vamos prosseguir com o cadastro do professor.\n")

    nome = input("Nome completo: ").strip()
    cpf = input("CPF (somente números): ").strip()
    telefone = input("Telefone (com DDD): ").strip()
    email = input("E-mail: ").strip()
    senha = input("Crie sua senha: ").strip()

    dados_prof = carregar_json(PROF_PATH)
    if "professores" not in dados_prof:
        dados_prof["professores"] = []

    novo_ra = gerar_ra_professor(dados_prof)

    novo_prof = {
        "ra": novo_ra,
        "nome": nome,
        "cpf": cpf,
        "telefone": telefone,
        "email": email,
        "senha": senha,
        "disciplina": disciplina_encontrada,
        "bloqueado": False
    }

    dados_prof["professores"].append(novo_prof)
    salvar_json(PROF_PATH, dados_prof)

    # Vincula o professor à disciplina
    disciplinas[disciplina_encontrada]["professor"] = {
        "ra": novo_ra,
        "nome": nome,
        "email": email
    }
    disciplinas[disciplina_encontrada]["codigo_acesso"] = None  # invalida o código
    salvar_json(DISCIPLINAS_PATH, disciplinas)

    print(f"\n✅ Cadastro concluído com sucesso!")
    print(f"RA do professor: {novo_ra}")
    input("Pressione ENTER para continuar...")

def cadastro_aluno():
    dados_alunos = carregar_json(ALUNO_PATH)
    if "alunos" not in dados_alunos:
        dados_alunos["alunos"] = []

    disciplinas = carregar_json(DISCIPLINAS_PATH)

    print("\n=== CADASTRAR ALUNO ===")

    nome = input("Nome completo: ").strip()
    cpf = input("CPF: ").strip()
    telefone = input("Telefone: ").strip()
    email = input("E-mail: ").strip()
    senha = input("Senha: ").strip()

    ra = gerar_ra_aluno()

    print("\n=== Escolha uma disciplina ===")
    nomes_disc = list(disciplinas.keys())

    if not nomes_disc:
        print("❌ Nenhuma disciplina cadastrada no sistema.")
        return

    for i, d in enumerate(nomes_disc, 1):
        print(f"{i}. {d}")

    try:
        esc = int(input("Escolha (número): ").strip()) - 1
        if esc < 0 or esc >= len(nomes_disc):
            raise ValueError
        disciplina_escolhida = nomes_disc[esc]
    except:
        print("❌ Escolha inválida.")
        return

    novo_aluno = {
        "nome": nome,
        "cpf": cpf,
        "telefone": telefone,
        "email": email,
        "senha": senha,
        "ra": ra,
        "disciplina": disciplina_escolhida,
        "notas": [],
        "media": None,
        "bloqueado": False
    }

    dados_alunos["alunos"].append(novo_aluno)
    salvar_json(ALUNO_PATH, dados_alunos)

    disciplina = disciplinas.get(disciplina_escolhida)
    disciplina.setdefault("alunos", [])

    disciplina["alunos"].append({
        "nome": nome,
        "ra": ra
    })

    disciplinas[disciplina_escolhida] = disciplina
    salvar_json(DISCIPLINAS_PATH, disciplinas)

    print(f"\n✅ Cadastro realizado com sucesso!")
    print(f"📌 Seu RA é: {ra}")
    print(f"📘 Disciplina matriculada: {disciplina_escolhida}")
    input("\nPressione ENTER para continuar...")

# 5) Painel Principal Godmode

def painel_admin_godmode():
    while True:
        print("\n=== PAINEL ADMINISTRATIVO (GODMODE) ===")
        print("1. Gerenciar administradores")
        print("2. Gerenciar professores")
        print("3. Gerenciar alunos")
        print("4. Criar disciplinas")
        print("5. Gerenciar disciplinas")
        print("6. Gerar relatórios (PDF)") 
        print("7. Voltar")

        op = input("Escolha uma opção: ").strip()

        if op == "1":
            gerenciar_administradores_godmode()
        elif op == "2":
            gerenciar_professores_godmode()
        elif op == "3":
            gerenciar_alunos_godmode()
        elif op == "4":
            criar_disciplina_completa()
        elif op == "5":
            gerenciar_disciplinas_godmode()
        elif op == "6":
            menu_relatorios_godmode()  
        elif op == "7":
            break
        else:
            print("❌ Opção inválida.")

# 6) Gerenciamento Administradores - Godmode

def gerenciar_administradores_godmode():
    while True:
        print("\n=== GERENCIAR ADMINISTRADORES ===")
        print("1. Gerar código para novo administrador limitado")
        print("2. Listar administradores")
        print("3. Bloquear / Desbloquear administrador")
        print("4. Voltar")

        op = input("Escolha uma opção: ").strip()

        if op == "1":
            gerar_token_admin_limitado()

        elif op == "2":
            dados = carregar_json(ADM_PATH).get("administradores", [])
            if not dados:
                print("Nenhum administrador cadastrado.")
            else:
                print("\nAdministradores cadastrados:")
                for a in dados:
                    print(f"- {a.get('nome')} (RA: {a.get('ra')}) "
                          f"Tipo: {a.get('tipo','?')} "
                          f"Bloqueado: {a.get('bloqueado', False)}")

        elif op == "3":
            dados = carregar_json(ADM_PATH)
            admins = dados.get("administradores", [])
            if not admins:
                print("Nenhum administrador cadastrado.")
                continue

            print("\nAdministradores:")
            for i, a in enumerate(admins, 1):
                print(f"{i}. {a.get('nome')} (RA: {a.get('ra')}) - Bloqueado: {a.get('bloqueado', False)}")

            try:
                sel = int(input("Escolha o número do administrador: ").strip()) - 1
            except ValueError:
                print("Entrada inválida.")
                continue

            if sel < 0 or sel >= len(admins):
                print("Opção inválida.")
                continue

            admins[sel]["bloqueado"] = not admins[sel].get("bloqueado", False)
            print(f"Novo status: Bloqueado = {admins[sel]['bloqueado']}")

            dados["administradores"] = admins
            salvar_json(ADM_PATH, dados)

        elif op == "4":
            break

        else:
            print("❌ Opção inválida.")

def gerar_token_admin_limitado():
    dados = carregar_json(ADM_PATH)
    if "tokens_pendentes" not in dados:
        dados["tokens_pendentes"] = []

    token = f"ADM-TK{randint(1000, 9999)}"

    dados["tokens_pendentes"].append({
        "token": token,
        "usado": False
    })

    salvar_json(ADM_PATH, dados)
    print(f"\n🔐 Token gerado com sucesso: {token}")
    print("Esse código deve ser entregue ao novo administrador para cadastro.")

# 7) Gerenciamento de Usuários - Godmode

def gerenciar_professores_godmode():
    while True:
        print("\n=== GERENCIAR PROFESSORES ===")
        print("1. Gerar código para novo professor")
        print("2. Listar professores")
        print("3. Bloquear / Desbloquear professor")
        print("4. Voltar")

        op = input("Escolha uma opção: ").strip()

        if op == "1":
            disciplinas = carregar_json(DISCIPLINAS_PATH)
            if not disciplinas:
                print("⚠️ Nenhuma disciplina cadastrada. Crie uma antes de gerar código.")
                continue

            print("\nDisciplinas disponíveis:")
            nomes = list(disciplinas.keys())
            for i, nome in enumerate(nomes, 1):
                print(f"{i}. {nome}")

            try:
                escolha = int(input("Escolha a disciplina (número): ").strip()) - 1
            except ValueError:
                print("Entrada inválida.")
                continue

            if escolha < 0 or escolha >= len(nomes):
                print("Opção inválida.")
                continue

            nome_disciplina = nomes[escolha]
            codigo = gerar_codigo_disciplina(nome_disciplina)
            disciplinas[nome_disciplina]["codigo_acesso"] = codigo
            salvar_json(DISCIPLINAS_PATH, disciplinas)
            print(f"\n✅ Código de acesso gerado para a disciplina '{nome_disciplina}': {codigo}")

        elif op == "2":
            dados_prof = carregar_json(PROF_PATH).get("professores", [])
            if not dados_prof:
                print("Nenhum professor cadastrado.")
            else:
                print("\nProfessores cadastrados:")
                for p in dados_prof:
                    disciplina = p.get("disciplina", "Não associada")
                    print(f"- {p.get('nome')} (RA: {p.get('ra')}) "
                          f"— Disciplina: {disciplina} "
                          f"— Bloqueado: {p.get('bloqueado', False)}")

        elif op == "3":
            dados = carregar_json(PROF_PATH)
            profs = dados.get("professores", [])
            if not profs:
                print("Nenhum professor cadastrado.")
                continue

            print("\nProfessores:")
            for i, p in enumerate(profs, 1):
                print(f"{i}. {p.get('nome')} (RA: {p.get('ra')}) - Bloqueado: {p.get('bloqueado', False)}")

            try:
                sel = int(input("Escolha o número do professor: ").strip()) - 1
            except ValueError:
                print("Entrada inválida.")
                continue

            if sel < 0 or sel >= len(profs):
                print("Opção inválida.")
                continue

            profs[sel]["bloqueado"] = not profs[sel].get("bloqueado", False)
            print(f"Novo status: Bloqueado = {profs[sel]['bloqueado']}")

            dados["professores"] = profs
            salvar_json(PROF_PATH, dados)

        elif op == "4":
            break

        else:
            print("❌ Opção inválida.")

def gerenciar_alunos_godmode():
    while True:
        print("\n=== GERENCIAR ALUNOS ===")
        print("1. Listar alunos")
        print("2. Bloquear / Desbloquear aluno")
        print("3. Voltar")

        op = input("Escolha uma opção: ").strip()

        if op == "1":
            dados_alunos = carregar_json(ALUNO_PATH).get("alunos", [])
            if not dados_alunos:
                print("Nenhum aluno cadastrado.")
            else:
                print("\nAlunos cadastrados:")
                for a in dados_alunos:
                    print(f"- {a.get('nome')} (RA: {a.get('ra')}) "
                          f"— Bloqueado: {a.get('bloqueado', False)} "
                          f"— Nota: {a.get('nota', 'Sem nota')}")

        elif op == "2":
            dados = carregar_json(ALUNO_PATH)
            alunos = dados.get("alunos", [])
            if not alunos:
                print("Nenhum aluno cadastrado.")
                continue

            print("\nAlunos:")
            for i, a in enumerate(alunos, 1):
                print(f"{i}. {a.get('nome')} (RA: {a.get('ra')}) - Bloqueado: {a.get('bloqueado', False)}")

            try:
                sel = int(input("Escolha o número do aluno: ").strip()) - 1
            except ValueError:
                print("Entrada inválida.")
                continue

            if sel < 0 or sel >= len(alunos):
                print("Opção inválida.")
                continue

            alunos[sel]["bloqueado"] = not alunos[sel].get("bloqueado", False)
            print(f"Novo status: Bloqueado = {alunos[sel]['bloqueado']}")

            dados["alunos"] = alunos
            salvar_json(ALUNO_PATH, dados)

        elif op == "3":
            break

        else:
            print("❌ Opção inválida.")

# 9) Gerenciamento de Disciplinas - Godmode    

def gerenciar_disciplinas_godmode():
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    if not disciplinas:
        print("Nenhuma disciplina cadastrada.")
        return

    nomes = list(disciplinas.keys())
    print("\nDisciplinas disponíveis:")
    for i, n in enumerate(nomes, 1):
        print(f"{i}. {n}")
    try:
        escolha = int(input("Escolha a disciplina (número): ").strip()) - 1
    except ValueError:
        print("Entrada inválida.")
        return
    if escolha < 0 or escolha >= len(nomes):
        print("Opção inválida.")
        return

    nome_sel = nomes[escolha]
    disc = disciplinas[nome_sel]

    while True:
        print(f"\n=== GERENCIANDO DISCIPLINA (GODMODE): {nome_sel} ===")
        print("1. Gerar código de acesso para professor")
        print("2. Ver professor e alunos")
        print("3. Definir horário da disciplina")
        print("4. Editar horário da disciplina")
        print("5. Informações da disciplina")
        print("6. Voltar")

        op = input("Escolha uma opção: ").strip()

        if op == "1":
            codigo = gerar_codigo_disciplina(nome_sel)
            disc["codigo_acesso"] = codigo
            disciplinas[nome_sel] = disc
            salvar_json(DISCIPLINAS_PATH, disciplinas)
            print(f"Código gerado: {codigo}")

        elif op == "2":
            prof = disc.get("professor")
            alunos = disc.get("alunos", [])
            print("\n👨‍🏫 Professor responsável:")
            if prof:
                for k, v in prof.items():
                    print(f"  {k}: {v}")
            else:
                print("Nenhum professor associado.")
            print("\n👨‍🎓 Alunos matriculados:")
            if alunos:
                for a in alunos:
                    print(f"- {a.get('nome')} (RA: {a.get('ra')}) — CPF: {a.get('cpf','N/A')} — E-mail: {a.get('email','N/A')}")
            else:
                print("Nenhum aluno cadastrado.")

        elif op == "3":
            definir_horario_disciplina(nome_sel, disciplinas)

        elif op == "4":
            editar_horario_disciplina(nome_sel, disciplinas)

        elif op == "5":
            mostrar_informacoes_disciplina_godmode(nome_sel, disciplinas)

        elif op == "6":
            break
        else:
            print("❌ Opção inválida.")

def criar_disciplina_completa():
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    if not isinstance(disciplinas, dict):
        disciplinas = {}

    print("\n=== CRIAR NOVA DISCIPLINA ===")
    nome = input("Nome da nova disciplina: ").strip().title()

    if not nome:
        print("❌ Nome inválido.")
        return

    if nome in disciplinas:
        print("⚠️ Essa disciplina já existe.")
        return

    novo_id = f"DISC{len(disciplinas) + 1:03}"

    prefixo = nome[:3].upper()
    sufixo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    codigo = f"{prefixo}-{sufixo}"

    disciplinas[nome] = {
        "id": novo_id,
        "professor": None,
        "alunos": [],
        "codigo_acesso": codigo,
        "horario": None
    }

    salvar_json(DISCIPLINAS_PATH, disciplinas)

    print("\n✅ Disciplina criada com sucesso!")
    print(f"📘 Nome: {nome}")
    print(f"🆔 ID: {novo_id}")
    print(f"🔐 Código de acesso para professor: {codigo}")

def gerar_codigo_disciplina(nome_disciplina):
    prefixo = nome_disciplina[:3].upper()
    sufixo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{prefixo}-{sufixo}"

def mostrar_informacoes_disciplina_godmode(nome_disciplina, disciplinas):
    os.system("cls" if os.name == "nt" else "clear")
    disc = disciplinas.get(nome_disciplina)

    if not disc:
        print("⚠️ Disciplina não encontrada.")
        input("ENTER para voltar...")
        return

    print("=" * 60)
    print(f"📘 INFORMAÇÕES — {nome_disciplina}")
    print("=" * 60)

    print(f"ID: {disc.get('id', 'N/A')}\n")

    print("👨‍🏫 PROFESSOR RESPONSÁVEL (RA):")
    prof = disc.get("professor")
    if prof:
        print(f"  Nome: {prof.get('nome','N/A')}")
        print(f"  RA: {prof.get('ra','N/A')}")
    else:
        print("  Nenhum professor vinculado.")
    print()

    print("🕒 HORÁRIOS CADASTRADOS:")
    horarios = disc.get("horarios", [])
    if horarios:
        for h in horarios:
            print(f"  - {h.get('dia')} das {h.get('inicio')} às {h.get('fim')}")
    else:
        print("  Nenhum horário definido.")
    print()

    print("📝 PROVAS:")
    provas = disc.get("provas", [])
    if provas:
        for p in provas:
            print(f"  - {p.get('titulo')} (Peso {p.get('peso',0)} — {len(p.get('questoes',[]))} questões)")
    else:
        print("  Nenhuma prova cadastrada.")
    print()

    print("👨‍🎓 ALUNOS MATRICULADOS:")
    alunos = disc.get("alunos", [])

    if alunos:
        pesos = [p.get("peso", 0) for p in provas]

        for aluno in alunos:
            nome = aluno.get("nome", "N/A")
            ra = aluno.get("ra", "N/A")
            notas = aluno.get("notas", [])

            if notas and pesos:
                lista_calc = []
                for i in range(len(pesos)):
                    nota = notas[i] if i < len(notas) else 0
                    peso = pesos[i] if i < len(pesos) else 0
                    lista_calc.append({"nota": nota, "peso": peso})

                media = calcular_media_ponderada(lista_calc)
                status = "APROVADO ✅" if media >= 7 else "REPROVADO ❌"
            else:
                media = "N/A"
                status = "N/A"

            print(f"  Nome: {nome}")
            print(f"  RA: {ra}")
            print(f"  Média Final: {media} — {status}\n")

    else:
        print("  Nenhum aluno matriculado.")
    print()

    print("🔑 CÓDIGO DE ACESSO:")
    codigo = disc.get("codigo_acesso")
    if codigo:
        print(f"  Código atual: {codigo}")
    else:
        print("  Nenhum código gerado.")
    print("=" * 60)

    input("Pressione ENTER para voltar...")

def definir_horario_disciplina(nome_disciplina, disciplinas):
    disc = disciplinas.get(nome_disciplina)
    if not disc:
        print("Disciplina não encontrada.")
        return

    dias_validos = ["segunda", "terca", "quarta", "quinta", "sexta"]
    print("\nDias disponíveis: segunda, terça, quarta, quinta, sexta")
    dia = input("Dia da semana: ").strip().lower()

    if dia not in dias_validos:
        print("❌ Dia inválido. Use apenas segunda a sexta.")
        return

    try:
        hora_inicio = int(input("Hora de início (19 a 21): ").strip())
        hora_fim = int(input("Hora de término (20 a 22): ").strip())
    except ValueError:
        print("❌ Insira apenas números inteiros.")
        return

    if not (19 <= hora_inicio < hora_fim <= 22):
        print("❌ Horário fora do intervalo permitido (19h às 22h).")
        return

    conflito = verificar_conflito_horario(disciplinas, dia, hora_inicio, hora_fim, nome_disciplina)
    if conflito:
        print(f"⚠️ Conflito detectado! A disciplina '{conflito}' já ocupa esse horário.")
        return

    disciplinas[nome_disciplina]["horario"] = {
        "dia": dia.capitalize(),
        "inicio": f"{hora_inicio}:00",
        "fim": f"{hora_fim}:00"
    }
    salvar_json(DISCIPLINAS_PATH, disciplinas)
    print(f"✅ Horário definido para {nome_disciplina}: {dia.capitalize()} das {hora_inicio}:00 às {hora_fim}:00")

def editar_horario_disciplina(nome_disciplina, disciplinas):
    disc = disciplinas.get(nome_disciplina)
    if not disc:
        print("Disciplina não encontrada.")
        return

    horario_atual = disc.get("horario")
    print("\n=== EDITAR HORÁRIO DA DISCIPLINA ===")

    if horario_atual:
        print(f"Horário atual: {horario_atual['dia']} — {horario_atual['inicio']} às {horario_atual['fim']}")
    else:
        print("Nenhum horário definido ainda.")

    dias_validos = ["segunda", "terca", "quarta", "quinta", "sexta"]
    print("\nDias disponíveis: segunda, terça, quarta, quinta, sexta")
    dia = input("Novo dia da semana: ").strip().lower()

    if dia not in dias_validos:
        print("❌ Dia inválido. Use apenas segunda a sexta.")
        return

    try:
        hora_inicio = int(input("Hora de início (19 a 21): ").strip())
        hora_fim = int(input("Hora de término (20 a 22): ").strip())
    except ValueError:
        print("❌ Insira apenas números inteiros.")
        return

    if not (19 <= hora_inicio < hora_fim <= 22):
        print("❌ Horário fora do intervalo permitido (19h às 22h).")
        return

    conflito = verificar_conflito_horario(disciplinas, dia, hora_inicio, hora_fim, nome_disciplina)
    if conflito:
        print(f"⚠️ Conflito detectado! A disciplina '{conflito}' já ocupa esse horário.")
        return

    disciplinas[nome_disciplina]["horario"] = {
        "dia": dia.capitalize(),
        "inicio": f"{hora_inicio}:00",
        "fim": f"{hora_fim}:00"
    }
    salvar_json(DISCIPLINAS_PATH, disciplinas)
    print(f"✅ Horário atualizado para {nome_disciplina}: {dia.capitalize()} das {hora_inicio}:00 às {hora_fim}:00")

# 10) Relatórios

def menu_relatorios_godmode():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("==============================================")
        print("📄 GERAR RELATÓRIOS — ADMINISTRADOR GODMODE")
        print("==============================================")
        print("1. Relatório de uma disciplina")
        print("2. Relatório de professores")
        print("3. Relatório de alunos")
        print("4. Voltar")
        print("----------------------------------------------")

        op = input("Escolha uma opção: ").strip()

        if op == "1":
            gerar_relatorio_disciplina_menu()
        elif op == "2":
            gerar_relatorio_professores()
            input("\nPressione ENTER para continuar...")
        elif op == "3":
            gerar_relatorio_alunos()
            input("\nPressione ENTER para continuar...")
        elif op == "4":
            break
        else:
            print("❌ Opção inválida.")
            input("ENTER para continuar...")

def gerar_relatorio_disciplina_menu():
    disciplinas = carregar_json(DISCIPLINAS_PATH)

    if not disciplinas:
        print("⚠️ Nenhuma disciplina cadastrada.")
        input("ENTER para continuar...")
        return

    print("\n=== Escolha uma disciplina para gerar relatório ===")
    nomes = list(disciplinas.keys())

    for i, nome in enumerate(nomes, 1):
        print(f"{i}. {nome}")

    try:
        esc = int(input("\nNúmero da disciplina: ").strip()) - 1
        if esc < 0 or esc >= len(nomes):
            raise ValueError
    except:
        print("❌ Opção inválida.")
        input("ENTER para continuar...")
        return

    nome_disc = nomes[esc]
    gerar_relatorio_disciplina(nome_disc)

    input("\nPressione ENTER para continuar...")

def gerar_relatorio_disciplina(disciplina_nome):
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    disc = disciplinas.get(disciplina_nome)

    if not disc:
        print("⚠️ Disciplina não encontrada.")
        return

    caminho_pdf = f"Relatorio_{disciplina_nome}.pdf"
    pdf = canvas.Canvas(caminho_pdf, pagesize=A4)

    x = 50
    y = 800

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(x, y, f"Relatório da Disciplina — {disciplina_nome}")
    y -= 40

    pdf.setFont("Helvetica", 12)

    # ID
    pdf.drawString(x, y, f"ID: {disc.get('id', 'N/A')}")
    y -= 20

    # Professor
    prof = disc.get("professor")
    if prof:
        pdf.drawString(x, y, f"Professor: {prof.get('nome')} — RA: {prof.get('ra')}")
    else:
        pdf.drawString(x, y, "Professor: Nenhum cadastrado")
    y -= 30

    # Horários
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x, y, "Horários:")
    y -= 20
    pdf.setFont("Helvetica", 12)

    horarios = disc.get("horarios", [])
    if horarios:
        for h in horarios:
            pdf.drawString(x, y, f"- {h['dia']} das {h['inicio']} às {h['fim']}")
            y -= 15
    else:
        pdf.drawString(x, y, "Nenhum horário definido.")
        y -= 20

    y -= 20

    # Provas
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x, y, "Provas:")
    y -= 20
    pdf.setFont("Helvetica", 12)

    provas = disc.get("provas", [])
    if provas:
        for p in provas:
            pdf.drawString(x, y, f"- {p['titulo']} (Peso {p['peso']} — {len(p['questoes'])} questões)")
            y -= 15
    else:
        pdf.drawString(x, y, "Nenhuma prova cadastrada.")
        y -= 20

    y -= 30

    # Alunos + médias + aprovado/reprovado
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x, y, "Alunos matriculados:")
    y -= 25
    pdf.setFont("Helvetica", 12)

    alunos = disc.get("alunos", [])
    provas_pesos = [p.get("peso", 0) for p in provas]

    medias = []
    aprovados = 0
    reprovados = 0

    if alunos:
        for aluno in alunos:
            nome = aluno.get("nome")
            ra = aluno.get("ra")
            notas = aluno.get("notas", [])

            # média automática
            if notas and provas_pesos:
                lista_calc = []
                for i in range(len(provas_pesos)):
                    nota = notas[i] if i < len(notas) else 0
                    peso = provas_pesos[i] if i < len(provas_pesos) else 0
                    lista_calc.append({"nota": nota, "peso": peso})

                media = calcular_media_ponderada(lista_calc)
                medias.append(media)

                status = "APROVADO" if media >= 7 else "REPROVADO"

                if media >= 7:
                    aprovados += 1
                else:
                    reprovados += 1
            else:
                media = "N/A"
                status = "N/A"

            pdf.drawString(x, y, f"{nome} — RA: {ra} — Média: {media} — {status}")
            y -= 15

            if y < 100:  # quebra de página automática
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y = 800
    else:
        pdf.drawString(x, y, "Nenhum aluno matriculado.")
        y -= 20

    # Estatísticas
    if medias:
        media_turma = round(sum(medias) / len(medias), 2)
        taxa_aprov = round((aprovados / len(medias)) * 100, 2)
        taxa_reprov = 100 - taxa_aprov

        y -= 30
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(x, y, "Estatísticas da Turma:")
        y -= 20
        pdf.setFont("Helvetica", 12)

        pdf.drawString(x, y, f"Média geral da turma: {media_turma}")
        y -= 15
        pdf.drawString(x, y, f"Taxa de aprovação: {taxa_aprov}%")
        y -= 15
        pdf.drawString(x, y, f"Taxa de reprovação: {taxa_reprov}%")
        y -= 25

    pdf.save()
    print(f"📄 Relatório salvo como: {caminho_pdf}")

def gerar_relatorio_professores():
    dados_prof = carregar_json(PROF_PATH).get("professores", [])
    disciplinas = carregar_json(DISCIPLINAS_PATH)

    caminho_pdf = "Relatorio_Professores.pdf"
    pdf = canvas.Canvas(caminho_pdf, pagesize=A4)

    x, y = 50, 800

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(x, y, "Relatório de Professores")
    y -= 40

    pdf.setFont("Helvetica", 12)

    for prof in dados_prof:
        nome = prof.get("nome")
        ra = prof.get("ra")
        disc_nome = prof.get("disciplina", "N/A")
        bloqueado = prof.get("bloqueado", False)

        # buscar disciplina
        disc = disciplinas.get(disc_nome, {})
        alunos = disc.get("alunos", [])
        provas = disc.get("provas", [])

        pdf.drawString(x, y, f"{nome} — RA: {ra}")
        y -= 15
        pdf.drawString(x, y, f"Disciplina: {disc_nome}")
        y -= 15
        pdf.drawString(x, y, f"Status: {'Bloqueado' if bloqueado else 'Ativo'}")
        y -= 15
        pdf.drawString(x, y, f"Alunos na disciplina: {len(alunos)}")
        y -= 15
        pdf.drawString(x, y, f"Provas criadas: {len(provas)}")
        y -= 30

        if y < 100:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = 800

    pdf.save()
    print(f"📄 Relatório salvo como: {caminho_pdf}")

def gerar_relatorio_alunos():
    alunos = carregar_json(ALUNO_PATH).get("alunos", [])
    disciplinas = carregar_json(DISCIPLINAS_PATH)

    caminho_pdf = "Relatorio_Alunos.pdf"
    pdf = canvas.Canvas(caminho_pdf, pagesize=A4)

    x, y = 50, 800

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(x, y, "Relatório de Alunos")
    y -= 40

    pdf.setFont("Helvetica", 12)

    for aluno in alunos:
        nome = aluno.get("nome")
        ra = aluno.get("ra")

        pdf.drawString(x, y, f"{nome} — RA: {ra}")
        y -= 20

        # verificar disciplinas onde o aluno está matriculado
        for nome_disc, disc in disciplinas.items():
            disc_alunos = disc.get("alunos", [])
            provas = disc.get("provas", [])

            # aluno matriculado?
            for a in disc_alunos:
                if a.get("ra") == ra:
                    notas = a.get("notas", [])
                    pesos = [p.get("peso", 0) for p in provas]

                    if notas and pesos:
                        lista = []
                        for i in range(len(pesos)):
                            nota = notas[i] if i < len(notas) else 0
                            peso = pesos[i] if i < len(pesos) else 0
                            lista.append({"nota": nota, "peso": peso})

                        media = calcular_media_ponderada(lista)
                        status = "APROVADO" if media >= 7 else "REPROVADO"
                    else:
                        media = "N/A"
                        status = "N/A"

                    pdf.drawString(x, y, f"- {nome_disc}: Média {media} — {status}")
                    y -= 15

        pdf.drawString(x, y, "-" * 60)
        y -= 25

        if y < 100:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = 800

    pdf.save()
    print(f"📄 Relatório salvo como: {caminho_pdf}")

# 11) Painel Administrador Limitado

def painel_admin_limitado():
    """Painel principal do administrador limitado."""
    while True:
        print("\n=== PAINEL ADMINISTRATIVO (LIMITADO) ===")
        print("1. Gerenciar professores")
        print("2. Gerenciar alunos")
        print("3. Gerenciar disciplinas")
        print("4. Voltar")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            gerenciar_professores_limitado()
        elif opcao == "2":
            gerenciar_alunos_limitado()
        elif opcao == "3":
            gerenciar_disciplinas_limitado()
        elif opcao == "4":
            print("\nRetornando ao menu principal...\n")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

# 12) Gerenciamento Administrador Limitado

def gerenciar_professores_limitado():
    while True:
        print("\n=== GERENCIAR PROFESSORES ===")
        print("1. Gerar código para novo professor")
        print("2. Visualizar professores cadastrados")
        print("3. Voltar")

        op = input("Escolha uma opção: ").strip()

        if op == "1":
            disciplinas = carregar_json(DISCIPLINAS_PATH)
            if not disciplinas or not isinstance(disciplinas, dict):
                print("⚠️ Nenhuma disciplina cadastrada.")
                input("Pressione ENTER para continuar...")
                continue

            nomes = list(disciplinas.keys())
            print("\nDisciplinas disponíveis:")
            for i, nome in enumerate(nomes, 1):
                print(f"{i}. {nome}")
            print(f"{len(nomes)+1}. Voltar")

            try:
                escolha = int(input("Escolha a disciplina (número): ").strip()) - 1
            except ValueError:
                print("Entrada inválida.")
                continue

            if escolha == len(nomes):
                break
            if escolha < 0 or escolha >= len(nomes):
                print("Opção inválida.")
                continue

            nome_disciplina = nomes[escolha]
            codigo = gerar_codigo_disciplina(nome_disciplina)
            disciplinas[nome_disciplina]["codigo_acesso"] = codigo
            salvar_json(DISCIPLINAS_PATH, disciplinas)
            print(f"\n✅ Código gerado para '{nome_disciplina}': {codigo}")
            input("Pressione ENTER para continuar...")

        elif op == "2":
            dados_prof = carregar_json(PROF_PATH).get("professores", [])
            if not dados_prof:
                print("Nenhum professor cadastrado.")
            else:
                print("\nProfessores cadastrados:")
                for p in dados_prof:
                    print(f"- {p.get('nome')} (RA: {p.get('ra')}) — Disciplina: {p.get('disciplina', 'N/A')}")
            input("Pressione ENTER para continuar...")

        elif op == "3":
            break
        else:
            print("❌ Opção inválida.")

def gerenciar_alunos_limitado():
    while True:
        print("\n=== GERENCIAR ALUNOS ===")
        print("1. Visualizar alunos cadastrados")
        print("2. Voltar")

        op = input("Escolha uma opção: ").strip()

        if op == "1":
            alunos = carregar_json(ALUNO_PATH).get("alunos", [])
            if not alunos:
                print("Nenhum aluno cadastrado.")
            else:
                print("\nAlunos cadastrados:")
                for a in alunos:
                    print(f"- {a.get('nome')} (RA: {a.get('ra')}) — Nota: {a.get('nota', 'Sem nota')}")
            input("Pressione ENTER para continuar...")

        elif op == "2":
            break
        else:
            print("❌ Opção inválida.")

def gerenciar_disciplinas_limitado():
    while True:
        disciplinas = carregar_json(DISCIPLINAS_PATH)
        if not disciplinas or not isinstance(disciplinas, dict):
            print("⚠️ Nenhuma disciplina cadastrada.")
            input("Pressione ENTER para voltar...")
            return

        nomes = list(disciplinas.keys())
        print("\n=== GERENCIAR DISCIPLINAS ===")
        for i, n in enumerate(nomes, 1):
            print(f"{i}. {n}")
        print(f"{len(nomes)+1}. Voltar")

        try:
            escolha = int(input("Escolha a disciplina (número): ").strip()) - 1
        except ValueError:
            print("Entrada inválida.")
            continue

        if escolha == len(nomes):
            break
        if escolha < 0 or escolha >= len(nomes):
            print("Opção inválida.")
            continue

        nome_sel = nomes[escolha]
        disc = disciplinas[nome_sel]
        submenu_disciplinas_limitado(nome_sel, disc, disciplinas)

def submenu_disciplinas_limitado(nome, disc, disciplinas):
    while True:
        print(f"\n=== DISCIPLINA: {nome} ===")
        print("1. Gerar código de acesso para professor")
        print("2. Ver professor e alunos")
        print("3. Informações da disciplina")
        print("4. Voltar")

        op = input("Escolha uma opção: ").strip()

        if op == "1":
            codigo = gerar_codigo_disciplina(nome)
            disc["codigo_acesso"] = codigo
            disciplinas[nome] = disc
            salvar_json(DISCIPLINAS_PATH, disciplinas)
            print(f"✅ Novo código gerado: {codigo}")
            input("Pressione ENTER para continuar...")

        elif op == "2":
            prof = disc.get("professor")
            alunos = disc.get("alunos", [])
            print("\nProfessor responsável:")
            if prof:
                print(f"- {prof.get('nome')} (RA: {prof.get('ra')})")
            else:
                print("Nenhum professor associado.")
            print("\nAlunos matriculados:")
            if alunos:
                for a in alunos:
                    print(f"- {a.get('nome')} (RA: {a.get('ra')}) — Nota: {a.get('nota','-')}")
            else:
                print("Nenhum aluno cadastrado.")
            input("Pressione ENTER para continuar...")

        elif op == "3":
            mostrar_informacoes_disciplina(nome, disciplinas)
            input("Pressione ENTER para continuar...")

        elif op == "4":
            break
        else:
            print("❌ Opção inválida.")

# 13) Painel do Professor

def painel_professor(professor):
    while True:
        print("\n===========================================")
        print("        🎓 PAINEL DO PROFESSOR")
        print("===========================================")
        print(f"Disciplina: {professor.get('disciplina')}")
        print("-------------------------------------------")
        print("1. Criar conteúdo (aulas)")
        print("2. Criar prova")
        print("3. Visualizar conteúdo criado")
        print("4. Visualizar provas criadas")
        print("5. Visualizar alunos (RA + Nota)")
        print("6. Enviar notas aos alunos")
        print("7. Sair")
        print("-------------------------------------------")

        op = input("Escolha: ").strip()

        if op == "1":
            criar_aula_professor(professor)
        elif op == "2":
            criar_prova_professor(professor)
        elif op == "3":
            listar_aulas_professor(professor)
        elif op == "4":
            listar_provas_professor(professor)
        elif op == "5":
            visualizar_alunos_professor(professor)
        elif op == "6":
            enviar_notas_professor(professor)
        elif op == "7":
            break
        else:
            print("❌ Opção inválida.")

def listar_provas_professor(professor):
    nome_disc = professor.get("disciplina")
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    disc = disciplinas.get(nome_disc)

    print(f"\n=== PROVAS DA DISCIPLINA: {nome_disc} ===")

    provas = disc.get("provas", [])
    if not provas:
        print("⚠️ Nenhuma prova cadastrada ainda.")
        input("ENTER para voltar...")
        return

    for i, prova in enumerate(provas, 1):
        titulo = prova.get("titulo", "Sem título")
        peso = prova.get("peso", 0)
        print(f"{i}. {titulo} (Peso {peso})")

    input("\nPressione ENTER para voltar...")

def ver_alunos_professor(professor):
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    disc = disciplinas.get(professor.get("disciplina"))
    if not disc or not disc.get("alunos"):
        print("\nNenhum aluno cadastrado nessa disciplina.")
        input("Pressione ENTER para continuar...")
        return

    print(f"\n📚 Alunos na disciplina {professor.get('disciplina')}:")
    for a in disc["alunos"]:
        status = "PENDENTE" if a.get("pendente", False) else "ENVIADA"
        print(f"- {a['nome']} (RA: {a['ra']}) — Nota: {a.get('nota','-')} [{status}]")
    input("Pressione ENTER para continuar...")

def enviar_notas_professor(professor):
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    disc = disciplinas.get(professor.get("disciplina"))
    if not disc or not disc.get("alunos"):
        print("\nNenhum aluno nessa disciplina.")
        input("Pressione ENTER para continuar...")
        return

    pendentes = [a for a in disc["alunos"] if a.get("pendente", False)]
    if not pendentes:
        print("\nNenhuma nota pendente para envio.")
        input("Pressione ENTER para continuar...")
        return

    print("\n📤 Notas pendentes de aprovação:")
    for i, a in enumerate(pendentes, 1):
        print(f"{i}. {a['nome']} (RA: {a['ra']}) — Nota: {a.get('nota')}")

    try:
        sel = int(input("\nSelecione um aluno para enviar nota (0 para voltar): "))
    except ValueError:
        print("Entrada inválida.")
        return

    if sel == 0:
        return
    if sel < 1 or sel > len(pendentes):
        print("Opção inválida.")
        return

    aluno_sel = pendentes[sel - 1]
    print(f"\nConfirmar envio da nota para {aluno_sel['nome']}? (S/N)")
    conf = input("> ").strip().lower()
    if conf == "s":
        for a in disc["alunos"]:
            if a["ra"] == aluno_sel["ra"]:
                a["pendente"] = False
                break
        salvar_json(DISCIPLINAS_PATH, disciplinas)
        print(f"✅ Nota de {aluno_sel['nome']} enviada com sucesso!")
    else:
        print("Operação cancelada.")
    input("Pressione ENTER para continuar...")

def visualizar_alunos_professor(professor):
    nome_disc = professor.get("disciplina")
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    disc = disciplinas.get(nome_disc)

    print(f"\n=== ALUNOS DA DISCIPLINA: {nome_disc} ===")

    alunos = disc.get("alunos", [])
    if not alunos:
        print("Nenhum aluno matriculado.")
        input("ENTER para voltar...")
        return
    
    provas = disc.get("provas", [])
    if not provas:
        print("⚠️ Não há provas cadastradas ainda. Média não pode ser calculada.")
        return

    for aluno in alunos:
        notas = aluno.get("notas", [])  # o professor envia quando corrige
        pesos = [p.get("peso", 0) for p in provas]

        # lista de {"nota": x, "peso": y}
        lista_calc = []
        for i, peso in enumerate(pesos):
            nota = notas[i] if i < len(notas) else 0
            lista_calc.append({"nota": nota, "peso": peso})

        media = calcular_media_ponderada(lista_calc)

        print(f"\nAluno: {aluno['nome']}")
        print(f"RA: {aluno['ra']}")
        print(f"Média Final: {media}")

    input("\nENTER para voltar...")

# 14) Aulas do Professor

def gerenciar_aulas_professor(professor):
    while True:
        print("\n=== GERENCIAR AULAS ===")
        print("1. Criar nova aula")
        print("2. Ver aulas existentes")
        print("3. Editar aula")
        print("4. Excluir aula")
        print("5. Voltar")

        op = input("Escolha: ").strip()
        if op == "1":
            criar_aula_professor(professor)
        elif op == "2":
            listar_aulas_professor(professor)
        elif op == "3":
            editar_aula_professor(professor)
        elif op == "4":
            excluir_aula_professor(professor)
        elif op == "5":
            break
        else:
            print("❌ Opção inválida.")

def criar_aula_professor(professor):
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    nome_disc = professor.get("disciplina")
    disc = disciplinas.get(nome_disc)

    if not disc:
        print("⚠️ Disciplina não encontrada.")
        return

    try:
        qtd = int(input("Quantas aulas deseja cadastrar? ").strip())
    except ValueError:
        print("Entrada inválida.")
        return

    novas_aulas = []
    for i in range(qtd):
        print(f"\n[Aula {i+1}]")
        titulo = input("Título da aula: ").strip()

        print("\nDigite TODO o conteúdo da aula em uma ÚNICA linha:")
        print("Use números para criar tópicos automaticamente:")
        print("Ex: 1 Introdução 2 Estruturas condicionais 3 Laços de repetição\n")

        conteudo_texto = input("> ").strip()
        if not conteudo_texto:
            print("Conteúdo vazio. Aula ignorada.")
            continue

        # === PARSE AUTOMÁTICO DOS TÓPICOS ===
        partes = re.split(r"(?=\d\s)", conteudo_texto)

        conteudo_formatado = ""
        for parte in partes:
            parte = parte.strip()
            if parte:
                match = re.match(r"(\d+)\s+(.*)", parte)
                if match:
                    num = match.group(1)
                    texto = match.group(2)
                    bloco = textwrap.fill(f"{num}. {texto}", width=80)
                    conteudo_formatado += bloco + "\n\n"
                else:
                    conteudo_formatado += textwrap.fill(parte, width=80) + "\n\n"

        novas_aulas.append({
            "titulo": titulo,
            "conteudo": conteudo_formatado.strip()
        })

    # === RESUMO ANTES DE SALVAR ===
    print("\nResumo das aulas criadas:")
    if not novas_aulas:
        print("Nenhuma aula criada.")
        return

    for a in novas_aulas:
        print(f"- {a['titulo']}")

    confirmar = input("\nDeseja salvar as aulas? (S/N): ").strip().lower()
    if confirmar == "s":
        disc.setdefault("aulas", []).extend(novas_aulas)
        disciplinas[nome_disc] = disc
        salvar_json(DISCIPLINAS_PATH, disciplinas)
        print("✅ Aulas salvas com sucesso!")
    else:
        print("Operação cancelada.")

    input("\nPressione ENTER para continuar...")

def listar_aulas_professor(professor):
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    disc = disciplinas.get(professor.get("disciplina"))
    aulas = disc.get("aulas", [])
    if not aulas:
        print("Nenhuma aula cadastrada.")
        input("Pressione ENTER para continuar...")
        return

    print("\n=== AULAS CADASTRADAS ===")
    for i, aula in enumerate(aulas, 1):
        print(f"{i}. {aula['titulo']}")
    try:
        escolha = int(input("Escolha uma aula para ver (0 para voltar): ").strip())
    except ValueError:
        return
    if escolha == 0:
        return
    if 1 <= escolha <= len(aulas):
        print(f"\n📘 {aulas[escolha-1]['titulo']}\n{'-'*40}\n{aulas[escolha-1]['conteudo']}")
    input("\nPressione ENTER para continuar...")

def editar_aula_professor(professor):
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    nome_disc = professor.get("disciplina")
    disc = disciplinas.get(nome_disc)
    aulas = disc.get("aulas", [])
    if not aulas:
        print("Nenhuma aula para editar.")
        return

    print("\nAulas disponíveis:")
    for i, aula in enumerate(aulas, 1):
        print(f"{i}. {aula['titulo']}")
    try:
        escolha = int(input("Escolha a aula para editar: ").strip()) - 1
    except ValueError:
        return
    if escolha < 0 or escolha >= len(aulas):
        return

    print("Digite o novo conteúdo (ENTER em branco para finalizar):")
    novo_conteudo = []
    while True:
        linha = input("> ")
        if linha == "":
            break
        novo_conteudo.append(linha)

    aulas[escolha]["conteudo"] = "\n".join(novo_conteudo)
    disc["aulas"] = aulas
    disciplinas[nome_disc] = disc
    salvar_json(DISCIPLINAS_PATH, disciplinas)
    print("✅ Aula atualizada com sucesso!")
    input("Pressione ENTER para continuar...")

def excluir_aula_professor(professor):
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    nome_disc = professor.get("disciplina")
    disc = disciplinas.get(nome_disc)
    aulas = disc.get("aulas", [])
    if not aulas:
        print("Nenhuma aula cadastrada.")
        return

    print("\nAulas disponíveis:")
    for i, aula in enumerate(aulas, 1):
        print(f"{i}. {aula['titulo']}")
    try:
        escolha = int(input("Escolha a aula para excluir: ").strip()) - 1
    except ValueError:
        return
    if escolha < 0 or escolha >= len(aulas):
        return

    confirm = input(f"Tem certeza que deseja excluir '{aulas[escolha]['titulo']}'? (S/N): ").strip().lower()
    if confirm == "s":
        aulas.pop(escolha)
        disc["aulas"] = aulas
        disciplinas[nome_disc] = disc
        salvar_json(DISCIPLINAS_PATH, disciplinas)
        print("✅ Aula excluída com sucesso!")
    input("Pressione ENTER para continuar...")

# 15) Provas do Professor

def gerenciar_provas_professor(professor):
    while True:
        print("\n=== GERENCIAR PROVAS ===")
        print("1. Criar nova prova")
        print("2. Ver provas existentes")
        print("3. Editar prova")
        print("4. Excluir prova")
        print("5. Voltar")

        op = input("Escolha: ").strip()
        if op == "1":
            criar_prova_professor(professor)
        elif op == "2":
            listar_provas_professor(professor)
        elif op == "3":
            editar_prova_professor(professor)
        elif op == "4":
            excluir_prova_professor(professor)
        elif op == "5":
            break
        else:
            print("❌ Opção inválida.")

def criar_prova_professor(professor):
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    nome_disc = professor.get("disciplina")
    disc = disciplinas.get(nome_disc)

    if not disc:
        print("⚠️ Disciplina não encontrada.")
        return

    # Verificar pesos já atribuídos
    provas_existentes = disc.get("provas", [])
    peso_atual = sum(p.get("peso", 0) for p in provas_existentes)

    try:
        qtd_provas = int(input("Quantas provas deseja criar? ").strip())
    except ValueError:
        print("Entrada inválida.")
        return

    novas_provas = []
    for p in range(qtd_provas):
        print(f"\n[Prova {p+1}]")
        titulo = input("Título da prova: ").strip()

        try:
            qtd_questoes = int(input("Quantas questões essa prova terá? ").strip())
        except ValueError:
            print("Entrada inválida. Pulando esta prova.")
            continue

        questoes = []
        for q in range(qtd_questoes):
            print(f"\nQuestão {q+1}:")

            pergunta_raw = input("Pergunta: ").strip()
            pergunta = textwrap.fill(pergunta_raw, width=80)

            alternativas = []
            print("\nDigite as 4 alternativas (somente o texto):")
            for i in range(1, 5):
                texto_alt_raw = input(f"Alternativa {i}: ").strip()
                texto_alt = textwrap.fill(f"{i}) {texto_alt_raw}", width=80)
                alternativas.append(texto_alt)

            correta_raw = input("Alternativa correta (1/2/3/4): ").strip()
            try:
                indice = int(correta_raw) - 1
                if indice not in [0,1,2,3]:
                    indice = 0
            except:
                indice = 0

            questoes.append({
                "pergunta": pergunta,
                "alternativas": alternativas,
                "correta": indice
            })

        print("\n=== DEFINIR PESO DA PROVA ===")
        print(f"Peso total disponível restante: {10 - peso_atual}")

        while True:
            try:
                peso = int(input("Peso dessa prova (1 a 10): ").strip())

                # Regras:
                # - peso não pode ser menor que 1
                # - peso não pode exceder o restante disponível
                # - peso_atual + peso <= 10
                if peso < 1:
                    print("⚠️ O peso mínimo é 1.")
                    continue
                if peso_atual + peso > 10:
                    print(f"⚠️ Peso excede o limite. Você ainda tem {10 - peso_atual} disponível.")
                    continue

                break
            except ValueError:
                print("⚠️ Digite um número inteiro válido.")

        peso_atual += peso  # Atualiza o acumulado

        novas_provas.append({
            "titulo": titulo,
            "questoes": questoes,
            "peso": peso
        })

    print(f"\nResumo: {len(novas_provas)} prova(s) criadas.")
    for p in novas_provas:
        print(f" - {p['titulo']} (Peso: {p['peso']}, Questões: {len(p['questoes'])})")

    confirmar = input("Salvar essas provas? (S/N): ").strip().lower()
    if confirmar == "s":
        disc.setdefault("provas", []).extend(novas_provas)
        disciplinas[nome_disc] = disc
        salvar_json(DISCIPLINAS_PATH, disciplinas)
        print("✅ Provas salvas com sucesso!")
    else:
        print("❌ Operação cancelada.")

    input("Pressione ENTER para continuar...")

def listar_provas_professor(professor):
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    nome_disc = professor.get("disciplina")

    if nome_disc not in disciplinas:
        print("\n❌ Erro: disciplina não encontrada!")
        return

    disc = disciplinas[nome_disc]
    provas = disc.get("provas", [])

    print("\n=== PROVAS CADASTRADAS ===")

    if not provas:
        print("Nenhuma prova cadastrada até o momento.")
        return

    for i, prova in enumerate(provas, start=1):
        titulo = prova.get("titulo", "Sem título")
        peso = prova.get("peso", 1)
        print(f"{i}. {titulo}  (Peso {peso})")

    print()

def editar_prova_professor(professor):
    nome_disc = professor.get("disciplina")
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    disc = disciplinas.get(nome_disc)

    provas = disc.get("provas", [])
    if not provas:
        print("⚠️ Não há provas cadastradas.")
        input("ENTER para voltar...")
        return

    print("\n=== EDITAR PROVA ===")
    for i, prova in enumerate(provas, 1):
        print(f"{i}. {prova['titulo']} (Peso {prova.get('peso', 0)})")

    try:
        esc = int(input("\nSelecione a prova: ").strip()) - 1
        if esc < 0 or esc >= len(provas):
            raise ValueError
    except:
        print("Opção inválida.")
        return

    prova = provas[esc]

    while True:
        print(f"\n=== Editando: {prova['titulo']} ===")
        print("1. Editar título")
        print("2. Editar peso")
        print("3. Editar questões")
        print("4. Voltar")

        op = input("Escolha: ").strip()

        if op == "1":
            novo = input("Novo título: ").strip()
            if novo:
                prova["titulo"] = novo
                salvar_json(DISCIPLINAS_PATH, disciplinas)
                print("✔ Título atualizado!")

        elif op == "2":
            try:
                novo_peso = int(input("Novo peso da prova: "))
                if novo_peso < 1 or novo_peso > 10:
                    print("Peso inválido (1 a 10).")
                else:
                    prova["peso"] = novo_peso
                    salvar_json(DISCIPLINAS_PATH, disciplinas)
                    print("✔ Peso atualizado!")
            except:
                print("Entrada inválida.")

        elif op == "3":
            editar_questoes_prova(prova, disciplinas, nome_disc)

        elif op == "4":
            break

        else:
            print("Opção inválida.")

def editar_questoes_prova(prova, disciplinas, nome_disc):
    questoes = prova.get("questoes", [])

    if not questoes:
        print("\n⚠️ Esta prova não possui questões cadastradas.")
        input("ENTER para voltar...")
        return

    while True:
        print("\n=== EDITAR QUESTÕES DA PROVA ===")
        for i, q in enumerate(questoes, start=1):
            pergunta_preview = q["pergunta"].split("\n")[0][:50]
            print(f"{i}. {pergunta_preview}...")

        print("\nAções:")
        print("1. Editar uma questão")
        print("2. Adicionar nova questão")
        print("3. Excluir uma questão")
        print("4. Voltar")

        op = input("Escolha: ").strip()

        if op == "1":
            try:
                idx = int(input("Número da questão: ").strip()) - 1
                if idx < 0 or idx >= len(questoes):
                    raise ValueError
            except:
                print("❌ Opção inválida.")
                continue

            q = questoes[idx]

            while True:
                print("\n=== EDITANDO QUESTÃO ===")
                print("1. Editar pergunta")
                print("2. Editar alternativas")
                print("3. Editar resposta correta")
                print("4. Voltar")

                escolha = input("Escolha: ").strip()

                if escolha == "1":
                    nova = input("Nova pergunta: ").strip()
                    if nova:
                        q["pergunta"] = textwrap.fill(nova, width=80)
                        print("✔ Pergunta atualizada!")

                elif escolha == "2":
                    print("\n=== EDITAR ALTERNATIVAS ===")
                    for i, alt in enumerate(q["alternativas"], start=1):
                        print(f"{i}. {alt}")

                    for i in range(4):
                        nova_alt_raw = input(f"Nova alternativa {i+1} (ENTER para manter): ").strip()
                        if nova_alt_raw != "":
                            q["alternativas"][i] = textwrap.fill(f"{i+1}) {nova_alt_raw}", width=80)

                    print("✔ Alternativas atualizadas!")

                elif escolha == "3":
                    try:
                        nova_correta = int(input("Nova alternativa correta (1-4): ").strip()) - 1
                        if nova_correta in [0,1,2,3]:
                            q["correta"] = nova_correta
                            print("✔ Resposta correta atualizada!")
                        else:
                            print("❌ Alternativa inválida.")
                    except:
                        print("❌ Entrada inválida.")

                elif escolha == "4":
                    break
                else:
                    print("Opção inválida.")

            prova["questoes"] = questoes
            disciplinas[nome_disc]["provas"] = disciplinas[nome_disc].get("provas", [])
            salvar_json(DISCIPLINAS_PATH, disciplinas)

        elif op == "2":
            print("\n=== ADICIONAR QUESTÃO ===")

            pergunta_raw = input("Pergunta: ").strip()
            pergunta = textwrap.fill(pergunta_raw, width=80)

            alternativas = []
            print("\nDigite as 4 alternativas:")
            for i in range(1, 5):
                alt_raw = input(f"Alternativa {i}: ").strip()
                alternativas.append(textwrap.fill(f"{i}) {alt_raw}", width=80))

            try:
                correta = int(input("Alternativa correta (1-4): ").strip()) - 1
                if correta not in [0,1,2,3]:
                    correta = 0
            except:
                correta = 0

            nova_questao = {
                "pergunta": pergunta,
                "alternativas": alternativas,
                "correta": correta
            }

            questoes.append(nova_questao)
            prova["questoes"] = questoes
            disciplinas[nome_disc]["provas"] = disciplinas[nome_disc].get("provas", [])
            salvar_json(DISCIPLINAS_PATH, disciplinas)

            print("✔ Questão adicionada!")

        elif op == "3":
            try:
                idx = int(input("Número da questão para excluir: ").strip()) - 1
                if idx < 0 or idx >= len(questoes):
                    raise ValueError
            except:
                print("❌ Número inválido.")
                continue

            removida = questoes.pop(idx)
            prova["questoes"] = questoes
            salvar_json(DISCIPLINAS_PATH, disciplinas)

            print("✔ Questão removida.")

        elif op == "4":
            break
        else:
            print("❌ Opção inválida.")

def excluir_prova_professor(professor):
    nome_disc = professor.get("disciplina")
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    disc = disciplinas.get(nome_disc)

    provas = disc.get("provas", [])
    if not provas:
        print("⚠️ Nenhuma prova cadastrada.")
        input("ENTER...")
        return

    print("\n=== EXCLUIR PROVA ===")
    for i, prova in enumerate(provas, 1):
        print(f"{i}. {prova['titulo']} (Peso {prova.get('peso', 0)})")

    try:
        esc = int(input("\nSelecione: ").strip()) - 1
        if esc < 0 or esc >= len(provas):
            raise ValueError
    except:
        print("Opção inválida.")
        return

    removida = provas.pop(esc)
    disciplinas[nome_disc] = disc
    salvar_json(DISCIPLINAS_PATH, disciplinas)

    print(f"✔ Prova '{removida['titulo']}' removida!")
    input("ENTER...")

# 16) Informações da Disciplina

def mostrar_informacoes_disciplina(nome_disciplina, disciplinas):
    disc = disciplinas.get(nome_disciplina)
    if not disc:
        print("Disciplina não encontrada.")
        return

    print("\n=== INFORMAÇÕES DA DISCIPLINA ===")
    print(f"📘 Nome: {nome_disciplina}")

    prof = disc.get("professor")
    if prof:
        print(f"👨‍🏫 Professor responsável: {prof.get('nome')} (RA: {prof.get('ra')})")
    else:
        print("👨‍🏫 Professor responsável: Nenhum")

    alunos = disc.get("alunos", [])
    print(f"👨‍🎓 Total de alunos cadastrados: {len(alunos)}")

    horario = disc.get("horario")
    if horario:
        print(f"🕒 Horário: {horario['dia']} — {horario['inicio']} às {horario['fim']}")
    else:
        print("🕒 Horário: Não definido")

    codigo = disc.get("codigo_acesso", "Nenhum")
    print(f"🔐 Código de acesso: {codigo}")

# 17) Painel do Aluno

def painel_aluno(aluno):
    while True:
        print("\n=== PAINEL DO ALUNO ===")
        print(f"Aluno: {aluno.get('nome')}  |  RA: {aluno.get('ra')}")
        print("1. Ver disciplinas disponíveis")
        print("2. Entrar em uma nova disciplina")
        print("3. Ver conteúdo da disciplina")
        print("4. Fazer provas")
        print("5. Ver minhas notas e média")
        print("6. Sair")

        op = input("Escolha: ").strip()

        if op == "1":
            listar_disciplinas_disponiveis()

        elif op == "2":
            trocar_disciplina_aluno(aluno)

        elif op == "3":
            mostrar_conteudo_para_aluno(aluno)

        elif op == "4":
            fazer_prova_aluno(aluno)

        elif op == "5":
            mostrar_notas_aluno(aluno)

        elif op == "6":
            print("\nSaindo do painel do aluno...")
            sleep(1)
            break

        else:
            print("❌ Opção inválida!")

def listar_disciplinas_disponiveis():
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    if not disciplinas:
        print("Nenhuma disciplina cadastrada.")
        return

    print("\n=== DISCIPLINAS DISPONÍVEIS ===")
    for nome, dados in disciplinas.items():
        prof = dados.get("professor")
        prof_nome = prof["nome"] if prof else "Sem professor"
        print(f"- {nome}  |  Professor: {prof_nome}")

def trocar_disciplina_aluno(aluno):
    nome_atual = aluno.get("disciplina")
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    dados_alunos = carregar_json(ALUNO_PATH)

    if "alunos" not in dados_alunos:
        print("❌ Banco de alunos corrompido.")
        return

    print("\n=== TROCAR DE DISCIPLINA ===")

    if nome_atual:
        print(f"📘 Disciplina atual: {nome_atual}")
    else:
        print("📘 O aluno ainda não está matriculado em nenhuma disciplina.")

    nomes_disc = list(disciplinas.keys())
    if not nomes_disc:
        print("❌ Não há disciplinas cadastradas.")
        return

    print("\nDisciplinas disponíveis:")
    for i, d in enumerate(nomes_disc, start=1):
        print(f"{i}. {d}")

    try:
        escolha = int(input("\nEscolha a nova disciplina: ").strip()) - 1
        if escolha < 0 or escolha >= len(nomes_disc):
            raise ValueError
        nova_disc = nomes_disc[escolha]
    except:
        print("❌ Opção inválida.")
        return

    if nova_disc == nome_atual:
        print("⚠️ Você já está matriculado nessa disciplina.")
        return

    if nome_atual:
        lista_atual = disciplinas[nome_atual].get("alunos", [])
        lista_atual = [a for a in lista_atual if a.get("ra") != aluno["ra"]]
        disciplinas[nome_atual]["alunos"] = lista_atual

    disciplinas[nova_disc].setdefault("alunos", [])
    disciplinas[nova_disc]["alunos"].append({
        "nome": aluno["nome"],
        "ra": aluno["ra"]
    })

    aluno["disciplina"] = nova_disc
    aluno["notas"] = []
    aluno["media"] = None  

    for idx, a in enumerate(dados_alunos["alunos"]):
        if a["ra"] == aluno["ra"]:
            dados_alunos["alunos"][idx] = aluno

    salvar_json(DISCIPLINAS_PATH, disciplinas)
    salvar_json(ALUNO_PATH, dados_alunos)

    print(f"\n✅ Disciplina alterada com sucesso!")
    print(f"📘 Nova disciplina: {nova_disc}")
    print("📝 Nota e média foram reiniciadas.")
    input("\nPressione ENTER para continuar...")

def mostrar_conteudo_para_aluno(aluno):
    disc_nome = aluno.get("disciplina")
    if not disc_nome:
        print("Você não está matriculado em nenhuma disciplina.")
        return

    disciplinas = carregar_json(DISCIPLINAS_PATH)
    disc = disciplinas.get(disc_nome)

    aulas = disc.get("aulas", [])

    if not aulas:
        print("Nenhum conteúdo cadastrado pelo professor ainda.")
        return

    total_topicos = len(aulas)

    print(f"\n=== CONTEÚDO DA DISCIPLINA: {disc_nome} ===")
    print("O conteúdo será exibido em tópicos interativos.\n")

    for i, bloco in enumerate(aulas, 1):

        print("\n" + "=" * 55)
        print(f"📘  TÓPICO {i} / {total_topicos}")
        print("=" * 55)

        print(bloco)

        print("\nPressione ENTER para avançar para o próximo tópico...")
        input()

        if i < total_topicos:
            print("\nCarregando próximo tópico", end="")
            for _ in range(3):
                time.sleep(0.4)
                print(".", end="")
            print("\n")

    print("\n📚 Fim do conteúdo! Você visualizou todos os tópicos.")

def trocar_disciplina_aluno(aluno):
    nome_atual = aluno.get("disciplina")
    disciplinas = carregar_json(DISCIPLINAS_PATH)
    dados_alunos = carregar_json(ALUNO_PATH)

    if "alunos" not in dados_alunos:
        print("❌ Banco de alunos corrompido.")
        return

    print("\n=== TROCAR DE DISCIPLINA ===")

    if nome_atual:
        print(f"📘 Disciplina atual: {nome_atual}")
    else:
        print("📘 O aluno ainda não está matriculado em nenhuma disciplina.")

    nomes_disc = list(disciplinas.keys())
    if not nomes_disc:
        print("❌ Não há disciplinas cadastradas.")
        return

    print("\nDisciplinas disponíveis:")
    for i, d in enumerate(nomes_disc, start=1):
        print(f"{i}. {d}")

    try:
        escolha = int(input("\nEscolha a nova disciplina: ").strip()) - 1
        if escolha < 0 or escolha >= len(nomes_disc):
            raise ValueError
        nova_disc = nomes_disc[escolha]
    except:
        print("❌ Opção inválida.")
        return

    if nova_disc == nome_atual:
        print("⚠️ Você já está matriculado nessa disciplina.")
        return

    if nome_atual:
        lista_atual = disciplinas[nome_atual].get("alunos", [])
        lista_atual = [a for a in lista_atual if a.get("ra") != aluno["ra"]]
        disciplinas[nome_atual]["alunos"] = lista_atual

    disciplinas[nova_disc].setdefault("alunos", [])
    disciplinas[nova_disc]["alunos"].append({
        "nome": aluno["nome"],
        "ra": aluno["ra"]
    })

    aluno["disciplina"] = nova_disc
    aluno["notas"] = []
    aluno["media"] = None 

    for idx, a in enumerate(dados_alunos["alunos"]):
        if a["ra"] == aluno["ra"]:
            dados_alunos["alunos"][idx] = aluno

    salvar_json(DISCIPLINAS_PATH, disciplinas)
    salvar_json(ALUNO_PATH, dados_alunos)

    print(f"\n✅ Disciplina alterada com sucesso!")
    print(f"📘 Nova disciplina: {nova_disc}")
    print("📝 Nota e média foram reiniciadas.")
    input("\nPressione ENTER para continuar...")

def fazer_prova_aluno(aluno):
    disc_nome = aluno.get("disciplina")
    if not disc_nome:
        print("Você não está em nenhuma disciplina.")
        return

    disciplinas = carregar_json(DISCIPLINAS_PATH)
    disciplina = disciplinas.get(disc_nome)

    provas = disciplina.get("provas", [])

    if not provas:
        print("Nenhuma prova disponível.")
        return

    print("\n=== REALIZAR PROVA ===")
    for i, prova in enumerate(provas, 1):
        titulo = prova.get("titulo", "Sem título")
        peso = prova.get("peso", 1)
        print(f"{i}. {titulo} (Peso {peso})")

    try:
        esc = int(input("Escolha a prova: ").strip()) - 1
    except ValueError:
        print("Entrada inválida.")
        return

    if esc < 0 or esc >= len(provas):
        print("Opção inválida.")
        return

    prova = provas[esc]

    pontuacao = 0
    total = len(prova["questoes"])

    for q in prova["questoes"]:
        print("\n" + q["pergunta"])
        for i, alt in enumerate(q["alternativas"], 1):
            print(f"{i}. {alt}")

        resp = input("Resposta: ").strip()

        try:
            indice_resp = int(resp) - 1
        except:
            indice_resp = -1

        if indice_resp == q["correta"]:
            pontuacao += 1

    nota = (pontuacao / total) * 10
    print(f"\n🎓 Sua nota nesta avaliação: {nota:.2f}")

    disciplina.setdefault("notas_pendentes", {})
    disciplina["notas_pendentes"][aluno["ra"]] = nota

    disciplinas[disc_nome] = disciplina
    salvar_json(DISCIPLINAS_PATH, disciplinas)

    input("\nPressione ENTER para continuar...")

def mostrar_notas_aluno(aluno):
    notas = aluno.get("notas", [])
    media = aluno.get("media", None)

    print("\n=== MINHAS NOTAS ===")

    if not notas:
        print("Nenhuma nota liberada pelo professor ainda.")
        return

    for item in notas:
        print(f"{item['prova']}: {item['nota']} (Peso {item['peso']})")

    if media is not None:
        print(f"\n📘 Média final: {media:.2f}")
    else:
        print("\nA média ainda não foi calculada pelo professor.")

# 18) Funções Auxiliares

def calcular_media_ponderada(provas):
    """
    Calcula média ponderada das provas.
    Parâmetro:
        provas -> lista de dicionários contendo 'nota' e 'peso'
    Retorna:
        média final (float) OU None se não houver notas
    """
    soma_ponderada = 0
    soma_pesos = 0

    for prova in provas:
        nota = prova.get("nota")
        peso = prova.get("peso", 0)

        if nota is None:
            continue

        try:
            nota = float(nota)
            peso = int(peso)
        except:
            continue  

        soma_ponderada += nota * peso
        soma_pesos += peso

    if soma_pesos == 0:
        return None  

    media = soma_ponderada / soma_pesos
    return round(media, 2)

def verificar_aprovacao(media):
    if media is None:
        return "Sem notas"
    return "Aprovado" if media >= 7 else "Reprovado"

def verificar_conflito_horario(dia, inicio, fim, disciplinas):

    def para_minutos(hora_str):
        h, m = map(int, hora_str.split(":"))
        return h * 60 + m

    inicio_novo = para_minutos(inicio)
    fim_novo = para_minutos(fim)

    for nome, disc in disciplinas.items():
        horario = disc.get("horario")

        if not horario:
            continue

        dia_existente = horario.get("dia")
        inicio_existente = horario.get("inicio")
        fim_existente = horario.get("fim")

        if not dia_existente:
            continue

        if dia_existente.lower() == dia.lower():

            ini_exist = para_minutos(inicio_existente)
            fim_exist = para_minutos(fim_existente)

            if inicio_novo < fim_exist and fim_novo > ini_exist:
                return True  

    return False  

# 19) Main

def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("=" * 50)
        print("🚀  SISTEMA CONEXAACADEMY — MENU PRINCIPAL")
        print("=" * 50)
        print("1. Login")                    
        print("2. Cadastro")                   
        print("3. Falar com o ConexaBot 🤖")
        print("4. Sair")
        print("-" * 50)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            menu_login()                       

        elif opcao == "2":
            cadastro_usuario()                

        elif opcao == "3":
            conexa_bot()

        elif opcao == "4":
            print("\nSaindo do sistema... Até logo!\n")
            break

        else:
            print("\n❌ Opção inválida. Tente novamente.")
            input("Pressione ENTER para continuar...")

if __name__ == "__main__":
    main()