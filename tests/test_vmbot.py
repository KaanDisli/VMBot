import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from VMBot import start_command, help_command, display_vm_by_machine_command, whitelist_command,unwhitelist_command,admin_confirm,convert_seconds_to_string_fixed,generate_vm_buttons,generate_time_buttons,handle_time,handle_display_vm_by_machine,handle_whitelist,handle_unwhitelist,handle_yes,handle_no
from VMControl import VMControl
import telebot 
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup




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
    
    @patch('VMBot.bot')
    @patch('telebot.types.InlineKeyboardMarkup')
    def test_generate_time_buttons(self,MockInlineKeyboardMarkup,mock_bot):
        mock_keyboard = MockInlineKeyboardMarkup.return_value  
        mock_message = MagicMock()
        mock_message.chat.id = 123456789
        generate_time_buttons(mock_message.chat.id ,"vm1")
        mock_bot.send_message.assert_called_with(mock_message.chat.id,"Please choose for how long you want to whitelist the machine",reply_markup=mock_keyboard)


    def test_generate_vm_buttons(self):
        mock_vm= MagicMock()
        mock_vm.name = "vm1"
        mock_dico = {mock_vm:["poweredOn","Kaan","time_interval"]}       
        expected_keyboard = InlineKeyboardMarkup()  
        mock_message = MagicMock()
        mock_message.chat.id = 123456789
        button = InlineKeyboardButton(text="vm1 , poweredOn", callback_data=f"unwhitelist:vm1:123456789")
        expected_keyboard.add(button)
        generated_keyboard = generate_vm_buttons(mock_dico,mock_message.chat.id)
        self.assertEqual(expected_keyboard.to_dict(),generated_keyboard.to_dict())


    @patch('VMBot.admin_confirm')
    @patch('telebot.types.CallbackQuery')
    def test_handle_time(self,MockCallBack,mock_admin_confirm):
        
        MockCall = MockCallBack()
        MockCall.data = "time:86400:vm1:123456789"
        handle_time(MockCall)
        mock_admin_confirm.assert_called_once_with("vm1", "86400", "123456789")

    @patch('VMBot.display_vm_by_machine_command')
    @patch('telebot.types.CallbackQuery')
    def test_handle_display_vm_by_machine(self,MockCallBack,mock_display):
        MockCall = MockCallBack()
        mock_message = MagicMock()
        mock_message.chat.id = "123456789"
        MockCall.message = mock_message
        MockCall.data  = "display_vm_by_machine"
        handle_display_vm_by_machine(MockCall)
        mock_display.assert_called_once_with(MockCall.message)

    @patch('VMBot.generate_time_buttons')
    @patch('telebot.types.CallbackQuery')
    def test_handle_whitelist(self,MockCallBack,mock_generate):
        MockCall = MockCallBack()
        MockCall.data = "whitelist:vm1:123456789"
        handle_whitelist(MockCall)
        mock_generate.assert_called_once_with("123456789","vm1")


    @patch('VMBot.MockMessage')
    @patch('VMBot.unwhitelist_command')
    @patch('telebot.types.CallbackQuery')
    def test_handle_unwhitelist(self,MockCallBack,mock_unwhitelist,MockMessage):
        MockCall = MockCallBack()
        MockCall.data = "unwhitelist:vm1:123456789"
        mock_message =  MockMessage()
        mock_message.chat.id = "123456789"
        mock_message.text = "/unwhitelist vm1"
        handle_unwhitelist(MockCall)
        mock_unwhitelist.assert_called_once_with(mock_message)


    @patch('VMBot.whitelist_command')
    @patch('VMBot.MockMessage')
    @patch('VMBot.users')
    @patch('telebot.types.CallbackQuery')
    def test_handle_yes(self,MockCallBack,mock_users,MockMessage,mock_whitelist):
        mock_users.get_username_from_chat_id.return_value = "Kaan"
        MockCall = MockCallBack()
        MockCall.data = "Yes:vm1:123456789:86400"
        text = f"/whitelist vm1 86400"
        mock_message =  MockMessage(text,"123456789")
        handle_yes(MockCall)
        mock_whitelist.assert_called_once_with(mock_message)

    @patch('VMBot.bot')
    @patch('VMBot.MockMessage')
    @patch('VMBot.users')
    @patch('telebot.types.CallbackQuery')
    def test_handle_no(self,MockCallBack,mock_users,MockMessage,mock_bot):
        mock_users.get_username_from_chat_id.return_value = "Kaan"
        MockCall = MockCallBack()
        MockCall.data = "Yes:vm1:123456789:86400"
        text = f"/whitelist vm1 86400"
        mock_message =  MockMessage(text,"123456789")
        handle_no(MockCall)
        mock_bot.send_message.assert_called_with("123456789","Sorry your request was denied by an admin")

    
"""    @patch.object(VMControl, '__init__', lambda x: None) 
    def test_change_vm_name(self,):
        vm_control_instance = VMControl()
        mock_vm= MagicMock()
        mock_vm.name = "vm1"
        new_name = "vm2"
        mock_vm.ReconfigVM_Task = MagicMock()
        vm_control_instance.update_host_vm_map  = MagicMock()
        vm_control_instance.change_vm_name(mock_vm,new_name)
        mock_vm.ReconfigVM_Task.assert_called_once()"""


if __name__ == "__main__":
    unittest.main()




