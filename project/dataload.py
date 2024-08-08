import os
import sys
from datetime import datetime
from rich import print
from rich.table import Table
import argparse
import pandas as pd
import multiprocessing
import psutil
import platform

def read_files(file_path):
    print(f"Leyendo archivo: {file_path}")
    start_time = datetime.now()
    try:
        data = pd.read_csv(file_path, encoding='latin1')
    except pd.errors.EmptyDataError:
        print(f"[bold red]Error:[/bold red] El archivo {file_path} está vacío o no tiene columnas.")
        data = None
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        return data, start_time, end_time, duration
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    return data, start_time, end_time, duration


def read_files_sequentially(file_paths):
    print(f"\nLeyendo los archivos en [bold cyan] sequentially [/bold cyan] mode")
    start_time_program = datetime.now()

    data_list = []
    durations = []
    start_times = []
    end_times = []
    
    for file_path in file_paths:
        data, start_time, end_time, duration = read_files(file_path)
        if data is not None:
            data_list.append(data)
            start_times.append(start_time)
            end_times.append(end_time)
            durations.append(duration)
        else: 
            print(f"[bold red]Error:[/bold red] El archivo {file_path} no pudo ser leído.")
        
    end_time_program = datetime.now()
    
    print_end("sequentially", start_time_program, end_time_program, file_paths, start_times, end_times, durations)
    save_to_csv("sequentially", start_time_program, end_time_program, file_paths, start_times, end_times, durations)
        

def check_cpu_affinity():
    p = psutil.Process(os.getpid())
    affinity = p.cpu_affinity()
    print(f"El proceso está asignado a los núcleos: {affinity}")

def read_files_in_same_core(file_paths):
    print(f"\nLeyendo los archivos en [bold cyan] same core [/bold cyan] mode")
    start_time_program = datetime.now()
    # Asignar el proceso a un solo core
    p = psutil.Process(os.getpid())
    p.cpu_affinity([0])
    check_cpu_affinity()

    data_list = []
    durations = []
    start_times = []
    end_times = []

    with multiprocessing.Pool() as pool:
        # Set the affinity of the worker processes to a single core
        worker_pool = pool._pool
        for worker in worker_pool:
            psutil.Process(worker.pid).cpu_affinity([0])
        
        results = pool.map(read_files, file_paths)

    for i, (data, start_time, end_time, duration) in enumerate(results):
        if data is not None:
            data_list.append(data)
        start_times.append(start_time)
        end_times.append(end_time)
        durations.append(duration)

    end_time_program = datetime.now()
    
    print_end("same core", start_time_program, end_time_program, file_paths, start_times, end_times, durations)
    save_to_csv("same_core", start_time_program, end_time_program, file_paths, start_times, end_times, durations)

def read_files_in_multi_core(file_paths):
    print(f"\nLeyendo los archivos en [bold cyan] multi core [/bold cyan] mode")
    start_time_program = datetime.now()
    p = psutil.Process(os.getpid())
    p.cpu_affinity(list(range(psutil.cpu_count()))) # Asignar el proceso a todos los cores
    check_cpu_affinity()

    data_list = []
    durations = []
    start_times = []
    end_times = []

    with multiprocessing.Pool() as pool:
        results = pool.map(read_files, file_paths)

    for i, (data, start_time, end_time, duration) in enumerate(results):
        if data is not None:
            data_list.append(data)
        start_times.append(start_time)
        end_times.append(end_time)
        durations.append(duration)

    end_time_program = datetime.now()

    print_end("multi core", start_time_program, end_time_program, file_paths, start_times, end_times, durations)
    save_to_csv("multi_core", start_time_program, end_time_program, file_paths, start_times, end_times, durations)


def mostrar_informacion_sistema():
    print(f"[bold cyan]Tipo de procesador:[/bold cyan] {platform.processor()}")
    print(f"[bold cyan]Cantidad de memoria RAM:[/bold cyan] {psutil.virtual_memory().total / (1024 ** 3):.2f} GB")
    print(f"[bold cyan]Sistema operativo:[/bold cyan] {platform.system()} {platform.release()}")
    print(f"[bold cyan]Numero de CPUs:[/bold cyan] {multiprocessing.cpu_count()}")


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
            start_times[i].strftime("%H:%M:%S.%f"),
            end_times[i].strftime("%H:%M:%S.%f"),
            f"{durations[i]:.6f}"
        )

    start_time_str = start_times[0].strftime("%H:%M:%S.%f")
    end_time_str = end_times[-1].strftime("%H:%M:%S.%f")
    duration_total = (end_time_program - start_time_program).total_seconds()
    duration_total_str = f"{duration_total:.6f}"

    
    print(f"\n[bold cyan]Modo:[/bold cyan] {mode}")
    print(f"[bold magenta]Hora de inicio del programa:[/bold magenta] {start_time_program.strftime('%H:%M:%S.%f')}")
    print(f"[bold magenta]Hora de inicio de la carga del primer archivo:[/bold magenta] {start_time_str}")
    print(f"[bold magenta]Hora de finalización de la carga del último archivo:[/bold magenta] {end_time_str}")
    print(f"[bold magenta]Hora de finalización del programa:[/bold magenta] {end_time_program.strftime('%H:%M:%S.%f')}")
    print(table)
    print(f"[bold green]Tiempo total del proceso:[/bold green] {duration_total_str} segundos")

def save_to_csv(mode, start_time_program, end_time_program, file_paths, start_times, end_times, durations):
    # Preparar datos para el archivo CSV
    data = {
        "Archivo": [os.path.basename(fp) for fp in file_paths],
        "Hora de inicio": [st.strftime("%H:%M:%S.%f") for st in start_times],
        "Hora de finalización": [et.strftime("%H:%M:%S.%f") for et in end_times],
        "Duración (s)": [f"{duration:.6f}" for duration in durations]
    }
    df = pd.DataFrame(data)
    
    # Agregar información adicional
    df["Modo"] = mode
    df["Hora de inicio del programa"] = start_time_program.strftime("%H:%M:%S.%f")
    df["Hora de inicio de la carga del primer archivo"] = start_times[0].strftime("%H:%M:%S.%f")
    df["Hora de finalización de la carga del último archivo"] = end_times[-1].strftime("%H:%M:%S.%f")
    df["Hora de finalización del programa"] = end_time_program.strftime("%H:%M:%S.%f")
    df["Tiempo total del proceso (s)"] = f"{(end_time_program - start_time_program).total_seconds():.6f}"

    # Guardar el DataFrame en un archivo CSV
    output_file = f"{mode}_summary_{end_time_program.strftime('%H%M%S')}.csv"
    df.to_csv(output_file, index=False)
    print(f"\n[bold green]Resumen guardado en:[/bold green] {output_file}\n")
    

    
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

    file_paths = [os.path.join(args.folder, file) for file in os.listdir(args.folder) if file.endswith('.csv')]
    
    if not file_paths:
        print("[bold red] Error: [/bold red] No se encontraron archivos csv en la carpeta especifica.")
        sys.exit(1)

    if args.same_core:
        read_files_in_same_core(file_paths)
    elif args.multi_core:
        read_files_in_multi_core(file_paths)
    else:
        read_files_sequentially(file_paths)
        

if __name__ == "__main__":
    main()
