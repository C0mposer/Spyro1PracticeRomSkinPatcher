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

def GetSparxVertexColorAddress(emu_handle, main_ram):
    #Sparx Model Shit
    MODELS_HEADER_OFFSET = 0x38

    MOBY_TYPE_OFFSET = 0x36
    SPARX_ANIM = 0x4
    SPARX_TYPE = 0x78

    ptr_to_models_base_address = ctypes.c_ulonglong(main_ram + int("0x076378", base=16))    # Global Pointer for models, with emulator base ram
    ptr_to_models_base_address_int = ptr_to_models_base_address.value # As an int
    change_memory_protection(emu_handle, ptr_to_models_base_address, 0x300, PAGE_EXECUTE_READWRITE) # Allow reading
    ptr_to_models = read_process_memory(emu_handle, ptr_to_models_base_address, 4)          # Dereference the current address to the models in the current level
    ptr_to_models_int = int.from_bytes(ptr_to_models[0:3], byteorder='little')              # Make an int, and remove 0x80 
    print(hex(ptr_to_models_int))

    ptr_to_sparx_base_address = ctypes.c_ulonglong(main_ram + int("0x075898", base=16))     # Global Pointer for Sparx with emulator base ram
    change_memory_protection(emu_handle, ptr_to_sparx_base_address, 0x300, PAGE_EXECUTE_READWRITE)  # Allow reading
    ptr_to_sparx = read_process_memory(emu_handle, ptr_to_sparx_base_address, 4)            # Dereference the current address to Sparx
    ptr_to_sparx_int = int.from_bytes(ptr_to_sparx[0:3], byteorder='little')                # Make an int, and remove 0x80 
    print(hex(ptr_to_sparx_int))

    change_memory_protection(emu_handle, ctypes.c_ulonglong(ptr_to_models_base_address_int + (SPARX_TYPE * 4)), 0x300, PAGE_EXECUTE_READWRITE)  # Allow reading
    start_of_sparx_models = read_process_memory(emu_handle, ctypes.c_ulonglong(ptr_to_models_base_address_int + (SPARX_TYPE * 4)), 4)           # Dereference the current address to the start of all sparx's model's
    start_of_sparx_models_int = int.from_bytes(start_of_sparx_models[0:3], byteorder='little')  # Make an int, and remove 0x80 
    print(hex(start_of_sparx_models_int))

    start_of_current_sparx_anim_models_ptr_int = (SPARX_ANIM * 4 & 0xFF) + start_of_sparx_models_int + MODELS_HEADER_OFFSET # Pointer to the start of yellow sparx's model
    print(hex(start_of_current_sparx_anim_models_ptr_int))
    change_memory_protection(emu_handle, ctypes.c_ulonglong(main_ram + start_of_current_sparx_anim_models_ptr_int), 0x300, PAGE_EXECUTE_READWRITE)  # Allow reading
    
    #Not hardcoded. Probably un-needed
    #start_of_current_sparx_anim_models = read_process_memory(emu_handle, ctypes.c_ulonglong(base_address + start_of_current_sparx_anim_models_ptr_int), 4)
    #start_of_current_sparx_anim_models_int = int.from_bytes(start_of_current_sparx_anim_models[0:4], byteorder='little')
    #print(hex(start_of_current_sparx_anim_models_int))
    
    start_of_sparx_vertex_colors_ptr = start_of_current_sparx_anim_models_ptr_int + 0x290 # Hard coded offset to his vertex color ptr, since it's always the same at this point
    print(hex(start_of_sparx_vertex_colors_ptr))

    change_memory_protection(emu_handle, ctypes.c_ulonglong(main_ram + start_of_sparx_vertex_colors_ptr), 0x300, PAGE_EXECUTE_READWRITE)    # Allow reading
    start_of_sparx_vertex_colors = read_process_memory(emu_handle, ctypes.c_ulonglong(main_ram + start_of_sparx_vertex_colors_ptr), 4)      # Derefernce to get the address of yellow sparx's vertex colors
    start_of_sparx_vertex_colors_int = int.from_bytes(start_of_sparx_vertex_colors[0:3], byteorder='little') # Make an int, and remove 0x80
    print(hex(start_of_sparx_vertex_colors_int))

    #change_memory_protection(emu_handle, ctypes.c_ulonglong(main_ram + start_of_sparx_vertex_colors_int), 0x300, PAGE_EXECUTE_READWRITE)   
    #sparx_vertex_colors = read_process_memory(emu_handle, ctypes.c_ulonglong(main_ram + start_of_sparx_vertex_colors_int), 4)
    #sparx_vertex_colors_int = int.from_bytes(sparx_vertex_colors[0:4], byteorder='little')
    
    return ctypes.c_ulonglong(main_ram + start_of_sparx_vertex_colors_int)


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

