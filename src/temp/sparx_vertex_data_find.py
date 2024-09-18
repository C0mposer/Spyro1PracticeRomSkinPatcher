import ctypes
import ctypes.wintypes
import os
import sys
import psutil
import requests
from termcolor import colored
import subprocess
import shutil

import convert_bmp

def ConvertFlameColorData(tip_color, base_color, left_color, right_color):
    flame_bytes = b""
    
    flame_bytes += int(tip_color[0]).to_bytes(1, 'big')
    flame_bytes += int(tip_color[1]).to_bytes(1, 'big')
    flame_bytes += int(tip_color[2]).to_bytes(1, 'big')
    flame_bytes += int(0x30).to_bytes(1, 'big')
    
    flame_bytes += int(base_color[0]).to_bytes(1, 'big')
    flame_bytes += int(base_color[1]).to_bytes(1, 'big')
    flame_bytes += int(base_color[2]).to_bytes(1, 'big')
    flame_bytes += int(0x30).to_bytes(1)
    
    flame_bytes += int(left_color[0]).to_bytes(1, 'big')
    flame_bytes += int(left_color[1]).to_bytes(1, 'big')
    flame_bytes += int(left_color[2]).to_bytes(1, 'big')
    flame_bytes += int(0x30).to_bytes(1, 'big')
    
    flame_bytes += int(right_color[0]).to_bytes(1, 'big')
    flame_bytes += int(right_color[1]).to_bytes(1, 'big')
    flame_bytes += int(right_color[2]).to_bytes(1, 'big')
    flame_bytes += int(0x30).to_bytes(1, 'big')
    
    #print("Flame Bytes: ")
    #print(' '.join(f'{byte:02x}' for byte in flame_bytes))
    return flame_bytes


def ConvertSparxGlowColorData(glow_color):
    glow_bytes = b""
    
    glow_bytes += int(glow_color[0]).to_bytes(1, 'big')
    glow_bytes += int(glow_color[1]).to_bytes(1, 'big')
    glow_bytes += int(glow_color[2]).to_bytes(1, 'big')
    glow_bytes += int(0x30).to_bytes(1, 'big')

    return glow_bytes
    

# Define constants
PROCESS_ALL_ACCESS = 0x1F0FFF
PAGE_EXECUTE_READWRITE = 0x40
PROCESS_VM_OPERATION = 0x8
PROCESS_VM_READ = 0x10
PROCESS_VM_WRITE = 0x20

# Define some data types
DWORD = ctypes.c_uint
HANDLE = ctypes.wintypes.HANDLE
HMODULE = ctypes.wintypes.HMODULE
LPSTR = ctypes.c_char_p
MAX_PATH = 260  # Maximum path length

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
psapi = ctypes.WinDLL('psapi', use_last_error=True)

url = "http://127.0.0.1:8080"
api_url = url + "/api/v1/cpu/ram/raw"


# Function to get process ID by a string. It doesn't have to be full, it can just be the start
def get_pid(process_name):
    process_name_lower = process_name.lower()
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        #print(proc.info['name'])
        if proc.info['name'].lower().startswith(process_name_lower):
            return proc.info['pid']
    print(colored("Could not find PID for proccess starting with " + process_name, "red"))
    return None

