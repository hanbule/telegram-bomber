from service import Service


class ModulBank(Service):
    phone_codes = [7]

    async def run(self):
        await self.post(
            "https://my.modulbank.ru/api/v2/registration/nameAndPhone",
            json={
                "FirstName": self.russian_name,
                "CellPhone": self.phone,
                "Package": "optimal",
            },
            timeout=self.timeout
        )