def ConvertGemColorData(gem_colors):
    gem_bytes = b""
    
    gem_bytes += int(gem_colors[0][0]).to_bytes(1, 'big') #1 Gem Shadow R
    gem_bytes += int(gem_colors[0][1]).to_bytes(1, 'big') #1 Gem Shadow G
    gem_bytes += int(gem_colors[0][2]).to_bytes(1, 'big') #1 Gem Shadow B
    gem_bytes += int(0x00).to_bytes(1, 'big')
    gem_bytes += int(gem_colors[1][0]).to_bytes(1, 'big') #1 Gem Highlight R
    gem_bytes += int(gem_colors[1][1]).to_bytes(1, 'big') #1 Gem Highlight G
    gem_bytes += int(gem_colors[1][2]).to_bytes(1, 'big') #1 Gem Highlight B
    gem_bytes += int(0x00).to_bytes(1, 'big')
    
    gem_bytes += int(gem_colors[2][0]).to_bytes(1, 'big') #2 Gem Shadow R
    gem_bytes += int(gem_colors[2][1]).to_bytes(1, 'big') #2 Gem Shadow G
    gem_bytes += int(gem_colors[2][2]).to_bytes(1, 'big') #2 Gem Shadow B
    gem_bytes += int(0x00).to_bytes(1, 'big')
    gem_bytes += int(gem_colors[3][0]).to_bytes(1, 'big') #2 Gem Highlight R
    gem_bytes += int(gem_colors[3][1]).to_bytes(1, 'big') #2 Gem Highlight G
    gem_bytes += int(gem_colors[3][2]).to_bytes(1, 'big') #2 Gem Highlight B
    gem_bytes += int(0x00).to_bytes(1, 'big')
    
    gem_bytes += int(gem_colors[4][0]).to_bytes(1, 'big') #5 Gem Shadow R
    gem_bytes += int(gem_colors[4][1]).to_bytes(1, 'big') #5 Gem Shadow G
    gem_bytes += int(gem_colors[4][2]).to_bytes(1, 'big') #5 Gem Shadow B
    gem_bytes += int(0x00).to_bytes(1, 'big')
    gem_bytes += int(gem_colors[5][0]).to_bytes(1, 'big') #5 Gem Highlight R
    gem_bytes += int(gem_colors[5][1]).to_bytes(1, 'big') #5 Gem Highlight G
    gem_bytes += int(gem_colors[5][2]).to_bytes(1, 'big') #5 Gem Highlight B
    gem_bytes += int(0x00).to_bytes(1, 'big')
    
    gem_bytes += int(gem_colors[6][0]).to_bytes(1, 'big') #10 Shadow Gem R
    gem_bytes += int(gem_colors[6][1]).to_bytes(1, 'big') #10 Shadow Gem G
    gem_bytes += int(gem_colors[6][2]).to_bytes(1, 'big') #10 Shadow Gem B
    gem_bytes += int(0x00).to_bytes(1, 'big')
    gem_bytes += int(gem_colors[7][0]).to_bytes(1, 'big') #10 Highlight Gem R
    gem_bytes += int(gem_colors[7][1]).to_bytes(1, 'big') #10 Highlight Gem G
    gem_bytes += int(gem_colors[7][2]).to_bytes(1, 'big') #10 Highlight Gem B
    gem_bytes += int(0x00).to_bytes(1, 'big')
    
    gem_bytes += int(gem_colors[8][0]).to_bytes(1, 'big') #25 Shadow Gem R
    gem_bytes += int(gem_colors[8][1]).to_bytes(1, 'big') #25 Shadow Gem G
    gem_bytes += int(gem_colors[8][2]).to_bytes(1, 'big') #25 Shadow Gem B
    gem_bytes += int(0x00).to_bytes(1, 'big')
    gem_bytes += int(gem_colors[9][0]).to_bytes(1, 'big') #25 Highlight Gem R
    gem_bytes += int(gem_colors[9][1]).to_bytes(1, 'big') #25 Highlight Gem G
    gem_bytes += int(gem_colors[9][2]).to_bytes(1, 'big') #25 Highlight Gem B
    gem_bytes += int(0x00).to_bytes(1, 'big')


    return gem_bytes
    

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

