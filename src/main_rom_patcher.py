import dearpygui.dearpygui as dpg
import pyperclip
import inject
from inject_custom_skin_into_iso import *
from convert_bmp import *


# Injects Custom Skin Into Practice ROM
def inject_rom_button_callback(sender, app_data):
    #Show Injecting Text
    dpg.show_item("rom_notification_text")
    dpg.set_value("rom_notification_text", "Patching ROM...")
    
    # Retrieve the file paths
    rom_path = dpg.get_value("ROM File Path")
    spyro_path = dpg.get_value("Spyro File Path")
    #flame_path = dpg.get_value("Flame File Path")
    #sparx_path = dpg.get_value("Sparx File Path")

    custom_spyro_bin_path = ConvertToClutBinFile(spyro_path)

    # The byte sequence to search for
    end_of_spyro_skin_byte_sequence = bytes.fromhex('B944B23C')
    #end_of_flame_skin_byte_sequence = bytes.fromhex('8CB14AA9')
    #end_of_sparx_skin_byte_sequence = bytes.fromhex('494949FF303030FF')

    offset_to_end_of_last_spyro_skin = FindBytesInFile(rom_path, end_of_spyro_skin_byte_sequence) + 4 # +4 because found last 4 bytes of spyro skins
    #offset_to_end_of_last_flame_skin = FindBytesInFile(file_path, end_of_flame_skin_byte_sequence) + 4 # +4 because found last 4 bytes of flame skins
    #offset_to_end_of_last_sparx_skin = FindBytesInFile(file_path, end_of_sparx_skin_byte_sequence) + 12 # +12 because found last 8 bytes of sparx skins. More generic data, so more bytes to find it
    
    InjectCustomSkin(rom_path, custom_spyro_bin_path, offset_to_end_of_last_spyro_skin)
    
    # Show Finished Injecting Text
    dpg.set_value("rom_notification_text", "Patching Complete!\n\nChoose \"SPYRO SKIN CUSTOM\" in the cosmetic menu to use it!")
    dpg.show_item("rom_notification_text")
    

def file_dialog_callback(sender, app_data):
    # Update the input text with the selected file path
    dpg.set_value(sender, app_data['file_path_name'])

if __name__ == "__main__":

    dpg.create_context()

    # Create the main application window
    with dpg.window(label="Spyro 1 Practice Rom Skin Patcher", width=800, height=1000, no_move=True) as main_window:
        with dpg.tab_bar():
            
            #Tab 1
            with dpg.tab(label="BMP Selector"):
                # Add file path inputs and file dialogs
                dpg.add_text("~ Practice Rom Skin Patcher ~", color=(00, 0xFF, 0x00, 0xFF))
                
                # Add file path inputs and file dialogs
                dpg.add_text("Select Spyro Skin .bmp file:")
                
                # Add spacing between the title and the file path inputs
                dpg.add_spacing(count=1)

                # Group for the spyro skin file path input and button
                with dpg.group(horizontal=True):
                    dpg.add_input_text(label="Spyro Skin .bmp", width=300, tag="Spyro File Path", readonly=True)
                    dpg.add_button(label="Browse", callback=lambda: dpg.show_item("spyro_file_dialog"))

                dpg.add_spacing(count=5)
                
                dpg.add_text("Select Your Practice Rom .bin file:")

                dpg.add_spacing(count=1)
                
                with dpg.group(horizontal=True):
                    dpg.add_input_text(label="Practice Rom .bin", width=300, tag="ROM File Path", readonly=True)
                    dpg.add_button(label="Browse", callback=lambda: dpg.show_item("rom_file_dialog"))
                
                # Create file dialogs
                with dpg.file_dialog(directory_selector=False, show=False, callback=lambda s, d: file_dialog_callback("Spyro File Path", d), tag="spyro_file_dialog", min_size=(750, 800), max_size=(750, 800), modal=True):
                    dpg.add_file_extension(".bmp", color=(255, 255, 255, 255))  # Show all file types
                with dpg.file_dialog(directory_selector=False, show=False, callback=lambda s, d: file_dialog_callback("ROM File Path", d), tag="rom_file_dialog", min_size=(750, 800), max_size=(750, 800), modal=True):
                    dpg.add_file_extension(".bin", color=(255, 255, 255, 255))  # Show all file types
                    
                dpg.add_spacing(count=5)
                
                dpg.add_button(label="Patch Your Practice ROM", tag="inject_rom_button", callback=inject_rom_button_callback, width=300, height=50)

                # Add notification text (initially hidden)
                dpg.add_text("Injection into ROM Complete!", tag="rom_notification_text")
                dpg.hide_item("rom_notification_text")

                dpg.add_spacing(count=250)
        
        dpg.set_primary_window(main_window, True)

    dpg.create_viewport(title='Skin Tester', width=815, height=1040)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    

    # Every-frame loop
    while dpg.is_dearpygui_running():
        # Render each frame
        dpg.render_dearpygui_frame()

    dpg.destroy_context()