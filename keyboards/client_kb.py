from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

registration_button = KeyboardButton('🤝Register')
kb_client_registration = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client_registration.add(registration_button)

pay_button = KeyboardButton("🧾Confirm payment")
student_info_button = KeyboardButton("💼Check balance")
kb_client_pay = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client_pay.add(pay_button).insert(student_info_button)

back_button = KeyboardButton('◀️Back')
kb_client_payments = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client_payments.add(back_button)

cancel_button = KeyboardButton('Cancel')
kb_client_cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(cancel_button)
