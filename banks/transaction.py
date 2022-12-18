from enum import Enum
from typing import List

from .client import Client


class TransactionState(Enum):
    UNPERFORMED = 0
    EXECUTED = 1
    CANCELLED = 2


class Transaction:
    def __init__(self,
                 from_bank_id: int,
                 to_bank_id: int,
                 from_account_id: int,
                 to_account_id: int,
                 money: float,
                 is_top_up: bool = False):
        self.from_bank_id = from_bank_id
        self.to_bank_id = to_bank_id
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        self.money = money
        self.state = TransactionState.UNPERFORMED
        self.is_top_up = is_top_up


class TransactionManager:
    def __init__(self, bank_manager):
        self.bank_manager = bank_manager
        self.executed_transactions: List[Transaction] = list()
        self.cancelled_transactions: List[Transaction] = list()

    def execute_transaction(self, transaction: Transaction) -> None:
        if transaction.state == TransactionState.EXECUTED or transaction.state == TransactionState.CANCELLED:
            return

        banks = self.bank_manager.banks
        from_bank = banks[transaction.from_bank_id]
        from_account = from_bank.get_account(id=transaction.from_account_id)
        to_bank = banks[transaction.to_bank_id]
        to_account = to_bank.get_account(id=transaction.to_account_id)

        if (not transaction.is_top_up and
                (not self._approved_client_and_transaction_limits(from_account.client,
                                                                  transaction.money,
                                                                  from_bank.suspicious_client_withdrawal_limit,
                                                                  from_bank.suspicious_client_transfer_limit) or
                 not self._approved_client_and_transaction_limits(to_account.client,
                                                                  transaction.money,
                                                                  to_bank.suspicious_client_withdrawal_limit,
                                                                  to_bank.suspicious_client_transfer_limit))):
            transaction.state = TransactionState.CANCELLED
            self.cancelled_transactions.append(transaction)
            return

        transfer_money = from_account._subtract_from_balance(transaction.money)
        if transfer_money is not None:
            to_account._add_to_balance(transfer_money)
        else:
            transaction.state = TransactionState.CANCELLED
            self.cancelled_transactions.append(transaction)
            return

        transaction.state = TransactionState.EXECUTED
        self.executed_transactions.append(transaction)

    def cancel_transaction(self, transaction: Transaction) -> None:
        if transaction.state is not TransactionState.EXECUTED:
            return

        banks = self.bank_manager.banks
        from_bank = banks[transaction.from_bank_id]
        from_account = from_bank.get_account(id=transaction.from_account_id)
        to_bank = banks[transaction.to_bank_id]
        to_account = to_bank.get_account(id=transaction.to_account_id)

        to_account._subtract_from_balance(transaction.money, force_subtract=True)
        from_account._add_to_balance(transaction.money)
        transaction.state = TransactionState.CANCELLED
        self.cancelled_transactions.append(transaction)

    def execute_daily_transactions(self) -> None:
        for bank in self.bank_manager.banks.values():
            transactions = bank.daily_aggregate_transactions()
            for transaction in transactions:
                self.execute_transaction(transaction)

    @staticmethod
    def _approved_client_and_transaction_limits(client: Client,
                                                money: float,
                                                withdrawal_limit: int,
                                                transfer_limit: float) -> bool:
        if client is not None and client.is_suspicious and (money >= withdrawal_limit or money >= transfer_limit):
            return False
        else:
            return True
