from service import Service

#cookie = {"__ddg1" = "WbP8lwHjtzyGgNsXlgmv"}

class Apteka(Service):
    phone_codes = [7]

    async def run(self):
        await self.post(
            "https://api.apteka.ru/auth/auth_code",
            json={'phone': "+" + self.formatted_phone, 
                 'cityId': "5e57803249af4c0001d64407"},
            timeout=self.timeout,
        )
