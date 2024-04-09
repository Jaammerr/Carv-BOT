class APIError(Exception):
    def __init__(self, data: dict):
        self.code = data.get("code")
        self.message = data.get("msg", "Unknown error")

    def __str__(self):
        return f"APIError: {self.code} | {self.message}"