def GetBaseAddressFromEXE(process_handle, process_name):
    base_address = None
    
    # Define an array to hold module handles
    module_handles = (HMODULE * 1024)()
    cb_needed = DWORD()

    if psapi.EnumProcessModules(process_handle, module_handles, ctypes.sizeof(module_handles), ctypes.byref(cb_needed)):
        for i in range(cb_needed.value // ctypes.sizeof(HMODULE)):
            module_name = (ctypes.c_char * MAX_PATH)()
            if psapi.GetModuleBaseNameA(process_handle, ctypes.c_ulonglong(module_handles[i]), module_name, MAX_PATH) > 0:
                module_name_str = module_name.value.decode('utf-8')
                if module_name_str.lower() == process_name.lower():
                    base_address = module_handles[i]
                    print(colored(f"Base address of {process_name}: {base_address:X}", "blue"))
                    break
    
    return base_address

def read_process_memory(handle, address, size):
    buffer = (ctypes.c_char * size)()
    bytes_read = ctypes.c_size_t()
    
    result = ctypes.windll.kernel32.ReadProcessMemory(handle, address, buffer, size, ctypes.byref(bytes_read))
    
    if result == 0:
        error_code = ctypes.windll.kernel32.GetLastError()
        print(colored(f"ReadProcessMemory failed with error code: {error_code}", "red"))
        return None
    
    return buffer.raw[:bytes_read.value]

# Function to write data to process memory
def write_to_process_memory(handle, address, data, size):
    buffer = (ctypes.c_char * size).from_buffer_copy(data)
    bytes_written = ctypes.c_size_t()
    result = ctypes.windll.kernel32.WriteProcessMemory(handle, address, buffer, size, ctypes.byref(bytes_written))
    return result != 0

# Function to change memory protection
def change_memory_protection(handle, address, size, protection):
    old_protection = ctypes.c_ulong()
    ctypes.windll.kernel32.VirtualProtectEx(handle, address, size, protection, ctypes.byref(old_protection))
    return old_protection



emu_info = {
'name': 'duckstation',
'base_exe_dll_name': 'duckstation-qt-x64-ReleaseLTCG.exe',
'main_ram_offset': 0x87E6B0,
'ptr': True,
'double_ptr': False,
'base': True,
}

# Get the PID of the target process
emu_pid = get_pid(emu_info['name'])
if emu_pid is None:
    exit_message = colored(f"Could not find {emu_info['name']} Process!", "red")
    print(exit_message)
    
emu_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, emu_pid)

if emu_info['base']:
    base_address = GetBaseAddressFromEXE(emu_handle, f"{emu_info['base_exe_dll_name']}")

    
    #Get pointer + base address like duckstation and pcsx2 1.7 and dolphin
if emu_info['ptr']:
    try:
        ptr_address = read_process_memory(emu_handle, ctypes.c_ulonglong(base_address + emu_info['main_ram_offset']), 8)
        pointer_value = int.from_bytes(ptr_address, byteorder='little', signed=False)  
    except:
        exit_message = colored(f"Failed to read pointer to main ram", "red")
        print(exit_message)
    
    main_ram = pointer_value    
    print(colored(f"Address of main ram in emu: {hex(main_ram)}", "blue"))
    
#Get base address + pointer, to a pointer like dolphin
if emu_info['double_ptr']:
    try:
        pointer_pointer_address = read_process_memory(emu_handle, ctypes.c_ulonglong(base_address + emu_info['main_ram_offset']), 8)
        pointer_pointer_value = int.from_bytes(pointer_pointer_address, byteorder='little', signed=False)  
        ptr_address = read_process_memory(emu_handle, ctypes.c_ulonglong(pointer_pointer_value), 8)
        pointer_value = int.from_bytes(ptr_address, byteorder='little', signed=False)  
    except:
        exit_message = colored(f"Failed to read pointer to main ram", "red")
        print(exit_message)
    
    main_ram = pointer_value    
    print(colored(f"Address of main ram in emu: {hex(main_ram)}", "blue"))
    
#else just add the offset to the base address, like for bizhawk
elif not emu_info['ptr'] and emu_info['base']:
    main_ram = base_address + emu_info['main_ram_offset']
#situation for if just a pointer, haven't encountered yet
elif not emu_info['base'] and emu_info['ptr']:
    pass
#else just a global address, like mednafen/pcsx2 1.6.0
elif not emu_info['base']:
    main_ram = emu_info['address']
    
#Injecting
MODELS_HEADER_OFFSET = 0x38

MOBY_TYPE_OFFSET = 0x36
SPARX_ANIM = 0x4
SPARX_TYPE = 0x78

