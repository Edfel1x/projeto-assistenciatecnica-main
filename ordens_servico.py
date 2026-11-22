
import equipamentos
import tecnicos

ordens_de_servico = []



def cadastrar_ordem_de_servico(defeito_relatado):

    defeito_relatado = defeito_relatado.strip()

    if not defeito_relatado:
        return "\nO campo defeito relatado não pode estar vazio."

    id_ordem = len(ordens_de_servico) + 1

    ordem = {
        "id": id_ordem,
        "defeito_relatado": defeito_relatado,
        "id_equipamento": None,
        "id_tecnico": None,
        "diagnostico": "",
        "servico_realizado": "",
        "status": "Aberta",
        "valor_servico": 0.0,
        "data_conclusao": None
    }

    ordens_de_servico.append(ordem)

    return f"\nOrdem de serviço ID {id_ordem} cadastrada com sucesso!"



def listar_ordens():

    print("\n----Lista de Ordens de Serviço----")

    if not ordens_de_servico:
        print("Nenhuma ordem de serviço cadastrada.")
        return

    for ordem in ordens_de_servico:
        print(f"\nID: {ordem['id']}")
        print(f"Defeito relatado: {ordem['defeito_relatado']}")
        print(f"Status: {ordem['status']}")
        print(f"ID do equipamento: {ordem['id_equipamento']}")
        print(f"ID do técnico: {ordem['id_tecnico']}")



def buscar_ordem():

    print("\n----Buscar Orden de Serviço----")

    try:
        id_ordem = int(input("Digite o ID da ordem: "))
    except ValueError:
        print("Digite um ID válido.")
        return

    for ordem in ordens_de_servico:

        if ordem["id"] == id_ordem:

            print(f"\nID: {ordem['id']}")
            print(f"Defeito: {ordem['defeito_relatado']}")
            print(f"Diagnóstico: {ordem['diagnostico']}")
            print(f"Status: {ordem['status']}")
            print(f"Equipamento: {ordem['id_equipamento']}")
            print(f"Técnico: {ordem['id_tecnico']}")
            print(f"Valor: R$ {ordem['valor_servico']:.2f}")

            return

    print("\nOrdem de serviço não encontrada.")



def atualizar_diagnostico(id_ordem, diagnostico):

    diagnostico = diagnostico.strip()

    if not diagnostico:
        print("O diagnóstico não pode estar vazio.")
        return

    for ordem in ordens_de_servico:

        if ordem["id"] == id_ordem:

            if ordem["status"] in ("Concluída", "Cancelada"):
                print("Não é possível alterar uma ordem encerrada.")
                return

            ordem["diagnostico"] = diagnostico

            print("Diagnóstico atualizado com sucesso!")
            return

    print("Ordem de serviço não encontrada.")

def atribuir_tecnico(id_ordem, id_tecnico):

    for ordem in ordens_de_servico:

        if ordem["id"] == id_ordem:

            if ordem["status"] in ("Concluída", "Cancelada"):
                print("Não é possível atribuir técnico a uma ordem encerrada.")
                return

            

            ordem["id_tecnico"] = id_tecnico

            print("Técnico atribuído com sucesso!")
            return

    print("Ordem de serviço não encontrada.")


def atualizar_status(id_ordem, novo_status):

    status_permitidos = [
        "Aberta",
        "Em manutenção",
        "Concluída",
        "Cancelada"
    ]

    novo_status = novo_status.strip()

    for status in status_permitidos:
        if novo_status.casefold() == status.casefold():
            novo_status = status
            break

    if novo_status not in status_permitidos:
        print("Status inválido.")
        return

    for ordem in ordens_de_servico:

        if ordem["id"] == id_ordem:

            if ordem["status"] in ("Concluída", "Cancelada"):
                print("Esta ordem já foi encerrada.")
                return

            if novo_status == "Concluída":
                print("Utilize a função finalizar_ordem() para concluir.")
                return

            if novo_status == "Cancelada":
                print("Utilize a função cancelar_ordem() para cancelar.")
                return

            ordem["status"] = novo_status

            print("Status atualizado com sucesso!")
            return

    print("Ordem de serviço não encontrada.")



