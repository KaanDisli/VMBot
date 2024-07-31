import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from VMBot import start_command, help_command, display_vm_by_machine_command, whitelist_command,unwhitelist_command,admin_confirm,convert_seconds_to_string_fixed
import telebot 




#We use .return_value when we want to specify what a mocked method should return
#We use direct value assignment for mock attributes



class Test_VmBot(unittest.TestCase):
    @patch('VMBot.bot')
    @patch('telebot.types.InlineKeyboardMarkup')
    @patch('telebot.types.InlineKeyboardButton')
    def test_start_command(self, MockInlineKeyboardButton, MockInlineKeyboardMarkup, mock_bot):
        mock_message = MagicMock()
        mock_message.chat.id = 123456789
        mock_keyboard = MockInlineKeyboardMarkup.return_value
        mock_button = MockInlineKeyboardButton.return_value 
        mock_bot.send_message.return_value= None
        start_command(mock_message)
        MockInlineKeyboardMarkup.assert_called_once()
        mock_bot.send_message.assert_called_once_with(
            mock_message.chat.id,
            "You have started the VMBot, how may I assist you today? To see how to use commands use /help ",
            reply_markup=mock_keyboard
        )
        MockInlineKeyboardButton.assert_called_once_with(
            text="Display all machines",
            callback_data="display_vm_by_machine"
        )

    @patch('VMBot.bot')
    @patch('telebot.types.InlineKeyboardMarkup')
    @patch('telebot.types.InlineKeyboardButton')
    def test_help_command(self, MockInlineKeyboardButton, MockInlineKeyboardMarkup, mock_bot):
        mock_message = MagicMock()
        mock_message.chat.id = 123456789
        mock_keyboard = MockInlineKeyboardMarkup.return_value
        mock_button = MockInlineKeyboardButton.return_value 
        mock_bot.send_message.return_value= None
        help_command(mock_message)
        MockInlineKeyboardMarkup.assert_called_once()
        MockInlineKeyboardButton.assert_called_once_with(
            "Contact us if you need any help",url="https://www.simbrella.com/"
        )
        mock_bot.send_message.assert_called_once_with(
            mock_message.chat.id,
            "1- To display all hosts and machines use /display_vm_by_machine\n 2- To whitelist both machines on a host use the format /whitelist <host_name> <duration> (seconds)\n ",
            reply_markup=mock_keyboard
        )
    @patch('VMBot.bot')
    @patch("VMBot.VMControl")
    @patch('telebot.types.InlineKeyboardMarkup')
    def test_display_vm_by_machine_command(self,MockInlineKeyboardMarkup,VM_Control,mock_bot):
        mock_dico = MagicMock()
        mock_dico.return_value = {'vm1': 'Machine 1', 'vm2': 'Machine 2'}
        VM_Control.get_vm_map.return_value =mock_dico
        mock_keyboard = MockInlineKeyboardMarkup.return_value
        mock_message = MagicMock()
        mock_message.chat.id = 123456789
        display_vm_by_machine_command(mock_message)
        mock_bot.send_message.assert_called_once_with(mock_message.chat.id,"Click on a machine to whitelist",reply_markup=mock_keyboard)
    
    
    @patch('VMBot.bot')
    @patch("VMBot.VMControl")
    @patch('telebot.types.InlineKeyboardMarkup')
    def test_whitelist_command(self,MockInlineKeyboardMarkup,VM_Control,mock_bot):
        mock_keyboard = MockInlineKeyboardMarkup.return_value
        mock_message = MagicMock()
        mock_message.chat.id = 123456789
        mock_message.text = "/whitelist vm1 20"
        mock_val = MagicMock()

        #if not val
        mock_val  = False
        VM_Control.whitelist_vm_by_name.return_value = mock_val
        mock_message_to_send = "Machine already whitelisted"
        whitelist_command(mock_message)
        mock_bot.send_message.assert_called_with(
            mock_message.chat.id,
            mock_message_to_send
        )

        #if val == -1:
        mock_val = -1
        VM_Control.whitelist_vm_by_name.return_value = mock_val
        mock_message_to_send = f"Machine name incorrect"
        mock_message.text = "/whitelist vm1 20"
        whitelist_command(mock_message)
        mock_bot.send_message.assert_called_with(
            mock_message.chat.id,
            mock_message_to_send
        )

        #elif val == -2:
        mock_message_to_send = f"Inappropriate duration, please choose a duration less than 3 weeks "
        mock_val = -2
        VM_Control.whitelist_vm_by_name.return_value = mock_val
        whitelist_command(mock_message)
        mock_bot.send_message.assert_called_with(
            mock_message.chat.id,
            mock_message_to_send
        )

        #else:
        mock_vm_name = "vm1"
        mock_val = True
        VM_Control.whitelist_vm_by_name.return_value = mock_val
        mock_message_to_send = f"Your request was accepted! Machine {mock_vm_name} is now whitelisted"
        whitelist_command(mock_message)
        mock_bot.send_message.assert_called_with(
            mock_message.chat.id,
            mock_message_to_send
        )
    @patch('VMBot.bot')
    @patch("VMBot.VMControl")
    @patch('telebot.types.InlineKeyboardMarkup')
    def test_unwhitelist_command(self,MockInlineKeyboardMarkup,VM_Control,mock_bot):
        mock_keyboard = MockInlineKeyboardMarkup.return_value
        vm_name = "vm1"
        mock_message = MagicMock()
        mock_message.chat.id = 123456789
        mock_message.text = "/unwhitelist vm1"

        #if val == -1:
        VM_Control.unwhitelist_vm_by_name.return_value = -1
        mock_message_to_send = f"Machine name incorrect"
        unwhitelist_command(mock_message)
        mock_bot.send_message.assert_called_with(
            mock_message.chat.id,
            mock_message_to_send
        )
        #else:
        VM_Control.unwhitelist_vm_by_name.return_value = True
        mock_message_to_send = f"Machine {vm_name} is now unwhitelisted"
        unwhitelist_command(mock_message)
        mock_bot.send_message.assert_called_with(
            mock_message.chat.id,
            mock_message_to_send
        )
        #false
        VM_Control.unwhitelist_vm_by_name.return_value = False
        mock_message_to_send = "Machine already unwhitelisted"
        unwhitelist_command(mock_message)
        mock_bot.send_message.assert_called_with(
            mock_message.chat.id,
            mock_message_to_send
        )

    @patch('VMBot.bot')
    @patch("VMBot.VMControl")
    @patch('telebot.types.InlineKeyboardMarkup')
    @patch('VMBot.users')
    def test_admin_confirm(self,mock_users,MockInlineKeyboardMarkup,VM_Control,mock_bot):
        
        mock_users.get_username_from_chat_id.return_value =  "mock_username" 
        mock_duration = 86400
        mock_duration_string =convert_seconds_to_string_fixed(mock_duration)
        mock_keyboard = MockInlineKeyboardMarkup.return_value
        
        mock_message_admin = MagicMock()
        mock_message_admin.chat.id = 123456789
        mock_message_user = MagicMock()
        mock_message_user.chat.id = 123456780

        mock_vm_name = "vm1"
        mock_username = mock_users.get_username_from_chat_id.return_value
        mock_message_to_send_admins = f"Do you accept a whitelist request for machine {mock_vm_name} from {mock_username} for a duration of {mock_duration_string} "
        mock_users.get_all_admin_chat_id.return_value = {mock_message_admin.chat.id}
        admin_confirm("vm1",mock_duration,mock_message_user.chat.id)

        mock_bot.send_message.assert_called_with(mock_message_admin.chat.id, mock_message_to_send_admins,reply_markup=mock_keyboard)

if __name__ == "__main__":
    unittest.main()




