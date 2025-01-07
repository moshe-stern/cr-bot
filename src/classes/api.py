BASE_URL = "https://members.centralreach.com/api/"
BASE_URL_CRX = "https://members.centralreach.com/crxapi/"


class AuthSettings:
    def __init__(self):
        self.LOAD_SETTINGS = f"{BASE_URL}?resources.loadresourceauthorizationsettings"
        self.LOAD_SETTING = f"{BASE_URL}?resources.loadresourceauthorizationsetting"
        self.DELETE = f"{BASE_URL}?resources.deleteresourceauthorizationsetting"
        self.SET_SETTING = f"{BASE_URL}?resources.setresourceauthorizationsetting"
        self.SET_GLOBAL_SETTING = f"{BASE_URL}?resources.setglobalauthorizationsettings"


class ServiceCodes:
    def __init__(self):
        self.GET = f"{BASE_URL}?resources.getservicecodes"
        self.GET_PLACES_OF_SERVICE = f"{BASE_URL_CRX}placesofservice"


class Authorization:
    def __init__(self):
        self.SET = f"{BASE_URL}?resources.setresourceauthorization"
        self.DELETE = f"{BASE_URL}?resources.deleteResourceAuthorization"
        self.LOAD_AUTHS_CODES = f"{BASE_URL}?scheduling.loadauthsandcodes"


class Schedule:
    def __init__(self):
        self.GET_EVENT = f"{BASE_URL}?scheduling.loadevent"
        self.UPDATE_EVENT = f"{BASE_URL}?scheduling.updateevent"
        self.GET_APPOINTMENTS = f"{BASE_URL}?contacts.loadcontactappointments"


class Billing:
    def __init__(self):
        self.GET = f"{BASE_URL_CRX}internal/billing/query"
        self.SET_PAYOR = f"{BASE_URL}?billingmanager.setpayor"
        self.GET_CLIENT_PAYORS = f"{BASE_URL}?billingmanager.loadclientspayors"
        self.GET_AUTH_CODES = (
            f"{BASE_URL}?billingmanager.loadprocedurecodesandauthorizations"
        )
        self.GET_TIMESHEET = f"{BASE_URL_CRX}/converted-timesheets/by-segment"
        self.PUT_TIMESHEET = f"{BASE_URL_CRX}/converted-timesheets"


class API:
    AUTH_SETTINGS = AuthSettings()
    SERVICE_CODES = ServiceCodes()
    AUTHORIZATION = Authorization()
    SCHEDULE = Schedule()
    BILLING = Billing()
