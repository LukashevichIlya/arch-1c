from abc import ABC, abstractmethod
from typing import Optional
from uuid import uuid4

from .client import Client
from .transaction import Transaction


class Account(ABC):
    def __init__(self, bank, client: Optional[Client]):
        self.id = uuid4().int
        self.bank = bank
        self.client = client
        self.balance = 0.

    def top_up(self, money: float) -> Transaction:
        return Transaction(from_bank_id=self.bank.id,
                           to_bank_id=self.bank.id,
                           from_account_id=self.bank.bank_account.id,
                           to_account_id=self.id,
                           money=money,
                           is_top_up=True)

    def transfer(self, money: float, to_bank, to_account_id: int) -> Transaction:
        return Transaction(from_bank_id=self.bank.id,
                           to_bank_id=to_bank.id,
                           from_account_id=self.id,
                           to_account_id=to_account_id,
                           money=money)

    def withdraw(self, money: float) -> Transaction:
        return Transaction(from_bank_id=self.bank.id,
                           to_bank_id=self.bank.id,
                           from_account_id=self.id,
                           to_account_id=self.bank.bank_account.id,
                           money=money)

    def _add_to_balance(self, money: float) -> None:
        self.balance += money

    @abstractmethod
    def _subtract_from_balance(self, money: float, force_subtract: bool = False) -> Optional[float]:
        raise NotImplementedError()

    @abstractmethod
    def daily_account_update(self) -> Optional[Transaction]:
        raise NotImplementedError()


class DebitAccount(Account):
    def __init__(self, bank, client: Optional[Client], annual_interest_on_balance: float):
        super().__init__(bank=bank, client=client)
        self.annual_interest_on_balance = annual_interest_on_balance

    def _subtract_from_balance(self, money: float, force_subtract: bool = False) -> Optional[float]:
        if force_subtract:
            self.balance -= money
            return money
        else:
            if money <= self.balance:
                self.balance -= money
                return money
            else:
                return None

    def daily_account_update(self) -> Optional[Transaction]:
        daily_earnings = (self.annual_interest_on_balance / 365 / 100) * self.balance
        return Transaction(from_bank_id=self.bank.id,
                           to_bank_id=self.bank.id,
                           from_account_id=self.bank.bank_account.id,
                           to_account_id=self.id,
                           money=daily_earnings)


class DepositAccount(Account):
    def __init__(self, bank, client: Optional[Client],
                 annual_interest_on_balance: float, deposit_period: int = 365):
        super().__init__(bank=bank, client=client)
        self.annual_interest_on_balance = annual_interest_on_balance
        self.deposit_period = deposit_period
        self.current_deposit_days = 0

    def _subtract_from_balance(self, money: float, force_subtract: bool = False) -> Optional[float]:
        if force_subtract:
            self.balance -= money
            return money
        else:
            if self.current_deposit_days < self.deposit_period:
                return None

            if money <= self.balance:
                self.balance -= money
                return money
            else:
                return None

    def daily_account_update(self) -> Optional[Transaction]:
        daily_earnings = (self.annual_interest_on_balance / 365 / 100) * self.balance
        return Transaction(from_bank_id=self.bank.id,
                           to_bank_id=self.bank.id,
                           from_account_id=self.bank.bank_account.id,
                           to_account_id=self.id,
                           money=daily_earnings)


class CreditAccount(Account):
    def __init__(self, bank, client: Optional[Client], limit: int, fee: int):
        super().__init__(bank=bank, client=client)
        self.limit = limit
        self.fee = fee

    def _subtract_from_balance(self, money: float, force_subtract: bool = False) -> Optional[float]:
        if force_subtract:
            self.balance -= money
            return money
        else:
            if money <= self.balance + self.limit:
                self.balance -= money
                return money
            else:
                return None

    def daily_account_update(self) -> Optional[Transaction]:
        if self.balance < 0:
            return Transaction(from_bank_id=self.bank.id,
                               to_bank_id=self.bank.id,
                               from_account_id=self.id,
                               to_account_id=self.bank.bank_account.id,
                               money=self.fee)


class BankAccount(Account):
    def __init__(self, bank):
        super().__init__(bank=bank, client=None)

    def _subtract_from_balance(self, money: float, force_subtract: bool = False) -> Optional[float]:
        self.balance -= money
        return money

    def daily_account_update(self) -> Optional[Transaction]:
        return None
