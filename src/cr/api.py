BASE_URL = "https://members.centralreach.com/api/"


class AuthSettings:
    def __init__(self):
        self.LOAD_SETTINGS = f"{BASE_URL}?resources.loadresourceauthorizationsettings"
        self.LOAD_SETTING = f"{BASE_URL}?resources.loadresourceauthorizationsetting"
        self.DELETE = f"{BASE_URL}?resources.deleteresourceauthorizationsetting"
        self.SET_SETTING = f"{BASE_URL}?resources.setresourceauthorizationsetting"


class ServiceCodes:
    def __init__(self):
        self.GET = f"{BASE_URL}?resources.getservicecodes"


class Authorization:
    def __init__(self):
        self.GET = f"{BASE_URL}?resources.setresourceauthorization"


class API:
    AUTH_SETTINGS = AuthSettings()
    SERVICE_CODES = ServiceCodes()
    AUTHORIZATION = Authorization()
