import winreg as reg
from nepyc.client.scripts.send_to_nePyc import SCRIPT_PATH


def add_to_registry():
    key = reg.HKEY_CLASSES_ROOT
    path = r'SystemFileAssociations\image\shell\Send to nePyc Server\command'

    try:
        reg.CreateKey(key, path)
        reg_key = reg.OpenKey(key, path, 0, reg.KEY_WRITE)

        reg.SetValue(reg_key, '', reg.REG_SZ, f'python "{SCRIPT_PATH}" "%1"')

        reg.CloseKey(reg_key)

        print('Registry key for nePyc added successfully')

    except WindowsError as e:
        print(f'Error: {e}. Failed to add registry key.')
