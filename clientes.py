clientes = []

def cadastro_cliente(nome, telefone, email):
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
    email = email.strip()

    id_cliente = len(clientes) + 1
    cliente = {
        "nome": nome,
        "telefone": telefone,
        "e-mail": email,
    }

    cliente["id"] = id_cliente
    clientes.append(cliente)
    return f"Cliente {nome} cadastrado com sucesso!"

def listar_clientes():
    print("\n----Lista de Clientes----")
    if not clientes:
        print("Nenhum cliente cadastrado.")
    else:
        for i, cliente in enumerate(clientes, start=1):
            print(f"{i}. ID: {cliente['id']}, Nome: {cliente['nome']}, Email: {cliente['e-mail']}, Telefone: {cliente['telefone']}")

def buscar_cliente_por_id(id_cliente):
    for cliente in clientes:
        if cliente["id"] == id_cliente:
            return cliente
    return None

def solicitar_cadastro_cliente():
    while True:
        nome = input("Digite o nome do cliente: ").strip()
        if not nome:
            print("O nome não pode ser vazio. Tente novamente.")
            continue
        if not nome.replace(" ", "").isalpha():
            print("O nome deve conter somente letras. Tente novamente.")
            continue
        break

    while True:
        try:
            telefone = input("Digite o telefone do cliente: ").strip()
            if not telefone:
                print("O telefone não pode ser vazio. Tente novamente.")
                continue
            if not telefone.isascii() or not telefone.isdigit():
                raise ValueError("O telefone deve conter somente números.")
        except ValueError:
            print("O telefone deve conter somente números. Tente novamente.")
            continue
        break

    email = input("Digite o email do cliente: ").strip()

    return nome, telefone, email

def menu_clientes():
    while True:
        print("\n----Menu de Clientes----")
        print("1. Cadastrar Cliente")
        print("2. Listar Clientes")
        print("3. Voltar")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            nome, telefone, email = solicitar_cadastro_cliente()
            resultado = cadastro_cliente(nome, telefone, email)
            if resultado:
                print(resultado)
        elif opcao == "2":
            listar_clientes()
        elif opcao == "3":
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    print("----Cadastro de Clientes----")
    try:
        menu_clientes()
    except (EOFError, KeyboardInterrupt):
        print("\nSaindo do cadastro de clientes...")
