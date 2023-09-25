from aiogram import Bot, Dispatcher, executor, types
import os
from crystalpay_sdk import CrystalPAY, PayoffSubtractFrom, InvoiceType
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



class TgBot:
    def __init__(
                        self,
                        login,
                        api_key,
                        salt,
                        token,
                        admin_id
                    ):
                    
        self.crystalpayAPI = CrystalPAY(login, api_key, salt)

        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot)

        async def start_command(message: types.Message):
            await message.answer('Вы попали в бота для заказа студенческой работы\n\nДля продолжения нажмите на кнопку:', reply_markup=InlineKeyboardMarkup().add( InlineKeyboardButton('Заполнить заявку', callback_data='start')))

        async def send_application(message:types.Message):
            application = message.text
            chat_id = message.chat.id
            await self.bot.send_message(chat_id, 'Скоро с вами свяжется администатор для согласования цены')
            await self.bot.send_message(chat_id=admin_id, text = f'Новая заявка!\n\n{application}')

        async def btns(callback:types.CallbackQuery):
            chat_id = callback.message.chat.id
            btn_data = callback.data
            message_id = callback.message.message_id
            
            if btn_data == 'start':
                await self.bot.edit_message_text('Введите ссылку на свой аккаунт телеграм и опишите работу, которую хотите заказать', chat_id, message_id)
            
            if btn_data == "check_payment":
                f = open('payment.txt',"r")
                id = f.read()
                f.close() 
                status = self.crystalpayAPI.Invoice.getinfo(id)
                if status['state'] != "notpayed":
                    await self.bot.edit_message_text('Оплата прошла успешно!', chat_id, message_id)
                    os.remove('payment.txt')
                else: 
                    await self.bot.edit_message_text('Оплата не прошла!', chat_id, message_id)
        

        async def payment(message:types.Message):
            if message.chat.id == admin_id:
                command_parts = message.text.split()

                if len(command_parts) == 3:
                    _, id, amount = command_parts
                    url = self.crystalpayAPI.Invoice.create(amount, InvoiceType.purchase,lifetime=10, description="Пополнение баланса")
                    id_payment = url['id']
                    f = open('payment.txt',"w")
                    f.write(id_payment)
                    f.close()
                    await self.bot.send_message(chat_id=id, text=f"Вам выставлен счет за предоставленые услуги на сумму: {amount} рублей, просьба оплатить",reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Оплатить', url=url['url']), (InlineKeyboardButton('Проверить оплату',callback_data='check_payment'))))
            else:
                pass
        self.dp.register_message_handler(start_command, commands=['start'])
        self.dp.register_message_handler(payment, commands=['send_payment'])
        self.dp.register_message_handler(send_application)
        self.dp.register_callback_query_handler(btns)
        
    
    def start(self):
        executor.start_polling(
                                    self.dp,
                                    skip_updates=True
                                    )      

