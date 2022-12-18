from banks.bank import BankManager
from banks.transaction import TransactionManager
from banks.client import Client

if __name__ == '__main__':
    bank_manager = BankManager()
    first_bank = bank_manager.add_bank(bank_name='First')
    second_bank = bank_manager.add_bank(bank_name='Second')

    first_bank_client = Client(name='John', surname='James')
    second_bank_client = Client(name='Mary', surname='Jones')

    first_bank.add_client(first_bank_client)
    second_bank.add_client(second_bank_client)

    transaction_manager = TransactionManager(bank_manager=bank_manager)

    first_bank_account = first_bank.add_account(account_type='Debit', client=first_bank_client)
    second_bank_account = second_bank.add_account(account_type='Deposit', client=second_bank_client)
    second_bank.open_deposit_account(account=second_bank_account, initial_money=60000, deposit_period=730)

    top_up_transaction = first_bank_account.top_up(money=50000)
    transaction_manager.execute_transaction(transaction=top_up_transaction)

    transfer_transaction = first_bank_account.transfer(money=10000,
                                                       to_bank=second_bank,
                                                       to_account_id=second_bank_account.id)
    transaction_manager.execute_transaction(transaction=transfer_transaction)

    withdraw_transaction = first_bank_account.withdraw(money=50000)
    transaction_manager.execute_transaction(transaction=withdraw_transaction)

    transaction_manager.execute_daily_transactions()
