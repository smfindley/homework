import sys
import socket
import psutil
import threading
import datetime
import pathlib

# GLOBALS
g_app_path = pathlib.Path(__file__).resolve().parent
g_app_name = pathlib.Path(__file__).name
g_log_name = str(pathlib.Path(__file__).stem) + ".log"
g_log_info = False

def main(): 
    # Parses command line args
    # Assumes the first arg is the script name passed from python engine, second arg is user-specified
    if len(sys.argv) > 1:
        cl_arg = sys.argv[1] 
              
        if cl_arg.lower() == "-loginfo":
            # Set disk logging flag
            global g_log_info 
            g_log_info = True

            print_header()
            log(f"Logging console output to: {g_app_path}\\{g_log_name}") 
            print_sys_info()
        elif cl_arg.lower() == "-help":
            print_help()     
        else:
            log(f"Invalid argument: {cl_arg}")
            print_help()
            
    else:
        print_header()
        print_sys_info()

def print_help(): 
    # Prints Help/ReadMe
    log(f"Usage: {g_app_name} <arg>")
    log("Arguments:")
    log(f"\t -logInfo\t Logs console output to file ({g_app_path}\\{g_log_name})")
    log("\t -help\t\t Displays this help message")

def print_header(): 
    # Pretty Header
    log(f"{g_app_name} - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")

def print_sys_info():
    # Pretty prints desired system information based on requirements
    
    #Computer Name
    log(f"Computer Name: {socket.getfqdn()}")

    #Total Physical Memory
    total_physical_mb = f"{psutil.virtual_memory().total / (1024 ** 3):.2f}"
    log(f"Total Physical Memory: {total_physical_mb} Gb")

    #Total Number of Physical Processors
    log(f"Total Number of Physical Processors: {psutil.cpu_count(logical=False)}")

    #Total Number of Cores
    log(f"Total Number of Cores: {psutil.cpu_count(logical=True)}")

    #Total Number of Hard Disks
    disk_list = psutil.disk_partitions(all=False);
    log(f"Total Number of Hard Disks: {len(disk_list)}")
    
    #Top 5 CPU Processes - multithreaded
    log("Top 5 Processes by % CPU Utilization (5 second sample interval):")
    process_list = list()
    measure_cpu_percent_threadpool(psutil.process_iter(), process_list)
    process_list.sort(reverse=True) #sort desc

    for proc in process_list[:5]: #pop top 5
        log(f"\t{proc[1]}: {proc[0]}%")
    
    log(f"\tTOTAL PROCESSES: {len(process_list)}")

def measure_cpu_percent_threadpool(process_generator, process_list): 
    # Spins as many threads as there are queried system processes
    # Waits for them to complete
    worker_threads = []
    for proc in process_generator:
        thread = threading.Thread(target=measure_cpu_percent_worker, args=(proc, process_list))
        worker_threads.append(thread)
        thread.start()
    
    for thread in worker_threads:
        thread.join()

def measure_cpu_percent_worker( proc, process_list): 
    # Worker thread function that is probably not thread safe for a python list tuple
    # Samples CPU at 5 second interval, per psutil docs
    try:
        proc.cpu_percent(interval=5)
        process_list.append((proc.cpu_percent(interval=None), proc.name()))
    except Exception as e:
        pass #do nothing
    
def log(log_message): 
    # Writes to Console and Log File (optionally)
    print(log_message) 

    if g_log_info == True:
        with open(f"{g_app_path}\\{g_log_name}", "+a") as logfile:
            logfile.write(f"{log_message}\n")

if __name__ == "__main__": #ENTRY POINT
    main()