def InjectIntoEmu(selected_emu, tip_color, base_color, left_color, right_color, sparx_glow_color, gem_colors, fire_bmp, spyro_bmp, sparx_bmp):
    
    if selected_emu == "Duckstation 0.1-5936":
        emu_info = {
        'name': 'duckstation',
        'base_exe_dll_name': 'duckstation-qt-x64-ReleaseLTCG.exe',
        'main_ram_offset': 0x87E6B0,
        'ptr': True,
        'double_ptr': False,
        'base': True,
        }
    if selected_emu == "Bizhawk 2.6.1":
        emu_info = {
        'name': 'EmuHawk',
        'base_exe_dll_name': 'octoshock.dll',
        'main_ram_offset': 0x310f80,
        'ptr': False,
        'double_ptr': False,
        'base': True
        }

    # Get the PID of the target process
    emu_pid = get_pid(emu_info['name'])
    if emu_pid is None:
        exit_message = colored(f"Could not find {emu_info['name']} Process!", "red")
        print(exit_message)
        return "Could not find {emu_info['name']} Process!"
        
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
            return "Failed to read pointer to main ram"
        
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
            return "Failed to read pointer to main ram"
        
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
    
    address_to_write_spyro_bmp_to = ctypes.c_ulonglong(main_ram + int("0x0740B0", base=16))
    address_to_write_fire_bmp_to = ctypes.c_ulonglong(main_ram + int("0x0742B0", base=16))
    address_to_write_sparx_bmp_to = GetSparxVertexColorAddress(emu_handle, main_ram)
    address_to_write_triangle_to = ctypes.c_ulonglong(main_ram + int("0x06E1A8", base=16))
    
    address_to_write_sparx_glow_to = ctypes.c_ulonglong(main_ram + int("0x0788C0", base=16))
    address_to_write_sparx_glow2_to = ctypes.c_ulonglong(main_ram + int("0x07880C", base=16))
    
    address_to_write_gem_colors_to = ctypes.c_ulonglong(main_ram + int("0x06E454", base=16))
    
    address_to_write_bool_to = ctypes.c_ulonglong(main_ram + int("0x074300", base=16))
    
    spyro_bmp_path = spyro_bmp
    spyro_bin_path = None
    spyro_bmp_data = b""
    
    fire_bmp_path = fire_bmp
    fire_bmp_data = b""
    fire_bin_path = None
    
    sparx_bmp_path = sparx_bmp
    sparx_bmp_data = b""
    sparx_bin_path = None
    
    flame_triangle_color_data = ConvertFlameColorData(base_color, tip_color, left_color, right_color)
    sparx_glow_color_data = ConvertSparxGlowColorData(sparx_glow_color)
    gem_color_data = ConvertGemColorData(gem_colors)
    
    if spyro_bmp_path:
        spyro_bin_path = spyro_bmp.split(".")[0] + ".bin"
        convert_bmp.ConvertToClutBinFile(spyro_bmp)
    if fire_bmp_path:
        fire_bin_path = fire_bmp.split(".")[0] + ".bin"
        convert_bmp.ConvertClutBinFileTransparent(fire_bmp)
    if sparx_bmp_path:
        sparx_bin_path = sparx_bmp.split(".")[0] + ".bin"
        convert_bmp.ConvertToRGB(sparx_bmp)
    
    if spyro_bin_path:
        with open(spyro_bin_path, "rb+") as bmp_file:
            spyro_bmp_data = bmp_file.read()
    if fire_bin_path:
        with open(fire_bin_path, "rb+") as bmp_file:
            fire_bmp_data = bmp_file.read()
    if sparx_bin_path:
        with open(sparx_bin_path, "rb+") as bmp_file:
            sparx_bmp_data = bmp_file.read()

    
    #print(hex(main_ram + int("0x80070000", base=16)))
    old_protection = change_memory_protection(emu_handle, address_to_write_spyro_bmp_to, 0x300, PAGE_EXECUTE_READWRITE)
    old_protection = change_memory_protection(emu_handle, address_to_write_fire_bmp_to, 0x300, PAGE_EXECUTE_READWRITE)
    old_protection = change_memory_protection(emu_handle, address_to_write_triangle_to, 0x300, PAGE_EXECUTE_READWRITE)
    
    if spyro_bmp_path:
        if write_to_process_memory(emu_handle, address_to_write_spyro_bmp_to, spyro_bmp_data, len(spyro_bmp_data)):
            print(colored(f"Successfully placed spyro BMP at: {hex(int("0x0740B0", base=16))}", "yellow"))
      
    if fire_bmp_path:  
        if write_to_process_memory(emu_handle, address_to_write_fire_bmp_to, fire_bmp_data, len(fire_bmp_data)):
            print(colored(f"Successfully placed fire BMP at: {hex(int("0x0742B0", base=16))}", "yellow"))
            
    if sparx_bmp_path:  
        #print("sparx color addr" + hex(address_to_write_sparx_bmp_to.value - main_ram))
        if write_to_process_memory(emu_handle, address_to_write_sparx_bmp_to, sparx_bmp_data, len(sparx_bmp_data)):
            print(colored(f"Successfully placed sparx BMP at: {hex(address_to_write_sparx_bmp_to.value - main_ram)}", "yellow"))
        
    if flame_triangle_color_data:
        if write_to_process_memory(emu_handle, address_to_write_triangle_to, flame_triangle_color_data, len(flame_triangle_color_data)):
            print(colored(f"Successfully placed flame triangles at: {hex(int("0x06E1A8", base=16))}", "yellow"))
    if sparx_glow_color_data:
        if write_to_process_memory(emu_handle, address_to_write_sparx_glow_to, sparx_glow_color_data, len(sparx_glow_color_data)):
            if write_to_process_memory(emu_handle, address_to_write_sparx_glow2_to, sparx_glow_color_data, len(sparx_glow_color_data)):
                print(colored(f"Successfully placed sparx glow at: {hex(int("0x07880C", base=16))} and {hex(int("0x0788C0", base=16))}", "yellow"))
    if gem_color_data:
        if write_to_process_memory(emu_handle, address_to_write_gem_colors_to, gem_color_data, len(gem_color_data)):
                print(colored(f"Successfully placed gem colors glow at: {hex(int("0x06E454", base=16))}", "yellow"))

         
    
    
    
    if write_to_process_memory(emu_handle, address_to_write_bool_to, b"0x00000001", 4):
        print(colored(f"Successfully injected update into rom!: {hex(int("0x074300", base=16))}", "green"))
    else:
        #change_memory_protection(emu_handle, address_to_write_to, len(mod_data[cave[0]]), old_protection)
        error_code = ctypes.windll.kernel32.GetLastError()
        exit_message = colored(f"Failed to write to memory. Code: {error_code}", "red")
        print(exit_message)
        return exit_message
        
        

    # function_address = kernel32.GetProcAddress(emu_handle, b"eeMem")
    # error_code = ctypes.windll.kernel32.GetLastError()
    # if not function_address:
    #     exit_message = colored(f"Failed. Code: {error_code}", "red")
    #     print(exit_message)
    #     raise Exception("Failed to get the function address")
    
    # print("TEST", function_address)

    # Close the process handle
    ctypes.windll.kernel32.CloseHandle(emu_handle)
    return f"Successfully injected mod into {emu_info['name']}!"

