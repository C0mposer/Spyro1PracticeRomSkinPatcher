import dearpygui.dearpygui as dpg
import pyperclip
import inject
from inject_custom_skin_into_iso import *
from convert_bmp import *

def select_emulator_callback(sender, app_data):
    selected_emu = dpg.get_value("emulator_choice")
    if selected_emu == "Duckstation 0.1-5936":
        dpg.configure_item("inject_button", label="Inject into Duckstation 0.1-5936")
    if selected_emu == "Bizhawk 2.6.1":
        dpg.configure_item("inject_button", label="Inject into Bizhawk 2.6.1")

def inject_button_callback(sender, app_data):
    dpg.show_item("notification_text")
    dpg.set_value("notification_text", "Injecting...")
    
    selected_emu = dpg.get_value("emulator_choice")
    
    # Retrieve the color values from each flame triangle color picker
    base_color = dpg.get_value("Base Color")
    tip_color = dpg.get_value("Tip Color")
    right_color = dpg.get_value("Right Color")
    left_color = dpg.get_value("Left Color")
    
    # Retrieve the color values from the sparx glow color picker
    sparx_glow_color = dpg.get_value("Sparx Glow Color")
    
    # Retrieve the color values from the gem color picer
    one_gem_shadow_color = dpg.get_value("1 Shadow Color")
    one_gem_highlight_color = dpg.get_value("1 Highlight Color")
    
    two_gem_shadow_color = dpg.get_value("2 Shadow Color")
    two_gem_highlight_color = dpg.get_value("2 Highlight Color")
    
    five_gem_shadow_color = dpg.get_value("5 Shadow Color")
    five_gem_highlight_color = dpg.get_value("5 Highlight Color")
    
    ten_gem_shadow_color = dpg.get_value("10 Shadow Color")
    ten_gem_highlight_color = dpg.get_value("10 Highlight Color")
    
    twenty_five_gem_shadow_color = dpg.get_value("25 Shadow Color")
    twenty_five_gem_highlight_color = dpg.get_value("25 Highlight Color")
    
    gem_colors_list = [
        one_gem_shadow_color, 
        one_gem_highlight_color, 
        two_gem_shadow_color,
        two_gem_highlight_color,
        five_gem_shadow_color,
        five_gem_highlight_color,
        ten_gem_shadow_color,
        ten_gem_highlight_color,
        twenty_five_gem_shadow_color,
        twenty_five_gem_highlight_color  
        ]
    
    print(gem_colors_list)
    
    # Retrieve the file paths
    flame_path = dpg.get_value("Flame File Path")
    spyro_path = dpg.get_value("Spyro File Path")
    sparx_path = dpg.get_value("Sparx File Path")
    
    print(f"Base Color: {base_color}")
    print(f"Tip Color: {tip_color}")
    print(f"Right Color: {right_color}")
    print(f"Left Color: {left_color}")
    print(f"Spyro Skin File Path: {spyro_path}")
    print(f"Flame Skin File Path: {flame_path}")
    
    # Call your custom function with the selected colors and file paths
    inject.InjectIntoEmu(selected_emu, base_color, tip_color, right_color, left_color, sparx_glow_color, gem_colors_list, flame_path, spyro_path, sparx_path)
    
    # Show notification
    dpg.set_value("notification_text", "Injection Complete!")
    dpg.show_item("notification_text")
  
# Injects Custom Skin Into Practice ROM
def inject_rom_button_callback(sender, app_data):
    #Show Injecting Text
    dpg.show_item("rom_notification_text")
    dpg.set_value("rom_notification_text", "Injecting into ROM...")
    
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
    dpg.set_value("rom_notification_text", "Injection Into Practice ROM Complete!\n\nChoose the \"SPYRO SKIN CUSTOM\" in the cosmetic menu to use it!")
    dpg.show_item("rom_notification_text")
    
def copy_color_button_callback(sender, app_data):
    # Retrieve the color values from each color picker
    dpg.hide_item("copy_text")
    
    center_color = dpg.get_value("Base Color")
    tip_color = dpg.get_value("Tip Color")
    right_color = dpg.get_value("Right Color")
    left_color = dpg.get_value("Left Color")
    
    color_c_string = f"""
        .tip.r = {hex(int(tip_color[0]))},
		.tip.g = {hex(int(tip_color[1]))},
		.tip.b = {hex(int(tip_color[2]))},
		.tip.shape_code = 0x30,

		.center.r = {hex(int(center_color[0]))},
		.center.g = {hex(int(center_color[1]))},
		.center.b = {hex(int(center_color[2]))},
		.center.shape_code = 0x30,
		
		.right.r = {hex(int(right_color[0]))},
		.right.g = {hex(int(right_color[1]))},
		.right.b = {hex(int(right_color[2]))},
		.right.shape_code = 0x30,

		.left.r = {hex(int(left_color[0]))},
		.left.g = {hex(int(left_color[1]))},
		.left.b = {hex(int(left_color[2]))},
		.left.shape_code = 0x30
    """
    
    pyperclip.copy(color_c_string)
    
    print("Copied color to clipboard")
    
    dpg.show_item("copy_text")
    dpg.set_value("copy_text", "Copied to Clipboard!")
    


