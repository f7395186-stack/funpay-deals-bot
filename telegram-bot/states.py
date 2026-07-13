from aiogram.fsm.state import State, StatesGroup

class DealCreation(StatesGroup):
    choosing_role = State()
    choosing_currency = State()
    entering_amount = State()
    entering_description = State()

class RequisiteEdit(StatesGroup):
    editing_card = State()
    editing_crypto = State()
    editing_wallet = State()
    editing_stars = State()

class BalanceAction(StatesGroup):
    depositing = State()
    withdrawing = State()
    choosing_withdraw_currency = State()
    entering_withdraw_amount = State()
    entering_withdraw_requisite = State()

class AdminAction(StatesGroup):
    entering_credit_target = State()
    entering_credit_amount = State()
