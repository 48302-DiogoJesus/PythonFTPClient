import sys
from ftplib import FTP
import os
import mimetypes
from pathlib import Path
import time
import socket

SERVER_IP = ""
SERVER_PORT = 21
ftp = FTP()
valid_commands = {"?", "check", "connect", "ls", "pwd", "cd", "cd..", "mkdir", "mkfile", "rmdir",
                  "rmfile", "rmfiles", "upload", "download", "exit", "disconnect"}
connected_only_commands = {"ls", "pwd", "cd", "cd..", "mkdir", "mkfile", "rmdir", "rmfile", "rmfiles", "upload", "download", "disconnect"}
connected = False
last_dir = []


def client_init():
    global connected
    print(f"\n- SERVER : {SERVER_IP}:{SERVER_PORT} -")
    print(f"\n- To see the available commands type \"?\" -")
    while True:
        func = None
        args = []
        if not connected:
            command = input("\nCommand >> ").split(' ')
        else:
            command = input(f"\n{CommandHandling.pwd_str()} >> ").split(' ')

        if command[0] not in valid_commands:
            print("\n[!] Invalid command.\nType '?' to see all the commands available")
            continue

        if command[0] == "connect" and connected:
            print("\n[!] You are already connected !\nTo connect with a different "
                  "user use the command \"disconnect\" and the connect again with new credentials")
            continue

        if command[0] in connected_only_commands and not connected:
            print("\n[!] You need to connect to the server first. Use the command \" connect 'user' 'pass' \"")
            continue

        if command[0] == "upload":
            if len(command) == 1:
                print(
                    "\n[!] Syntax Error\n[!] Command Syntax Example: download \"C:/file.txt\"\nRelative/Absolute path supported")
                continue
            file = fetch_in_quotation(command)
            if not os.path.exists(file):
                print(f"\n[!] {file.name} doesn't exist in this computer")
                continue
            func = CommandHandling.cmd_upload
            args.append(file)
        elif command[0] == "download":
            if len(command) == 1:
                print("\n[!] Syntax Error\n[!] Command Syntax Example: download \"file.txt\"")
                continue
            if command[1] == "":
                continue
            file = fetch_in_quotation(command)
            func = CommandHandling.cmd_download
            args.append(file)
        elif command[0] == "connect":
            if len(command) != 3:
                username = input("\n[?] Username: ")
                password = input("[?] Password: ")
            else:
                username = command[1]
                password = command[2]
            func = CommandHandling.cmd_connect
            args.append((username, password))
        elif command[0] == "rmfile":
            if len(command) == 1:
                print("\n[!] Syntax Error\nCommand Syntax Example: rmfile \"folder1/file.txt\"")
                continue
            if command[1] == "":
                continue
            file = fetch_in_quotation(command)
            func = CommandHandling.cmd_remove_file
            args.append(file)
        elif command[0] == "rmfiles":
            if len(command) == 1:
                print("\n[!] Syntax Error\nCommand Syntax Example: rmfiles \"folder1/anotherfolder\"")
                continue
            dir_name = fetch_in_quotation(command)
            func = CommandHandling.cmd_remove_files
            args.append(dir_name)
        elif command[0] == "rmdir":
            if len(command) == 1:
                print(f"\n[!] Syntax Error\nCommand Syntax Example: rmdir folder1/folder2")
                continue
            if command[1] == "":
                continue
            dir_name = fetch_in_quotation(command)
            func = CommandHandling.cmd_remove_dir
            args.append(dir_name)
        elif command[0] == "mkdir":
            if len(command) == 1:
                print(f"\n[!] Syntax Error\nCommand Syntax Example: mkdir folder1/folder2")
                continue
            if command[1] == "":
                continue
            dir_name = fetch_in_quotation(command)
            func = CommandHandling.cmd_make_dir
            args.append(dir_name)
        elif command[0] == "pwd":
            print(f"\nCurrent Server Directory: {CommandHandling.pwd_str()()}")
            continue
        elif command[0] == "mkfile":
            if len(command) == 1:
                print(f"\n[!] Syntax Error\nCommand Syntax Example: mkfile folder1/filename.txt")
                continue
            if command[1] == "":
                continue
            func = CommandHandling.cmd_make_file
            file_name = fetch_in_quotation(command)
            args.append(file_name)
        elif command[0] == "cd":
            if len(command) == 1:
                continue
            dir_name = fetch_in_quotation(command)
            func = CommandHandling.cmd_cd
            args.append(dir_name)
            args.append(False)
        elif command[0] == "cd..":
            func = CommandHandling.cmd_cd
            args.append(CommandHandling.pwd_str()(True))
            args.append(True)
        elif command[0] == "ls":
            func = CommandHandling.cmd_ls
        elif command[0] == "?":
            func = CommandHandling.cmd_help
        elif command[0] == "exit":
            func = CommandHandling.cmd_exit
        elif command[0] == "check":
            args.append(True)
            func = CommandHandling.cmd_check
        elif command[0] == "disconnect":
            connected = False
            ftp.close()
            print(f"\n[-] You have disconnected from \"{SERVER_IP}\" ...")
            continue

        func([args])


