tecnicos = []


def cadastro_tecnico(nome, telefone, especialidade):
    nome = nome.strip()
    if not nome:
        print("O nome não pode ser vazio.")
        return
    try:
        telefone = telefone.strip()
    except (AttributeError, TypeError):
        print("Telefone inválido: informe um número de telefone.")
        return
    if not telefone:
        print("O telefone não pode ser vazio.")
        return
    especialidade = especialidade.strip()
    if not especialidade:
        print("A especialidade não pode ser vazia.")
        return

    id_tecnico = len(tecnicos) + 1
    tecnico = {
        "nome": nome,
        "telefone": telefone,
        "especialidade": especialidade,
    }

    tecnico["id"] = id_tecnico
    tecnicos.append(tecnico)
    return f"Técnico {nome} cadastrado com sucesso!"

def listar_tecnicos():
    print("\n----Lista de Técnicos----")
    if not tecnicos:
        print("Nenhum técnico cadastrado.")
    else:
        for i, tecnico in enumerate(tecnicos, start=1):
            print(f"{i}. ID: {tecnico['id']}, Nome: {tecnico['nome']}, Especialidade: {tecnico['especialidade']}, Telefone: {tecnico['telefone']}")

def buscar_tecnico_por_id(id_tecnico):
    for tecnico in tecnicos:
        if tecnico["id"] == id_tecnico:
            return tecnico
    return None

def solicitar_cadastro_tecnico():
    while True:
        nome = input("Digite o nome do técnico: ").strip()
        if not nome:
            print("O nome não pode ser vazio. Tente novamente.")
            continue
        if not nome.replace(" ", "").isalpha():
            print("O nome deve conter somente letras. Tente novamente.")
            continue
        break

    while True:
        try:
            telefone = input("Digite o telefone do técnico: ").strip()
            if not telefone:
                print("O telefone não pode ser vazio. Tente novamente.")
                continue
            if not telefone.isascii() or not telefone.isdigit():
                raise ValueError("O telefone deve conter somente números.")
        except ValueError:
            print("O telefone deve conter somente números. Tente novamente.")
            continue
        break

    while True:
        especialidade = input("Digite a especialidade do técnico: ").strip()
        if not especialidade:
            print("A especialidade não pode ser vazia. Tente novamente.")
            continue
        break

    return nome, telefone, especialidade

def menu_tecnicos():
    while True:
        print("\n----Menu de Técnicos----")
        print("1. Cadastrar Técnico")
        print("2. Listar Técnicos")
        print("3. Voltar")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            nome, telefone, especialidade = solicitar_cadastro_tecnico()
            resultado = cadastro_tecnico(nome, telefone, especialidade)
            if resultado:
                print(resultado)
        elif opcao == "2":
            listar_tecnicos()
        elif opcao == "3":
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    print("----Cadastro de Técnicos----")
    try:
        menu_tecnicos()
    except (EOFError, KeyboardInterrupt):
        print("\nSaindo do cadastro de técnicos...")
