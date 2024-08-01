
import logging
import telebot 
import config
import requests
import json
import VMControl
import traceback
from pyVmomi import vim
from datetime import timedelta
from services import user_service
token = "7425220594:AAFJqNADAboDwaf77IN5cfuV1rIlYlyuPVs"


Username = "@VMBBBBot"
url = "http://127.0.0.1:5000"

bot = telebot.TeleBot(token)
users = user_service.Users()
class MockMessage:
    def __init__(self, text, chat_id ):
        self.chat = MockChat(chat_id)
        self.text = text
class MockChat:
    def __init__(self, chat_id):
        self.id = chat_id


def convert_seconds_to_string(seconds):
    time_delta = timedelta(seconds=int(seconds))
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

def convert_seconds_to_string_fixed(seconds):
    if seconds == "86400":
        return "1 day"
    elif seconds == "259200":
        return "3 days"
    elif seconds == "604800": 
        return "1 week"
    elif seconds == "1814400":
        return "3 weeks"
    else:
        return -1

def generate_time_buttons(chat_id,vm_name):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_20_seconds = telebot.types.InlineKeyboardButton(text="20 seconds", callback_data=f"time:20:{vm_name}:{chat_id}")
    button_1_day = telebot.types.InlineKeyboardButton(text="1 day", callback_data=f"time:86400:{vm_name}:{chat_id}")
    button_3_days = telebot.types.InlineKeyboardButton(text="3 days", callback_data=f"time:259200:{vm_name}:{chat_id}")
    button_1_week = telebot.types.InlineKeyboardButton(text="1 week", callback_data=f"time:604800:{vm_name}:{chat_id}")
    button_3_weeks = telebot.types.InlineKeyboardButton(text="3 weeks", callback_data=f"time:1814400:{vm_name}:{chat_id}")
    keyboard.add(button_20_seconds,button_1_day,button_3_days,button_1_week,button_3_weeks)
    bot.send_message(chat_id,"Please choose for how long you want to whitelist the machine",reply_markup=keyboard)

def generate_vm_buttons(dico,chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for vm, str in dico.items():
        powerState, User, time_interval = str 
        display_name = f"{vm.name} , {powerState}"


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
    button1 = telebot.types.InlineKeyboardButton(text="Display all machines", callback_data="display_vm_by_machine") 
    keyboard.add(button1) 
    bot.send_message(message.chat.id,"You have started the VMBot, how may I assist you today? To see how to use commands use /help ",reply_markup=keyboard)
@bot.message_handler(commands=(["help"]))

def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton('Contact us if you need any help',url="https://www.simbrella.com/"))
    bot.send_message(message.chat.id,"1- To display all hosts and machines use /display_vm_by_machine\n 2- To whitelist both machines on a host use the format /whitelist <host_name> <duration> (seconds)\n ",reply_markup=keyboard)

@bot.message_handler(commands=(["display_vm_by_machine"]))
def display_vm_by_machine_command(message):
    try:
        dico =  VMControl.get_vm_map()
        keyboard = generate_vm_buttons(dico,message.chat.id)
        bot.send_message(message.chat.id,"Click on a machine to whitelist",reply_markup=keyboard)

    except Exception as e :
        print(e)
        bot.send_message(message.chat.id,"Error")

@bot.message_handler(commands=(["whitelist"]))
####WE NEED TO MAKE SURE THIS COMMAND IS NOT ACCESSED BY USERS WITHOUT ADMIN VERIFICATION LATER
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

                if val == -1:
                    message_to_send = f"Machine name incorrect"
                elif val == -2:
                    message_to_send = f"Inappropriate duration, please choose a duration less than 3 weeks "
                else:
                    message_to_send = f"Your request was accepted! Machine {vm_name} is now whitelisted"
                   
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

def admin_confirm(vm_name,duration,chat_id_user):
    username = users.get_username_from_chat_id(chat_id_user)
    print(f"duration:{duration}")
    duration_string = convert_seconds_to_string_fixed(duration)
    log_message = f"Machine {vm_name} was requested to be whitelisted by {username} for a duration of {duration_string}"
    users.add_log(log_message)
    message_to_send_admins = f"Do you accept a whitelist request for machine {vm_name} from {username} for a duration of {duration_string} "
    keyboard_admin = telebot.types.InlineKeyboardMarkup()
    button_admin1 = telebot.types.InlineKeyboardButton(text=f"Yes", callback_data=f"Yes:{vm_name}:{chat_id_user}:{duration}")
    button_admin2 = telebot.types.InlineKeyboardButton(text="No", callback_data=f"No:{vm_name}:{chat_id_user}:{duration}")
    keyboard_admin.add(button_admin1)
    keyboard_admin.add(button_admin2)
    admin_chat_id_dico = users.get_all_admin_chat_id()
    for chat_id_admin in admin_chat_id_dico:
        bot.send_message(chat_id_admin, message_to_send_admins,reply_markup=keyboard_admin)


@bot.callback_query_handler(func=lambda call:call.data.startswith("time"))
def handle_time(call):
    time, duration, vm_name, chat_id_user = call.data.split(':')
    admin_confirm(vm_name, duration,chat_id_user)


@bot.callback_query_handler(func=lambda call:call.data.startswith("display_vm_by_machine"))
def handle_display_vm_by_machine(call):
    print("inside display_vm_by_machine callbackquery handler ")
    display_vm_by_machine_command(call.message)
    
@bot.callback_query_handler(func=lambda call:call.data.startswith("whitelist"))
def handle_whitelist(call):
    action, vm_name, chat_id_user = call.data.split(':')
    ###send all admins a request, if he confirms continue with the whitelisting
    generate_time_buttons(chat_id_user,vm_name)
    

@bot.callback_query_handler(func=lambda call:call.data.startswith("unwhitelist"))
def handle_unwhitelist(call):
    action, vm_name, chat_id_user = call.data.split(':')
    text = f"/unwhitelist {vm_name}"
    message =  MockMessage(text,chat_id_user)
    unwhitelist_command(message)

@bot.callback_query_handler(func=lambda call:call.data.startswith("Yes"))
def handle_yes(call):
    action, vm_name, chat_id_user, duration = call.data.split(':')
    admin_name = users.get_username_from_chat_id(call.message.chat.id)
    users.add_log(f"The request was accepted by admin {admin_name}")
    text = f"/whitelist {vm_name} {duration}"
    message =  MockMessage(text,chat_id_user)
    whitelist_command(message)

@bot.callback_query_handler(func=lambda call:call.data.startswith("No"))
def handle_no(call):
    admin_name = users.get_username_from_chat_id(call.message.chat.id)
    action, vm_name, chat_id_user, duration = call.data.split(':')
    users.add_log(f"The request was denied by admin {admin_name}")
    bot.send_message(chat_id_user, "Sorry your request was denied by an admin")


if __name__ == "__main__":
    try:
        VMControl = VMControl.VMControl()
        Username = "@VMBBBBot"
        url = "http://127.0.0.1:5000"
        
        print("Polling...")
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Failed to start polling: {e}")

