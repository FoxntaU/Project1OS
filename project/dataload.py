import os
import sys
import time
from rich import print
from rich.table import Table
import pandas as pd
import multiprocessing
import psutil
import platform
from concurrent.futures import ProcessPoolExecutor

# Define the default folder path here
DEFAULT_FOLDER_PATH = r"C:\Users\david\Desktop\Project1OS-main\Project1OS-main\datasets"
# Set the number of cores you want to use
NUM_CORES = 11  # Change this value to use a different number of cores
# Select the mode of execution: "sequential", "same_core", "multi_core"
MODE = "multi_core"  # Change this to "sequential", "same_core", or "multi_core"


def read_files(file_path):
    print(f"Leyendo archivo: {file_path}")
    start_time = time.time()
    try:
        data = pd.read_csv(file_path, encoding='latin1')
    except pd.errors.EmptyDataError:
        print(
            f"[bold red]Error:[/bold red] El archivo {file_path} está vacío o no tiene columnas.")
        data = None
        duration = 0
        return data, duration

    end_time = time.time()
    duration = end_time - start_time
    return data, duration


def read_files_sequentially(file_paths):
    print(
        f"\nLeyendo los archivos en [bold cyan] sequentially [/bold cyan] mode")
    start_time_program = time.time()

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

    print_end("sequentially", start_time_program, end_time_program,
              file_paths, start_times, end_times, durations)


def check_cpu_affinity():
    p = psutil.Process(os.getpid())
    affinity = p.cpu_affinity()
    print(f"El proceso está asignado a los núcleos: {affinity}")


def read_files_in_same_core(file_paths):
    print(f"\nLeyendo los archivos en [bold cyan] same core [/bold cyan] mode")
    start_time_program = time.time()
    p = psutil.Process(os.getpid())
    # Asignar el proceso a un solo core
    p.cpu_affinity([0])
    check_cpu_affinity()

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

    print_end("same core", start_time_program, end_time_program,
              file_paths, start_times, end_times, durations)


def read_files_in_multi_core(file_paths, num_cores):
    available_cores = multiprocessing.cpu_count()
    if num_cores > available_cores:
        print(
            f"[bold red]Error:[/bold red] El número de cores especificado ({num_cores}) es mayor que el número de cores disponibles ({available_cores}).")
        sys.exit(1)

    print(
        f"\nLeyendo los archivos en [bold cyan] multi core [/bold cyan] mode con {num_cores} cores")
    start_time_program = time.time()

    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        results = list(executor.map(read_files, file_paths))

    data_list = []
    durations = []
    start_times = []
    end_times = []

    for i, (data, duration) in enumerate(results):
        if data is not None:
            data_list.append(data)
        durations.append(duration)
        start_times.append(start_time_program if i == 0 else end_times[-1])
        end_times.append(time.time())

    end_time_program = time.time()

    print_end("multi core", start_time_program, end_time_program,
              file_paths, start_times, end_times, durations)


def mostrar_informacion_sistema():
    print(f"[bold cyan]Tipo de procesador:[/bold cyan] {platform.processor()}")
    print(
        f"[bold cyan]Cantidad de memoria RAM:[/bold cyan] {psutil.virtual_memory().total / (1024 ** 3):.2f} GB")
    print(
        f"[bold cyan]Sistema operativo:[/bold cyan] {platform.system()} {platform.release()}")
    print(
        f"[bold cyan]Numero de CPUs:[/bold cyan] {multiprocessing.cpu_count()}")


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

    start_time_str = time.strftime(
        "%H:%M:%S", time.localtime(start_time_program))
    end_time_str = time.strftime("%H:%M:%S", time.localtime(end_time_program))
    duration_total = end_time_program - start_time_program
    duration_total_str = time.strftime("%M:%S", time.gmtime(duration_total))

    print(table)
    print(f"\n[bold cyan]Modo:[/bold cyan] {mode}")
    print(
        f"[bold magenta]Hora de inicio del programa:[/bold magenta] {start_time_str}")
    print(
        f"[bold magenta]Hora de finalización del programa:[/bold magenta] {end_time_str}")
    print(
        f"[bold green]Tiempo total del proceso:[/bold green] {duration_total_str}")


def main():
    folder = DEFAULT_FOLDER_PATH

    if not os.path.isdir(folder):
        print("[bold red]Error:[/bold red] La carpeta especificada no existe.")
        sys.exit(1)

    file_paths = [os.path.join(folder, file)
                  for file in os.listdir(folder) if file.endswith('.csv')]

    if not file_paths:
        print(
            "[bold red] Error: [/bold red] No se encontraron archivos csv en la carpeta especifica.")
        sys.exit(1)

    if MODE == "same_core":
        read_files_in_same_core(file_paths)
    elif MODE == "multi_core":
        read_files_in_multi_core(file_paths, NUM_CORES)
    else:
        read_files_sequentially(file_paths)


if __name__ == "__main__":
    main()

# Ejecutar el script simplemente ejecutando python dataload.py

