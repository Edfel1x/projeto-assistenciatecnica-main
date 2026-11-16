import clientes

equipamentos = []

def cadastro_equipamento(tipo, marca, modelo, numero_serie, id_cliente=None):
    tipo = tipo.strip()
    if not tipo:
        print("O tipo do equipamento não pode ser vazio.")
        return
    marca = marca.strip()
    if not marca:
        print("A marca do equipamento não pode ser vazia.")
        return
    modelo = modelo.strip()
    if not modelo:
        print("O modelo do equipamento não pode ser vazio.")
        return
    numero_serie = numero_serie.strip()
    if not numero_serie:
        print("O número de série do equipamento não pode ser vazio.")
        return

    if id_cliente is not None and clientes.buscar_cliente_por_id(id_cliente) is None:
        print(f"Cliente ID {id_cliente} não encontrado.")
        return

    id_equipamento = len(equipamentos) + 1
    equipamento = {
        "tipo": tipo,
        "marca": marca,
        "modelo": modelo,
        "numero_serie": numero_serie,
        "id_cliente": id_cliente,
    }

    equipamento["id"] = id_equipamento
    equipamentos.append(equipamento)
    return f"Equipamento {tipo} {marca} {modelo} cadastrado com sucesso!"

def listar_equipamentos():
    print("\n----Lista de Equipamentos----")
    if not equipamentos:
        print("Nenhum equipamento cadastrado.")
    else:
        for i, equipamento in enumerate(equipamentos, start=1):
            dono = equipamento.get("id_cliente")
            if dono is None:
                nome_dono = "sem cliente"
            else:
                cliente = clientes.buscar_cliente_por_id(dono)
                nome_dono = cliente["nome"] if cliente else "cliente removido"
            print(f"{i}. ID: {equipamento['id']}, Tipo: {equipamento['tipo']}, Marca: {equipamento['marca']}, Modelo: {equipamento['modelo']}, Número de Série: {equipamento['numero_serie']}, Cliente: {nome_dono}")

def buscar_equipamento_por_id(id_equipamento):
    for equipamento in equipamentos:
        if equipamento["id"] == id_equipamento:
            return equipamento
    return None

def listar_equipamentos_por_cliente(id_cliente):
    cliente = clientes.buscar_cliente_por_id(id_cliente)
    if cliente is None:
        print(f"Cliente ID {id_cliente} não encontrado.")
        return
    print(f"\n----Lista de Equipamentos do Cliente {cliente['nome']}----")
    equipamentos_cliente = [equipamento for equipamento in equipamentos if equipamento.get("id_cliente") == id_cliente]
    if not equipamentos_cliente:
        print("Nenhum equipamento cadastrado para este cliente.")
    else:
        for i, equipamento in enumerate(equipamentos_cliente, start=1):
            print(f"{i}. ID: {equipamento['id']}, Tipo: {equipamento['tipo']}, Marca: {equipamento['marca']}, Modelo: {equipamento['modelo']}, Número de Série: {equipamento['numero_serie']}")

def atualizar_equipamento(id_equipamento, tipo=None, marca=None, modelo=None, numero_serie=None, id_cliente=None):
    equipamento = buscar_equipamento_por_id(id_equipamento)
    if not equipamento:
        return f"Equipamento ID {id_equipamento} não encontrado."
    if id_cliente is not None and clientes.buscar_cliente_por_id(id_cliente) is None:
        return f"Cliente ID {id_cliente} não encontrado."
    if tipo is not None:
        equipamento["tipo"] = tipo
    if marca is not None:
        equipamento["marca"] = marca
    if modelo is not None:
        equipamento["modelo"] = modelo
    if numero_serie is not None:
        equipamento["numero_serie"] = numero_serie
    if id_cliente is not None:
        equipamento["id_cliente"] = id_cliente
    return f"Equipamento ID {id_equipamento} atualizado com sucesso!"

