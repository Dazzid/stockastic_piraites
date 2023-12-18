import psutil
import subprocess

def get_running_processes():
    # Get a list of all running processes
    running_processes = psutil.process_iter(['pid', 'name'])

    # Extract PID and name information
    pid_name_info = [(process.info['pid'], process.info['name']) for process in running_processes]

    return pid_name_info

def stop_process(pid):
    try:
        # Use the subprocess module to run the kill command
        subprocess.run(['kill', str(pid)])
        print(f"Process with PID {pid} terminated successfully.")
    except subprocess.CalledProcessError:
        print(f"Error: Unable to terminate process with PID {pid}.")