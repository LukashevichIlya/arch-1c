from typing import Optional


class Client:
    def __init__(self,
                 name: str,
                 surname: str,
                 address: Optional[str] = None,
                 passport_number: Optional[int] = None):
        self.name = name
        self.surname = surname
        self.address = address
        self.passport_number = passport_number
        self.is_suspicious = self.is_suspicious_client()

    def is_suspicious_client(self) -> bool:
        if self.address is None or self.passport_number is None:
            is_suspicious = True
        else:
            is_suspicious = False

        return is_suspicious

    def set_address(self, address: str) -> None:
        self.address = address

    def set_passport_number(self, passport_number: int) -> None:
        self.passport_number = passport_number

    def __str__(self):
        return f"{self.name} {self.surname}"
