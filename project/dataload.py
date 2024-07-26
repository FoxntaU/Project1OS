import os
import sys
import time
from rich import print
from rich.table import Table
import argparse
import pandas as pd
import multiprocessing
import psutil
import platform


def read_files(file_path):
    print(f"Reading file: {file_path}")
    start_time = time.time()
    try:
        data = pd.read_csv(file_path, encoding='latin1')
    except pd.errors.EmptyDataError:
        print(f"[bold red]Error:[/bold red] El archivo {file_path} está vacío o no tiene columnas.")
        data = None
        duration = 0
        return data, duration 
    
    end_time = time.time()
    duration = end_time - start_time
    return data, duration


def read_files_sequentially(folder):
    print(f"\nLeyendo los archivos en [bold cyan] sequentially [/bold cyan] mode")
    start_time_program = time.time()
    
    file_paths = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith('.csv')]
    
    if not file_paths:
        print("[bold red] Error: [/bold red] No se encontraron arcchivos csv en la carpeta especifica.")
        sys.exit(1)
    
    data_list = []
    durations = []
    start_times = []
    end_times = []
    
    for i, file_path in enumerate(file_paths):
        if i == 0:
            start_time_first_file = time.time()
            start_times.append(start_time_first_file)
        else:
            start_times.append(end_times[-1])
    
        data, duration = read_files(file_path)
        if data is not None:
            data_list.append(data)
        durations.append(duration)
        end_times.append(time.time())
        
    end_time_program = time.time()
    
    print_end("sequentially", start_time_program, end_time_program, file_paths, start_times, end_times, durations)
        
    
def read_files_in_same_core(folder):
    
    print(f"\nLeyendo los archivos en [bold cyan] same core [/bold cyan] mode")

def read_files_in_multi_core(folder):

    print(f"\nLeyendo los archivos en [bold cyan] multi core [/bold cyan] mode")


def mostrar_informacion_sistema():
    print(f"[bold cyan]Tipo de procesador:[/bold cyan] {platform.processor()}")
    print(f"[bold cyan]Cantidad de memoria RAM:[/bold cyan] {psutil.virtual_memory().total / (1024 ** 3):.2f} GB")
    print(f"[bold cyan]Sistema operativo:[/bold cyan] {platform.system()} {platform.release()}")
 


def print_end(mode, start_time_program, end_time_program, file_paths, start_times, end_times, durations):
    print("\n")
    print("[bold]Información del sistema[/bold]")
    mostrar_informacion_sistema()
    table = Table(title="Resumen de carga de archivos")
    table.add_column("Archivo", justify="left", style="cyan", no_wrap=True)
    table.add_column("Hora de inicio", style="magenta")
    table.add_column("Hora de finalización", style="magenta")
    table.add_column("Duración (s)", style="green")

    for i, file_path in enumerate(file_paths):
        table.add_row(
            os.path.basename(file_path),
            time.strftime("%H:%M:%S", time.localtime(start_times[i])),
            time.strftime("%H:%M:%S", time.localtime(end_times[i])),
            f"{durations[i]:.2f}"
        )

    start_time_str = time.strftime("%H:%M:%S", time.localtime(start_time_program))
    end_time_str = time.strftime("%H:%M:%S", time.localtime(end_time_program))
    duration_total = end_time_program - start_time_program
    duration_total_str = time.strftime("%M:%S", time.gmtime(duration_total))

    print(table)
    print(f"\n[bold cyan]Modo:[/bold cyan] {mode}")
    print(f"[bold magenta]Hora de inicio del programa:[/bold magenta] {start_time_str}")
    print(f"[bold magenta]Hora de finalización del programa:[/bold magenta] {end_time_str}")
    print(f"[bold green]Tiempo total del proceso:[/bold green] {duration_total_str}")

    
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
        read_files_in_same_core(args.folder)
    elif args.multi_core:
        read_files_in_multi_core(args.folder)
    else:
        read_files_sequentially(args.folder)
        

if __name__ == "__main__":
    main()


# Ejecutar el script
# python dataload.py [OPCIONES -s, -m or nothing] -f "C:\Users\nicolas\Desktop\Sistemas Operativos\Project1OS\datasets"