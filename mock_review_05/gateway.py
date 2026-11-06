class PaymentGateway:
    def charge(self, investor_id: int, amount, request_key: str) -> str:
        """Call external processor and return its transaction reference.

        The actual provider client is injected in production.
        """
        raise NotImplementedError
