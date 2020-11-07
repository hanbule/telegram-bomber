from service import Service


class Benzuber(Service):
    async def run(self):
        await self.post(
            "https://app.benzuber.ru/app/1.7/auth/login", data={"phone": self.formatted_phone, "flag": "A"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Linux; U; Android 10.0; Redmi Note 6 Pro MIUI/20.8.30",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "Content-Length": "0"
            },
            timeout=self.timeout
        )
