from typing import Dict, List, Union
from uuid import uuid4

from .account import DebitAccount, DepositAccount, CreditAccount, BankAccount
from .client import Client
from .transaction import Transaction


class Bank:
    def __init__(self,
                 name: str,
                 debit_interest_on_balance: float = 5.0,
                 deposit_interest_on_balance: Dict[int, float] = {0: 3.0, 50000: 3.5, 100000: 4.0},
                 credit_limit: int = 100000,
                 credit_fee: int = 200,
                 suspicious_client_withdrawal_limit: int = 20000,
                 suspicious_client_transfer_limit: int = 20000):
        self.id = uuid4().int
        self.name = name
        self.debit_interest_on_balance = debit_interest_on_balance
        self.deposit_interest_on_balance = deposit_interest_on_balance
        self.credit_limit = credit_limit
        self.credit_fee = credit_fee
        self.suspicious_client_withdrawal_limit = suspicious_client_withdrawal_limit
        self.suspicious_client_transfer_limit = suspicious_client_transfer_limit
        self.bank_account = BankAccount(bank=self)

        self.clients: Dict[str, Client] = dict()
        self.accounts: Dict[int, Union[DebitAccount, DepositAccount, CreditAccount, BankAccount]] = dict()
        self.accounts[self.bank_account.id] = self.bank_account
        self.clients_accounts: Dict[str, List[Union[DebitAccount, DepositAccount, CreditAccount, BankAccount]]] = dict()

    def add_client(self, client: Client) -> None:
        client_name = str(client)
        if client_name not in self.clients:
            self.clients[client_name] = client
            self.clients_accounts[client_name] = list()

    def add_account(self, account_type: str, client: Client) -> Union[DebitAccount, DepositAccount, CreditAccount]:
        match account_type:
            case 'Debit':
                account = DebitAccount(bank=self,
                                       client=client,
                                       annual_interest_on_balance=self.debit_interest_on_balance)
            case 'Deposit':
                account = DepositAccount(bank=self,
                                         client=client,
                                         annual_interest_on_balance=0)
            case 'Credit':
                account = CreditAccount(bank=self,
                                        client=client,
                                        limit=self.credit_limit,
                                        fee=self.credit_fee)

        self.accounts[account.id] = account
        self.clients_accounts[str(client)].append(account)
        return account

    def get_account(self, id: int) -> Union[DebitAccount, DepositAccount, CreditAccount]:
        if id in self.accounts:
            return self.accounts[id]

    def open_deposit_account(self, account: DepositAccount, initial_money: float, deposit_period: int) -> None:
        annual_interest_on_balance = 0
        for min_limit, interest_on_balance in self.deposit_interest_on_balance.items():
            if initial_money > min_limit:
                annual_interest_on_balance = interest_on_balance

        account.annual_interest_on_balance = annual_interest_on_balance
        account.balance = initial_money
        account.deposit_period = deposit_period

    def daily_aggregate_transactions(self) -> List[Transaction]:
        all_transactions = list()
        for account in self.accounts.values():
            transaction = account.daily_account_update()
            if transaction is not None:
                all_transactions.append(transaction)

        return all_transactions


class BankManager:
    def __init__(self):
        self.banks: Dict[int, Bank] = dict()

    def add_bank(self, bank_name: str, **kwargs) -> Bank:
        bank = Bank(name=bank_name, **kwargs)
        self.banks[bank.id] = bank
        return bank
