from service import Service


class KoronoPay(Service):
    async def run(self):
        await self.post(
            "https://koronapay.com/transfers/online/api/users/otps",
            data={"phone": self.formatted_phone},
            timeout=self.timeout
        )