ptr_to_models_base_address = ctypes.c_ulonglong(main_ram + int("0x076378", base=16)) # Global Pointer for models, with emulator base ram
ptr_to_models_base_address_int = ptr_to_models_base_address.value # As an int
change_memory_protection(emu_handle, ptr_to_models_base_address, 0x300, PAGE_EXECUTE_READWRITE) # Allow reading
ptr_to_models = read_process_memory(emu_handle, ptr_to_models_base_address, 4)      # The current address to the models in the current level
ptr_to_models_int = int.from_bytes(ptr_to_models[0:3], byteorder='little')          # Make an int, and remove 0x80 
print(hex(ptr_to_models_int))

ptr_to_sparx_base_address = ctypes.c_ulonglong(main_ram + int("0x075898", base=16)) # Global Pointer for Sparx with emulator base ram
change_memory_protection(emu_handle, ptr_to_sparx_base_address, 0x300, PAGE_EXECUTE_READWRITE)  # Allow reading
ptr_to_sparx = read_process_memory(emu_handle, ptr_to_sparx_base_address, 4)        # The current address to Sparx
ptr_to_sparx_int = int.from_bytes(ptr_to_sparx[0:3], byteorder='little')            # Make an int, and remove 0x80 
print(hex(ptr_to_sparx_int))

change_memory_protection(emu_handle, ctypes.c_ulonglong(ptr_to_models_base_address_int + (SPARX_TYPE * 4)), 0x300, PAGE_EXECUTE_READWRITE)
start_of_sparx_models = read_process_memory(emu_handle, ctypes.c_ulonglong(ptr_to_models_base_address_int + (SPARX_TYPE * 4)), 4)
start_of_sparx_models_int = int.from_bytes(start_of_sparx_models[0:3], byteorder='little')
print(hex(start_of_sparx_models_int))

start_of_current_sparx_anim_models_ptr_int = (SPARX_ANIM * 4 & 0xFF) + start_of_sparx_models_int + MODELS_HEADER_OFFSET
print(hex(start_of_current_sparx_anim_models_ptr_int))
change_memory_protection(emu_handle, ctypes.c_ulonglong(main_ram + start_of_current_sparx_anim_models_ptr_int), 0x300, PAGE_EXECUTE_READWRITE)
#start_of_current_sparx_anim_models = read_process_memory(emu_handle, ctypes.c_ulonglong(base_address + start_of_current_sparx_anim_models_ptr_int), 4)
#start_of_current_sparx_anim_models_int = int.from_bytes(start_of_current_sparx_anim_models[0:4], byteorder='little')
#print(hex(start_of_current_sparx_anim_models_int))
start_of_sparx_vertex_colors_ptr = start_of_current_sparx_anim_models_ptr_int + 0x290
print("bruh:" + hex(start_of_sparx_vertex_colors_ptr))

change_memory_protection(emu_handle, ctypes.c_ulonglong(main_ram + start_of_sparx_vertex_colors_ptr), 0x300, PAGE_EXECUTE_READWRITE)
start_of_sparx_vertex_colors = read_process_memory(emu_handle, ctypes.c_ulonglong(main_ram + start_of_sparx_vertex_colors_ptr), 4)
start_of_sparx_vertex_colors_int = int.from_bytes(start_of_sparx_vertex_colors[0:3], byteorder='little')
print(hex(start_of_sparx_vertex_colors_int))

change_memory_protection(emu_handle, ctypes.c_ulonglong(main_ram + start_of_sparx_vertex_colors_int), 0x300, PAGE_EXECUTE_READWRITE)
sparx_vertex_colors = read_process_memory(emu_handle, ctypes.c_ulonglong(main_ram + start_of_sparx_vertex_colors_int), 4)
sparx_vertex_colors_int = int.from_bytes(sparx_vertex_colors[0:4], byteorder='little')
print(hex(sparx_vertex_colors_int))


ctypes.windll.kernel32.CloseHandle(emu_handle)

if __name__ == "__main__":
    duckstation_info = {
    'name': 'duckstation',
    'base_exe_dll_name': 'duckstation-qt-x64-ReleaseLTCG.exe',
    'main_ram_offset': 0x87E6B0,
    'ptr': True,
    'double_ptr': False,
    'base': True,
    }
    
    mednafen_131_info = {
    'name': 'mednafen',
    'address': 0x2034E80,
    'base': False,
    'ptr': False,
    'double_ptr': False
    }