def file_dialog_callback(sender, app_data):
    # Update the input text with the selected file path
    dpg.set_value(sender, app_data['file_path_name'])

if __name__ == "__main__":

    dpg.create_context()

    # Create the main application window
    with dpg.window(label="Spyro 1 Skin Tester", width=800, height=1000, no_move=True) as main_window:
        with dpg.tab_bar():
            
            #Tab 1
            with dpg.tab(label="BMP Selector"):
                # Add file path inputs and file dialogs
                dpg.add_text("~ BMP Skin Selector ~", color=(00, 0xB0, 0xFF, 0xFF))
                
                # Add file path inputs and file dialogs
                dpg.add_text("Select .bmp File Paths:")
                
                # Add spacing between the title and the file path inputs
                dpg.add_spacing(count=1)

                # Group for the spyro skin file path input and button
                with dpg.group(horizontal=True):
                    dpg.add_input_text(label="Spyro Skin .bmp", width=300, tag="Spyro File Path", readonly=True)
                    dpg.add_button(label="Browse", callback=lambda: dpg.show_item("spyro_file_dialog"))

                # Add spacing between the file path groups
                dpg.add_spacing(count=2)
                
                # Group for the flame skin file path input and button
                with dpg.group(horizontal=True):
                    dpg.add_input_text(label="Flame Skin .bmp", width=300, tag="Flame File Path", readonly=True)
                    dpg.add_button(label="Browse", callback=lambda: dpg.show_item("flame_file_dialog"))

                # Add spacing between the file path groups
                dpg.add_spacing(count=2)
                
                # Group for the flame skin file path input and button
                with dpg.group(horizontal=True):
                    dpg.add_input_text(label="Sparx Skin .bmp", width=300, tag="Sparx File Path", readonly=True)
                    dpg.add_button(label="Browse", callback=lambda: dpg.show_item("sparx_file_dialog"))
                    
                dpg.add_spacing(count=5)
                       
                # Create file dialogs
                with dpg.file_dialog(directory_selector=False, show=False, callback=lambda s, d: file_dialog_callback("Spyro File Path", d), tag="spyro_file_dialog", min_size=(750, 800), max_size=(750, 800), modal=True):
                    dpg.add_file_extension(".bmp", color=(255, 255, 255, 255))  # Show all file types
                    
                with dpg.file_dialog(directory_selector=False, show=False, callback=lambda s, d: file_dialog_callback("Flame File Path", d), tag="flame_file_dialog", min_size=(750, 800), max_size=(750, 800), modal=True):
                    dpg.add_file_extension(".bmp", color=(255, 255, 255, 255))  # Show all file types
                    
                with dpg.file_dialog(directory_selector=False, show=False, callback=lambda s, d: file_dialog_callback("Sparx File Path", d), tag="sparx_file_dialog", min_size=(750, 800), max_size=(750, 800), modal=True):
                    dpg.add_file_extension(".bmp", color=(255, 255, 255, 255))  # Show all file types

            
            #Tab 2
            with dpg.tab(label="Flame Triangle Editor"):
                dpg.add_text("~ Edit Flame Triangle Colors ~", color=(0xFF, 0xC0, 0x00, 0xFF))
                dpg.add_spacing(count=2)
                
                # Create first row of color wheels
                with dpg.group(horizontal=True):
                    dpg.add_color_picker((0xF0, 0xF0, 60, 255), width=200, label="Base Color", tag="Base Color")
                    dpg.add_color_picker((0xD0, 0x90, 0x40, 255), width=200, label="Tip Color", tag="Tip Color")

                # Create second row of color wheels
                with dpg.group(horizontal=True):
                    dpg.add_color_picker((0x90, 0x60, 0x20, 255), width=200, label="Right Color", tag="Right Color")
                    dpg.add_color_picker((0xA0, 0x30, 0x10, 255), width=200, label="Left Color", tag="Left Color")
                
                dpg.add_spacing(count=5)
                
                # Add a larger button to submit and print selected colors
                dpg.add_button(label="Copy Flame Triangle Color", callback=copy_color_button_callback, width=200, height=30)

                dpg.add_text("Copied to clipboard", tag="copy_text")
                dpg.hide_item("copy_text")
                
                dpg.add_spacing(count=5)
            
            # Tab 3
            with dpg.tab(label="Sparx Glow Editor"):
                dpg.add_text("~ Edit Sparx Glow ~", color=(0xFF, 0xF0, 0x00, 0xFF))
                dpg.add_spacing(count=2)
                
                # Create first row of color wheels
                with dpg.group(horizontal=True):
                    dpg.add_color_picker((0xC0, 0xC0, 0x60, 255), width=200, label="Sparx Glow Color", tag="Sparx Glow Color")

                dpg.add_spacing(count=5)
                
            #Tab 4
            with dpg.tab(label="Gem Color Editor"):
                dpg.add_text("~ Edit Gem Colors ~", color=(0xFF, 0x00, 0x40, 0xFF))
                dpg.add_spacing(count=2)
                
                # Create first row of color wheels
                with dpg.group(horizontal=True):
                    dpg.add_text("1 Gem:")
                    dpg.add_color_picker((0x50, 0x00, 0x00, 255), width=200, label="Shadow Color", tag="1 Shadow Color")
                    dpg.add_color_picker((0xFF, 0x00, 0x00, 255), width=200, label="Highlight Color", tag="1 Highlight Color")

                # Create second row of color wheels
                with dpg.group(horizontal=True):
                    dpg.add_text("2 Gem:")
                    dpg.add_color_picker((0x00, 0x50, 0x00, 255), width=200, label="Shadow Color", tag="2 Shadow Color")
                    dpg.add_color_picker((0x00, 0xFF, 0x00, 255), width=200, label="Highlight Color", tag="2 Highlight Color")
                    
                with dpg.group(horizontal=True):
                    dpg.add_text("5 Gem:")
                    dpg.add_color_picker((0x00, 0x00, 0x50, 255), width=200, label="Shadow Color", tag="5 Shadow Color")
                    dpg.add_color_picker((0x00, 0x00, 0xFF, 255), width=200, label="Highlight Color", tag="5 Highlight Color")
                    
                with dpg.group(horizontal=True):
                    dpg.add_text("10 Gem:")
                    dpg.add_color_picker((0x50, 0x50, 0x00, 255), width=200, label="Shadow Color", tag="10 Shadow Color")
                    dpg.add_color_picker((0xFF, 0xFF, 0x00, 255), width=200, label="Highlight Color", tag="10 Highlight Color")
                    
                with dpg.group(horizontal=True):
                    dpg.add_text("25 Gem:")
                    dpg.add_color_picker((0x50, 0x00, 0x50, 255), width=200, label="Shadow Color", tag="25 Shadow Color")
                    dpg.add_color_picker((0xFF, 0x00, 0xFF, 255), width=200, label="Highlight Color", tag="25 Highlight Color")
                
                dpg.add_spacing(count=5)
                
        #! ROM Patcher (Seperate Program)
        #     #Tab 5
        #     with dpg.tab(label="Inject Skins into Practice Rom"):
        #         dpg.add_text("~ Inject Skins into Practice Rom ~", color=(0x0, 0xFF, 00, 0xFF))
        #         dpg.add_spacing(count=2)
                
        #         dpg.add_text("Select your practice rom .bin file:")

        #         with dpg.group(horizontal=True):
        #             dpg.add_input_text(label="Practice Rom .bin", width=300, tag="ROM File Path", readonly=True)
        #             dpg.add_button(label="Browse", callback=lambda: dpg.show_item("rom_file_dialog"))
                
        #         # Create file dialogs
        #         with dpg.file_dialog(directory_selector=False, show=False, callback=lambda s, d: file_dialog_callback("ROM File Path", d), tag="rom_file_dialog", min_size=(750, 800), max_size=(750, 800), modal=True):
        #             dpg.add_file_extension(".bin", color=(255, 255, 255, 255))  # Show all file types
                    
        #         dpg.add_spacing(count=5)
                
        #         dpg.add_button(label="Inject Into Practice Rom", tag="inject_rom_button", callback=inject_rom_button_callback, width=300, height=50)

        #         # Add notification text (initially hidden)
        #         dpg.add_text("Injection into ROM Complete!", tag="rom_notification_text")
        #         dpg.hide_item("rom_notification_text")

        #         dpg.add_spacing(count=250)
        # Add an emulator selection option
        dpg.add_text("Select an Emulator:")
        dpg.add_radio_button(tag="emulator_choice", items=("Duckstation 0.1-5936", "Bizhawk 2.6.1"), default_value="Duckstation 0.1-5936", callback=select_emulator_callback, horizontal=True)
        # Add a larger button to inject, across all tabs
        dpg.add_button(label="Inject Into Duckstation 0.1-5936", tag="inject_button", callback=inject_button_callback, width=300, height=50)

        # Add notification text (initially hidden)
        dpg.add_text("Injection Complete!", tag="notification_text")
        dpg.hide_item("notification_text")
        
        dpg.set_primary_window(main_window, True)

    dpg.create_viewport(title='Skin Tester', width=815, height=1040)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    

    # Every-frame loop
    while dpg.is_dearpygui_running():
        # Render each frame
        dpg.render_dearpygui_frame()

    dpg.destroy_context()