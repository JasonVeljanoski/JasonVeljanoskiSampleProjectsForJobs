import enum


class ImgPath(enum.Enum):
    FIVE_WHY = "/attachments/imgs/five_why"
    FLASH_REPORT = "/attachments/imgs/flash_report"
    ACTION = "/attachments/imgs/action"
    RCA = "/attachments/imgs/rca"
    SHARED_LEARNING = "/attachments/imgs/shared_learning"
    FEEDBACK = "/attachments/imgs/feedback"


class DocumentPaths(enum.Enum):
    FIVE_WHY = "/attachments/five_why"
    FLASH_REPORT = "/attachments/flash_report"
    RCA = "/attachments/rca"
    SHARED_LEARNING = "/attachments/shared_learnings"
    TEMPLATES = "/app/app/templates"
    GENERAL = "/attachments/general"


class TemplateDocNames(enum.Enum):
    FIVE_WHY = "five_why.docx"
    FLASH_REPORT = "flash_report.pptx"
    FLASH_REPORT_YES = "flash_report_yes.pptx"
    FLASH_REPORT_NO = "flash_report_no.pptx"
    RCA = "rca.docx"
    SHARED_LEARNING = "shared_learning.pptx"


class PriorityEnum(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ActionSourceEnum(enum.Enum):
    FLASH_REPORT = "Flash Report"
    FIVE_WHY = "5-Why"
    ROOT_CAUSE = "Root Cause"


class DashboardColorEnum(enum.Enum):
    BMS = "green"
    SHAREPOINT = "purple"
    TRELLO = "orange"
    TEAMS = "pink"
    OTHER = "red"


class SiteEnum(enum.Enum):
    CC = "Christmas Creek"
    SOL = "Solomon"
    CB = "Cloudbreak"
    ROP = "Rail Operation"
    ELI = "Eliwana"
    PORT = "Anderson Point"
    EO = "Energy Operations"
    IRON_BRIDGE = "Iron Bridge"
    OTHER = ""


class LogEnum(enum.Enum):
    ACTION = "Action"
    INVESTIGATION = "Investigation"
    FLASH_REPORT = "Flash Report"
    FIVE_WHY = "Five Why"
    ROOT_CAUSE = "Root Cause"
    SHARED_LEARNINGS = "Shared Learnings"


class TimeUsageCode(enum.Enum):
    OD = "OD"
    SD = "SD"
    UM = "UM"
    PL = "PL"
    SM = "SM"
    OTHER = "OTHER"


class DashboardTypeEnum(enum.Enum):
    TABLEAU = 1
    REMS = 2
    APLUS = 3


class InvestigationTypeEnum(enum.IntEnum):
    FIVE_WHY = 1
    RCA = 2
    FLASH_REPORT_ONLY = 3


class EventTypeEnum(enum.IntEnum):
    APLUS = 1
    REMS = 2


class StatusEnum(enum.IntEnum):
    OPEN = 1
    ON_HOLD = 2
    CLOSED = 3
    OVERDUE = 4


class NotificationTypeEnum(enum.IntEnum):
    INFO = 1
    SUCCESS = 2
    WARNING = 3


class ArchiveStatus(enum.IntEnum):
    Archived = 1
    Active = 2


class FeedbackReason(enum.IntEnum):
    BUG = 1
    GENERAL_FEEDBACK = 2


class FeedbackStatusEnum(enum.IntEnum):
    OPEN = 1
    ON_HOLD = 2
    CLOSED_COMPLETE = 3
    CLOSED_DUPLICATE = 4
    CLOSED_FEEDBACK_ONLY = 5
