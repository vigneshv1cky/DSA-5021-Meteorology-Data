# Connect and Disconnect from Remote Server in VS Code

### **1. Install the Remote - SSH Extension**
- Open **VS Code**.
- Go to the **Extensions** view (`Cmd + Shift + X` on Mac).
- Search for **Remote - SSH** and click **Install**.

---

### **2. Connect to a Remote Server**

1. Open the **Command Palette** (`Cmd + Shift + P`).
2. Type `Remote-SSH: Connect to Host...` and select it.
3. Click **+ Add New SSH Host**.
4. Enter the SSH command:  
   ```bash
   ssh user@remote-server-ip
   ```
   Example:  
   ```bash
   ssh ubuntu@192.168.1.100
   ```
5. Choose the **SSH configuration file** (`~/.ssh/config`).
6. After adding the host, select it from the list.
7. VS Code will open a new window and connect to the remote server. You will now see the remote file system in the **Explorer**.

---

### **3. Open and Edit Files**
- Use the **Explorer** to browse remote files.
- Open `index.html` (or any file) directly to start editing.

---

### **4. Disconnect from the Remote Server**

1. Open the **Command Palette** (`Cmd + Shift + P`).
2. Type `Remote-SSH: Close Remote Connection` and select it.
3. The connection will be closed, and you'll return to your local VS Code window.

---

### **(Optional) Set Up SSH Key for Passwordless Login**
If you don’t want to enter your password every time:
1. Generate an SSH key pair:
   ```bash
   ssh-keygen -t rsa -b 4096
   ```
2. Copy the public key to the remote server:
   ```bash
   ssh-copy-id user@remote-server-ip
   ```
3. Now you can connect without entering a password.

---

### **Summary Commands**
- **Connect to Remote Server**:  
  `Remote-SSH: Connect to Host...`
- **Disconnect from Remote Server**:  
  `Remote-SSH: Close Remote Connection`