def solicitar_cadastro_equipamento():
    while True:
        tipo = input("Digite o tipo do equipamento: ").strip()
        if not tipo:
            print("O tipo do equipamento não pode ser vazio. Tente novamente.")
            continue
        break

    while True:
        marca = input("Digite a marca do equipamento: ").strip()
        if not marca:
            print("A marca do equipamento não pode ser vazia. Tente novamente.")
            continue
        break

    while True:
        modelo = input("Digite o modelo do equipamento: ").strip()
        if not modelo:
            print("O modelo do equipamento não pode ser vazio. Tente novamente.")
            continue
        break

    while True:
        numero_serie = input("Digite o número de série do equipamento: ").strip()
        if not numero_serie:
            print("O número de série do equipamento não pode ser vazio. Tente novamente.")
            continue
        break

    while True:
        entrada = input("Digite o ID do cliente (deixe em branco para nenhum): ").strip()
        if not entrada:
            id_cliente = None
            break
        if not entrada.isdigit():
            print("O ID deve conter somente números. Tente novamente.")
            continue
        id_cliente = int(entrada)
        if clientes.buscar_cliente_por_id(id_cliente) is None:
            print(f"Cliente ID {id_cliente} não encontrado. Tente novamente.")
            continue
        break

    return tipo, marca, modelo, numero_serie, id_cliente

def solicitar_atualizacao_equipamento():
    while True:
        entrada = input("Digite o ID do equipamento que deseja atualizar: ").strip()
        if not entrada.isdigit():
            print("O ID deve conter somente números. Tente novamente.")
            continue
        id_equipamento = int(entrada)
        equipamento = buscar_equipamento_por_id(id_equipamento)
        if equipamento is None:
            print(f"Equipamento ID {id_equipamento} não encontrado. Tente novamente.")
            continue
        break

    print("Deixe em branco para manter o valor atual.")
    tipo = input(f"Tipo [{equipamento['tipo']}]: ").strip() or None
    marca = input(f"Marca [{equipamento['marca']}]: ").strip() or None
    modelo = input(f"Modelo [{equipamento['modelo']}]: ").strip() or None
    numero_serie = input(f"Número de série [{equipamento['numero_serie']}]: ").strip() or None

    while True:
        entrada = input("ID do cliente (deixe em branco para manter): ").strip()
        if not entrada:
            id_cliente = None
            break
        if not entrada.isdigit():
            print("O ID deve conter somente números. Tente novamente.")
            continue
        id_cliente = int(entrada)
        if clientes.buscar_cliente_por_id(id_cliente) is None:
            print(f"Cliente ID {id_cliente} não encontrado. Tente novamente.")
            continue
        break

    return id_equipamento, tipo, marca, modelo, numero_serie, id_cliente

def menu_equipamentos():
    while True:
        print("\n----Menu de Equipamentos----")
        print("1. Cadastrar Equipamento")
        print("2. Listar Equipamentos")
        print("3. Listar Equipamentos por Cliente")
        print("4. Atualizar Equipamento")
        print("5. Voltar")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            tipo, marca, modelo, numero_serie, id_cliente = solicitar_cadastro_equipamento()
            resultado = cadastro_equipamento(tipo, marca, modelo, numero_serie, id_cliente)
            if resultado:
                print(resultado)
        elif opcao == "2":
            listar_equipamentos()
        elif opcao == "3":
            entrada = input("Digite o ID do cliente: ").strip()
            if entrada.isdigit():
                listar_equipamentos_por_cliente(int(entrada))
            else:
                print("O ID deve conter somente números.")
        elif opcao == "4":
            id_equipamento, tipo, marca, modelo, numero_serie, id_cliente = solicitar_atualizacao_equipamento()
            print(atualizar_equipamento(id_equipamento, tipo, marca, modelo, numero_serie, id_cliente))
        elif opcao == "5":
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    print("----Cadastro de Equipamentos----")
    try:
        menu_equipamentos()
    except (EOFError, KeyboardInterrupt):
        print("\nSaindo do cadastro de equipamentos...")
