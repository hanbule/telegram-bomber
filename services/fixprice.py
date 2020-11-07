from service import Service


class FixPrice(Service):
    async def run(self):
        await self.post(
            "https://fix-price.ru/ajax/confirm14_phone.php",
            data={
                "register_call": "Y",
                "action": "getCode",
                "phone": "+" + self.formatted_phone,
            }, 
            timeout=self.timeout
        )