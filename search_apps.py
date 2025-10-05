import subprocess

def search_apps(app_name: str):
    final_list = {}
    ps_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    command = f"Get-Command -CommandType Application | Where-Object {{$_.Name -like '{app_name}*.exe'}}"

    apps_list = subprocess.run(f"{ps_path} -Command {command} -ErrorAction SilentlyContinue", capture_output=True, text=True, check=True, encoding='utf-8')
    apps_list = apps_list.stdout.strip().split("\n")
    apps_list = apps_list[2:]

    new_apps_list = []
    for app in apps_list:
        new_apps_list.append(app)

    return new_apps_list

if __name__ == '__main__':
    print(search_apps("python"))