def fetch_in_quotation(command):
    if len(command) > 2:
        build_str = ""
        for string in command[1:len(command)]:
            build_str = build_str + " " + string
        return build_str[1:].replace("\"", "'")
    elif len(command) == 2:
        return command[1]


class CommandHandling:
    @staticmethod
    def cmd_help(*args):
        print("\n|----------------- HELP -----------------|\n")
        if connected:
            print(" - ?                              => Displays this menu\n"
                  " - pwd                            => Check current server directory\n"
                  " - ls                             => List files in current server directory\n"
                  " - cd 'directory_name'            => Change current server directory\n"
                  " - cd..                           => Go one folder backwards in server\n"
                  " - mkdir 'new_directory_name'     => Create new directory in current server directory\n"
                  " - rmdir 'directory_name'         => Remove a directory in current server directory\n"   
                  " - mkfile 'file_name'             => Create new file in current server directory\n"
                  " - rmfile 'server_file_name'      => Remove a file in current server directory\n"
                  " - rmfiles 'server_folder'        => Remove all files from a server directory\n"
                  " - upload 'local file name'       => Upload a file to the server\n"
                  " - download 'server_file_name'    => Download a file from your server folder\n"
                  " - disconnect                     => Closes FTP connection with the server\n"
                  " - exit                           => Close the program")
        else:
            print(" - ?                              => Displays this menu\n"
                  " - connect 'user' 'pass'          => Establish a connecting to the server\n"
                  " - check                          => Checks whether the server is online\n"
                  " - exit                           => Close the program")

    @staticmethod
    def pwd_str(back=False):
        pwd = ""
        if len(last_dir) == 0:
            pwd = "/"
            return pwd
        for p in range(len(last_dir)):
            if back and p == len(last_dir) - 1:
                break
            if p < 1:
                pwd = pwd + "/" + last_dir[p]
            else:
                pwd = pwd + "/" + last_dir[p]
        return pwd

    @staticmethod
    def cmd_check(*args):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((SERVER_IP, SERVER_PORT))
            sock.close()
            if args[0]:
                print(f"\n[!] {SERVER_IP}:{SERVER_PORT} is ONLINE")
                return True
        except:
            print(f"\n[!] Could not connect to {SERVER_IP}:{SERVER_PORT}")
            return False

    @staticmethod
    def cmd_exit(*args):
        print("\n[!] Closing client now...")
        sys.exit(0)

    @staticmethod
    def cmd_remove_dir(*args):
        global last_dir
        dir_name = args[0][0][0]
        confirm = input(f"\n[?] Delete \"{dir_name}\" from server? (y/n): ")
        if confirm == "y":
            try:
                ftp.rmd(dir_name)
                print(f"\n[+] \"{dir_name}\" was deleted")
            except:
                print(f"\n[!] Couldn't delete \"{dir_name}\".\n"
                      f"Make sure the folder has no files in it.\n"
                      f"If it has use the command \"rmfiles 'folder name'\" first")
                return
        else:
            print(f"\n[!] \"{dir_name}\" won't be deleted")

    @staticmethod
    def get_sub_dirs(dir_name):
        global connected
        sub_dirs = []
        CommandHandling.cmd_cd(dir_name)
        data = []

        try:
            ftp.dir(data.append)
        except Exception as e:
            if "421" in str(e):
                print(f"\n[!] Connection Timed Out. Please connect again")
                connected = False
            else:
                print(f"\n[!] {e}")

        for file_dir in data:
            file_dir = file_dir.split(None, 8)
            if "d" in file_dir[0]:
                # It's a directory
                sub_dirs.append(file_dir[8])
        return sub_dirs

    @staticmethod
    def cmd_remove_files(dir_name):
        global last_dir, connected
        dir_name = dir_name[0][0]
        confirm = input(f"\n[?] Remove all files inside \"{dir_name}\"? (y/n): ")
        if confirm != "y":
            print(f"[!] \"{dir_name}\" files won't be deleted")
            return
        try:
            ftp.cwd(dir_name)
        except Exception as e:
            if "421" in str(e):
                print(f"\n[!] Connection Timed Out. Please connect again")
                connected = False
            else:
                print(f"\n[!] {e}")

        files = []
        ftp.dir(files.append)
        for file in files:
            try:
                if "d" not in file.split(None, 8)[0]:
                    ftp.delete(str(file.split(None, 8)[8]))
            except:
                # Its a folder
                continue

        ftp.cwd(CommandHandling.pwd_str()())

    @staticmethod
    def cmd_make_dir(*args):
        dir_name = args[0][0][0]
        confirm = input(f"\n[?] Create \"{dir_name}\"? (y/n): ")
        if confirm == "y":
            try:
                ftp.mkd(dir_name)
                print(f"\n[+] \"{dir_name}\" was created")
            except:
                print(f"\n[!] \"{dir_name}\" couldn't be created")
                return
        else:
            print(f"\n[!] \"{dir_name}\" won't be created")

    @staticmethod
    def cmd_remove_file(file):
        file = Path(file[0][0])
        confirm = input(f"\n[?] Delete \"{file.name}\"? (y/n): ")
        if confirm == "y":
            try:
                ftp.delete(str(file))
            except:
                print(f"\n[!] Couldn't delete \"{file.name}\"")
                return
            print(f"\n[+] \"{file.name}\" was deleted from the server")
        else:
            print(f"\n[!] \"{file.name}\" won't be deleted")

    @staticmethod
    def cmd_cd(*args):
        global last_dir
        if len(args) == 1:
            dir_name = args[0][0][0]
            back = args[0][0][1]
        else:
            dir_name = Path(args[0]).name
            back = args[1]
        try:
            if back:
                if len(last_dir) == 0:
                    pass
                elif len(last_dir) == 1:
                    dir_name = "/"
                    last_dir.remove(last_dir[len(last_dir) - 1])
                else:
                    last_dir.remove(last_dir[len(last_dir)-1])
                ftp.cwd(dir_name)
            else:
                splitted = dir_name.split('/')
                for directory in splitted:
                    last_dir.append(directory)
                ftp.cwd(dir_name)

        except:
            print(f"\n[!] \"{dir_name}\" doesn't exist in this directory")
            last_dir.remove(last_dir[len(last_dir)-1])

    @staticmethod
    def cmd_download(file):
        file = Path(file[0][0])
        mime = mimetypes.guess_type(file)
        cmd = fr'RETR {file}'

        start_time = time.time()
        try:
            print(f"\n[!] Downloading \"{file.name}\"...\nDepending on the file size this process may take a while.")
            if "text" in mime:
                with open(file.name, "w") as local_file:
                    ftp.retrlines(cmd, local_file.write)
            else:
                with open(file.name, "wb") as local_file:
                    ftp.retrbinary(cmd, local_file.write)
        except:
            print(f"\n[!] Couldn't download \"{file.name}\"")
            os.remove(file)
            return

        time_took = float(str(time.time() - start_time)[0:7])
        file_size = os.path.getsize(file.name)
        if time_took > 0.1:
            print(f"\n- {file.name} was sent in {time_took}s")
            print(
                f"\n- Transfer Speed: {CommandHandling.calc_transfer_speed_mbs(file_size, time_took)} MB/s")

        print(f"\n[+] Downloaded \"{file.name}\" to the current local folder")

    @staticmethod
    def cmd_upload(file, init_call=True):
        if init_call:
            file_to_send = Path(file[0][0])
        else:
            file_to_send = Path(file)
        mime = mimetypes.guess_type(file_to_send)

        cmd = fr'STOR {file_to_send}'
        start_time = time.time()
        print(f"\n[!] Uploading \"{file_to_send.name}\"...\nDepending on the file size this process may take a while.")
        if mime[0] is not None and "text" in mime[0]:
            with(open(file_to_send, "rb")) as text_file:
                try:
                    ftp.storlines(cmd, text_file)
                except:
                    print(f"\n[!] Couldn't upload \"{file_to_send.name}\"")
                    return
        else:
            with(open(file_to_send, "rb")) as binary_file:
                try:
                    ftp.storbinary(cmd, binary_file)
                except:
                    print(f"\n[!] Couldn't upload \"{file_to_send.name}\"")
                    return

        time_took = float(str(time.time() - start_time)[0:7])
        file_size = os.path.getsize(file_to_send)

        if time_took > 0.1:
            print(f"\n- {file_to_send.name} was sent in {time_took}s")
            print(
                f"\n- Transfer Speed was {CommandHandling.calc_transfer_speed_mbs(file_size, time_took)} MB/s")

        print(f"\n[+] \"{file_to_send}\" sent")

    @staticmethod
    def calc_transfer_speed_mbs(file_size, time_took):
        return str(float(str(file_size * pow(10, -6))[0:7]) / float(str(time_took)[0:7]))[0:6]

    @staticmethod
    def cmd_ls(*args):
        global connected
        data = []
        try:
            ftp.dir(data.append)
        except Exception as e:
            if "421" in str(e):
                print(f"\n[!] Connection Timed Out. Please connect again")
                connected = False
            else:
                print(f"\n[!] {e}")
        if len(data) == 0:
            if CommandHandling.pwd_str() == "/":
                print(f"\n- The server is empty")
            else:
                print(f"\n- This folder is empty")
            return
        print("\n[*] -- Server Files -- [*]\n")
        for line in data:
            line = line.split(None, 8)
            if "d" in line[0]:
                f_type = "Directory  :  "
            else:
                f_type = "File       :  "

            new_line = "| Last modification: " + line[6] + "/" + line[5] + " at " + line[7] + " | " + f_type + "\"" + line[8] + "\""
            print(new_line)

    @staticmethod
    def cmd_make_file(*args):
        file_name = args[0][0][0]
        if os.path.exists(file_name):
            file_name = "TEMP." + file_name
        open(file_name, "x")
        file = open(file_name, "a")
        print(f"\n[*] Writing to \"{file_name}\" [*]\n\nWrite line by line\nType \"save\" and press ENTER "
              f"in a new line to stop writing to the file and save it to the server\n")
        while True:
            line = input("[+] New Line: ")
            if line == "save":
                break
            file.write(line + "\n")
        file.close()
        CommandHandling.cmd_upload(file_name.replace("TEMP.", ""), False)
        os.remove(file_name)

    @staticmethod
    def cmd_connect(*args):
        global connected
        if CommandHandling.cmd_check(False) is False:
            return
        try:
            ftp.timeout = 2
            ftp.connect(SERVER_IP, SERVER_PORT)
            ftp.login(args[0][0][0][0], args[0][0][0][1])
        except:
            print(f"\n[!] Wrong credentials")
            return
        print(f"\n[+] Connected to {SERVER_IP}:{SERVER_PORT}")
        connected = True


if __name__ == '__main__':
    print("\n[+] ----- Welcome to JFTP Client ----- [+]")
    if len(sys.argv) < 2:
        print("\n[!] You need to set the Server IP in order no connect")
        print("\n[!] Ex: python jftp-client.py \"server ip\"")
        sys.exit(0)
    elif len(sys.argv) == 2:
        SERVER_IP = sys.argv[1]
        print(f"\n[!] You didn't specify the server port. {SERVER_PORT} (Default) will be used")
    else:
        SERVER_IP = sys.argv[1]
        SERVER_PORT = int(sys.argv[2])

    client_init()
