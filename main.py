import clientes
import equipamentos
import tecnicos

def menu_principal():
    while True:
        print("\n===== Sistema de Assistência Técnica =====")
        print("1. Clientes")
        print("2. Equipamentos")
        print("3. Técnicos")
        print("4. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            clientes.menu_clientes()
        elif opcao == "2":
            equipamentos.menu_equipamentos()
        elif opcao == "3":
            tecnicos.menu_tecnicos()
        elif opcao == "4":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    try:
        menu_principal()
    except (EOFError, KeyboardInterrupt):
        print("\nSaindo do sistema...")
