import clientes
import equipamentos
import tecnicos
import ordens_servico

def menu_principal():
    while True:
        print("\n===== Sistema de Assistência Técnica =====")
        print("1. Clientes")
        print("2. Equipamentos")
        print("3. Técnicos")
        print("4. Ordens de Serviço")
        print("5. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            clientes.menu_clientes()
        elif opcao == "2":
            equipamentos.menu_equipamentos()
        elif opcao == "3":
            tecnicos.menu_tecnicos()
        elif opcao == "4":
            ordens_servico.menu_ordens_de_servico()
        elif opcao == "5":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    try:
        menu_principal()
    except (EOFError, KeyboardInterrupt):
        print("\nSaindo do sistema...")