def finalizar_ordem(id_ordem, valor_servico):

    try:
        valor_servico = float(valor_servico.replace(",", "."))
    except (ValueError, AttributeError):
        print("Digite um valor válido.")
        return

    if valor_servico < 0:
        print("O valor não pode ser negativo.")
        return

    for ordem in ordens_de_servico:

        if ordem["id"] == id_ordem:

            if ordem["status"] in ("Concluída", "Cancelada"):
                print("Esta ordem já foi encerrada.")
                return

            if not ordem["id_tecnico"]:
                print("Atribua um técnico antes de finalizar.")
                return

            if not ordem["diagnostico"]:
                print("Registre um diagnóstico antes de finalizar.")
                return

            ordem["valor_servico"] = valor_servico
            ordem["status"] = "Concluída"

            from datetime import datetime
            ordem["data_conclusao"] = datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )

            print("Ordem de serviço finalizada com sucesso!")
            return

    print("Ordem de serviço não encontrada.")



def cancelar_ordem(id_ordem):

    for ordem in ordens_de_servico:

        if ordem["id"] == id_ordem:

            if ordem["status"] == "Concluída":
                print("Não é possível cancelar uma ordem concluída.")
                return

            if ordem["status"] == "Cancelada":
                print("Esta ordem já foi cancelada.")
                return

            ordem["status"] = "Cancelada"

            print("Ordem de serviço cancelada com sucesso!")
            return

    print("Ordem de serviço não encontrada.")



def gerenciar_ordem():

    while True:

        print("\n===== GERENCIAMENTO DE ORDENS DE SERVIÇO =====")
        print("1 - Atualizar diagnóstico")
        print("2 - Atribuir técnico")
        print("3 - Atualizar status")
        print("4 - Finalizar ordem de serviço")
        print("5 - Cancelar ordem de serviço")
        print("0 - Voltar ao menu anterior")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":

            try:
                id_ordem = int(input("ID da ordem: "))
            except ValueError:
                print("ID inválido.")
                continue

            diagnostico = input("Novo diagnóstico: ")

            atualizar_diagnostico(id_ordem, diagnostico)

        elif opcao == "2":

            try:
                id_ordem = int(input("ID da ordem: "))
                id_tecnico = int(input("ID do técnico: "))
            except ValueError:
                print("Digite IDs válidos.")
                continue

            atribuir_tecnico(id_ordem, id_tecnico)

        elif opcao == "3":

            try:
                id_ordem = int(input("ID da ordem: "))
            except ValueError:
                print("ID inválido.")
                continue

            novo_status = input("Novo status: ")

            atualizar_status(id_ordem, novo_status)

        elif opcao == "4":

            try:
                id_ordem = int(input("ID da ordem: "))
            except ValueError:
                print("ID inválido.")
                continue

            valor_servico = input("Valor do serviço: ")

            finalizar_ordem(id_ordem, valor_servico)

        elif opcao == "5":

            try:
                id_ordem = int(input("ID da ordem: "))
            except ValueError:
                print("ID inválido.")
                continue

            confirmar = input(
                "Tem certeza que deseja cancelar esta OS? (s/n): "
            ).strip().lower()

            if confirmar == "s":
                cancelar_ordem(id_ordem)
            else:
                print("Cancelamento não realizado.")

        elif opcao == "0":
            print("Voltando ao menu anterior...")
            break

        else:
            print("Opção inválida! Tente novamente.")



def menu_ordens_de_servico():

    while True:

        print("\n===== ORDENS DE SERVIÇO =====")
        print("1 - Cadastrar ordem de serviço")
        print("2 - Listar ordens de serviço")
        print("3 - Buscar ordem de serviço")
        print("4 - Gerenciar ordens de serviço")
        print("0 - Voltar ao menu principal")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":

            defeito = input("Defeito relatado: ")

            print(cadastrar_ordem_de_servico(defeito))

        elif opcao == "2":
            listar_ordens()

        elif opcao == "3":
            buscar_ordem()

        elif opcao == "4":
            gerenciar_ordem()

        elif opcao == "0":
            print("Voltando ao menu principal...")
            break

        else:
            print("Opção inválida! Tente novamente.")
