from src.classes import UpdateKeys


class PayorUpdateKeysV2(UpdateKeys):
    insurance_company_id: int

    def __init__(self, **kwargs) -> None:
        self.insurance_company_id = kwargs.get("insurance_company_id", 0)
