# Python-FTP-Client
An Intuitive FTP CLient written in Python

## Features
* Login/Logout capabilities
* Upload, Download, Create and remove files and folders with commands close to UNIX
* Intuitive file navigation with command line alike commands like "cd", "cd..", "ls", "pwd"
* Possibility for using diferent port

## How It Works
The client can connect to any FTP server and authenticate with username and password combination. After authenticated the user can send simple and well-known commands to create and remove files and folders, upload and download.

## Dependencies
Note: Code written in Python 3.9

* pathlib (from Path)
```
pip install Path
```

Note: All the other libraries are installed by default with a normal Python installation

### Libraries Used

* sys
* os
* ftplib
* pathlib
* time
* socket

## Usage

### Run the Program

```
python jftp-client.py 'server_ip' 'server_port' (default: 21)
```

### User/Password Authentication

```
connect 'user_name' 'password'
```
#### Authentication Example
![alt text](https://github.com/j3z-repos/Python-FTP-Client/blob/main/Commands.png)
