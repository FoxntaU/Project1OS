import os
import sys
from rich import print
from rich.table import Table
import argparse


def read_files_in_parallel(folder, mode):
    
    print(f"Leyendo los archivos en [bold cyan]{mode}[/bold cyan] mode")

    def same_core():
        pass

    def multi_core():
        pass


def read_files_sequentially(folder):
    print(f"Leyendo los archivos en [bold cyan] sequentially [/bold cyan] mode")


def main():
    parser = argparse.ArgumentParser(description="dataload - Lector de datos.")
    parser.add_argument("-f", "--folder", required=True, help="Carpeta con archivos CSV")
    parser.add_argument("-s", "--same-core", action="store_true", help="Leer archivos en paralelo en el mismo core")
    parser.add_argument("-m", "--multi-core", action="store_true", help="Leer archivos en paralelo en múltiples cores")
    args = parser.parse_args()
    
    if not os.path.isdir(args.folder):
        print("[bold red]Error:[/bold red] La carpeta especificada no existe.")
        sys.exit(1)

    if args.same_core and args.multi_core:
        print("[bold red]Error:[/bold red]  No se pueden usar las opciones -s y -m al mismo tiempo.")
        sys.exit(1)

    if args.same_core:
        read_files_in_parallel(args.folder, mode='same_core')
    elif args.multi_core:
        read_files_in_parallel(args.folder, mode='multi_core')
    else:
        read_files_sequentially(args.folder)

if __name__ == "__main__":
    main()