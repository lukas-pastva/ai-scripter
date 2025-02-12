AI-Scripter
===========

**AI-Scripter** is a Python utility that generates comprehensive state files for your projects by scanning the **current working directory**. It creates a detailed report including an ASCII tree of your project folder and the contents of all non-hidden files, facilitating documentation and upgrades.

Features
--------

*   **Comprehensive Scanning:** Scans the current directory and its subdirectories.
*   **ASCII Tree Generation:** Provides a visual representation of your directory structure.
*   **Content Aggregation:** Compiles contents of all non-hidden files into a single state file.
*   **Automated Naming:** Generates state files with timestamps for easy tracking.
*   **PowerShell Integration:** Easily callable from any location in PowerShell on Windows.

Prerequisites
-------------

*   **Python 3.x** installed on your system.
*   **PowerShell** (for Windows users) to execute the script from any directory.

Installation
------------

1.  **Download the Script:** Save `ai.py` to a directory, e.g., `C:\Scripts`.
    
2.  **Add to PATH:**
    
    *   Open **System Properties** > **Advanced** > **Environment Variables**.
    *   Edit the `Path` variable and add `C:\Scripts`.
    *   Click **OK** to apply.
3.  **Associate `.py` Files with Python:**
    
    *   Open PowerShell as Administrator.
    *   Run:
         
      ```cmd
      assoc .py=Python.File
      ftype Python.File="C:\Path\To\Python\python.exe" "%1" %*
      ```
        
      ```powershell
      Set-ItemProperty -Path "HKLM:\Software\Classes\.py" -Name "(Default)" -Value "Python.File"
      Set-ItemProperty -Path "HKLM:\Software\Classes\Python.File\shell\open\command" -Name "(Default)" -Value '"C:\Path\To\Python.exe" "%1" %*'
      ```



        Replace `C:\Path\To\Python\python.exe` with your Python installation path.

Usage
-----

1.  **Navigate to Your Project Directory:** Ensure you are in the directory you want to scan.
    
      ```powershell
      cd C:\Path\To\Your\Project
      ```

2.  **Run AI-Scripter:**
    
      ```powershell
      ai.py
      ```

    This creates an `ai` directory with a `state-YYYY-MM-DD-HH-MM-SS.txt` file containing the ASCII tree and file contents.
    

Example
-------

Given the following structure:

```plaintext
C:\Projects\MyProject
│
├── main.py
├── utils.py
├── .hidden_file.py
│
├── README.md
└── ai.py  (located in C:\Scripts)
```

Running `ai.py` inside `C:\Projects\MyProject` will generate:

```makerfile
C:\Projects\MyProject\ai\state-2024-12-08-15-30-45.txt
```

Containing the ASCII tree of the current directory and the contents of `main.py` and `utils.py`.

Contact
-------

For questions or feedback, reach out to:

*   **Email:** info@lukaspastva.sk
*   **GitHub:** [lukas\-pastva](https://github.com/lukas-pastva)

* * *

Thank you for using **AI-Scripter**! We hope it enhances your project documentation and development workflow.