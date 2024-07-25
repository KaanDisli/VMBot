
import logging
import telebot 
import config
import requests
import json
import VMControl
import traceback
from pyVmomi import vim
VMControl = VMControl.VMControl()

Username = "@VMBBBBot"
url = "http://127.0.0.1:5000"
token = "7425220594:AAFJqNADAboDwaf77IN5cfuV1rIlYlyuPVs"
bot = telebot.TeleBot(token)

class MockMessage:
    def __init__(self, text, chat_id ):
        self.chat = MockChat(chat_id)
        self.text = text
class MockChat:
    def __init__(self, chat_id):
        self.id = chat_id


def generate_buttons(dico,chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for vm, str in dico.items():
        powerState, User, time_interval = str
        if VMControl.is_linux(vm):
            display_name = f"{vm.name} , {powerState}"
        else:    
            display_name = f"{vm.name}, {powerState}"

        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
            whitelist_or_unwhitelist = "whitelist"
        else:
            whitelist_or_unwhitelist = "unwhitelist"
        button = telebot.types.InlineKeyboardButton(text=display_name, callback_data=f"{whitelist_or_unwhitelist}:{vm.name}:{chat_id}")
        keyboard.add(button)
    return keyboard

def extract_arg(arg):
    return arg.split()[1:]

@bot.message_handler(commands=(["start"]))
def start_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Display all machines", callback_data="display_vm_by_host") 
    keyboard.add(button1) 
    bot.send_message(message.chat.id,"You have started the VMBot, how may I assist you today? To see how to use commands use /help ",reply_markup=keyboard)
@bot.message_handler(commands=(["help"]))

def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton('Contact us if you need any help',url="https://www.simbrella.com/"))
    bot.send_message(message.chat.id,"1- To display all hosts and machines use /display_vm_by_host\n 2- To whitelist both machines on a host use the format /whitelist <host_name> <duration> (seconds)\n ",reply_markup=keyboard)

@bot.message_handler(commands=(["display_vm_by_host"]))
def display_vm_by_host_command(message):
    try:
        dico =  VMControl.get_vm_map()
        keyboard = generate_buttons(dico,message.chat.id)
        bot.send_message(message.chat.id,"Click on a machine to whitelist",reply_markup=keyboard)

    except Exception as e :
        print(e)
        bot.send_message(message.chat.id,"Error")

@bot.message_handler(commands=(["whitelist"]))
def whitelist_command(message):
    try:
        parameters = extract_arg(message.text)
        if parameters == []:
            message_to_send = "Please enter a machine name"
        elif len(parameters) < 2:
            message_to_send = "Insufficient parameters"
        else:
            vm_name = parameters[0] 
            duration = parameters[1] 
            val = VMControl.whitelist_vm_by_name(vm_name,duration)
            
            if val:
                print(f"val {val}")
                if val == -1:
                    message_to_send = f"Machine name incorrect"
                elif val == -2:
                    message_to_send = f"Inappropriate duration, please choose a duration less than an hour (3600 seconds) "
                else:
                    message_to_send = f"Machine {vm_name} is now whitelisted"
                   
            else:
                message_to_send = "Machine already whitelisted"
        bot.send_message(message.chat.id,message_to_send)

    except Exception as e :
        print(e)
        tb_str = traceback.format_exc()
        print(f"Traceback:\n{tb_str}")
        bot.send_message(message.chat.id,"Error")

@bot.message_handler(commands=(["unwhitelist"]))
def unwhitelist_command(message):
    try:
        parameters = extract_arg(message.text)
        if parameters == []:
            message_to_send = "Please enter a machine name"
        else:
            vm_name = parameters[0]  
            val = VMControl.unwhitelist_vm_by_name(vm_name)

            if val:
                if val == -1:
                    message_to_send = f"Machine name incorrect"
                else:
                    message_to_send = f"Machine {vm_name} is now unwhitelisted"
                   
            else:
                message_to_send = "Machine already unwhitelisted"
        bot.send_message(message.chat.id,message_to_send)

    except Exception as e :
        print(e)
        tb_str = traceback.format_exc()
        print(f"Traceback:\n{tb_str}")
        bot.send_message(message.chat.id,"Error")

@bot.callback_query_handler(func=lambda call:True)
def handle_button(call):
    if call.data == "display_vm_by_host":
        message_to_send = VMControl.display_vm_by_machine()
        print(message_to_send)
        bot.send_message(call.message.chat.id, message_to_send)
    action, vm_name, chat_id = call.data.split(':') 
    if action == "whitelist":
        #param is vm_name
        duration = 20
        text = f"/whitelist {vm_name} {duration}"
        message =  MockMessage(text,chat_id)
        whitelist_command(message)
    if action == "unwhitelist":
        text = f"/unwhitelist {vm_name}"
        message =  MockMessage(text,chat_id)
        unwhitelist_command(message)

print("Polling...")
bot.polling(none_stop=True)
