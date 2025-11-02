import enum


class ImgPath(enum.Enum):
    ACTION = "/app/app/attachments/imgs/action"


class DocumentPaths(enum.Enum):
    GENERAL = "/attachments/general"


class PriorityEnum(enum.Enum):
    UNKNOWN = 5
    LOW = 4
    MEDIUM = 3
    HIGH = 2
    URGENT = 1


class SystemTypeEnum(enum.Enum):
    ACE = "ACE"
    AHM = "AHM"
    BMS_ACT = "BMS-ACT"
    BMS_CR = "BMS-CR"
    BMS_HZD = "BMS-HZD"
    BMS_ITR = "BMS_ITR"
    SMH = "SMH"
    TEAMS = "Teams"
    SAP_NOTIFICATION = "SAP Notification"
    SAP_WORK_ORDER = "SAP Work Order"
    DEP = "DEP"


class PrivacyEnum(enum.IntEnum):
    PUBLIC = 1
    CONFIDENTIAL = 3


class LinkedSystemEnum(enum.Enum):
    ACTION = 1
    SAP_NOTIFICATION = 2
    SAP_WO = 3
    AHM_OVERDUE = 4
    AHM_SIMP = 5
    AHM_ALS = 6
    AHM_TX = 7


class ActionTagEnum(enum.Enum):
    SHORT_TERM = 1
    LONG_TERM = 2
    ONLINE = 3
    SHUTDOWN = 4
    INSPECTION_ONLY = 5
    PARTS_REQUIRED = 6
    CAPITAL = 7


class StatusEnum(enum.IntEnum):
    OVERDUE = 1
    OPEN = 2
    ON_HOLD = 3
    CLOSED = 4


class Priority(enum.IntEnum):
    OPEN = 0
    ONHOLD = 1
    CLOSED = 2


class FeedbackReason(enum.IntEnum):
    BUG = 1
    GENERAL_FEEDBACK = 2


class FeedbackStatusEnum(enum.IntEnum):
    OPEN = 1
    ON_HOLD = 2
    CLOSED_COMPLETE = 3
    CLOSED_DUPLICATE = 4
    CLOSED_FEEDBACK_ONLY = 5


class ArchiveStatus(enum.IntEnum):
    Active = 1
    Archived = 2


class LogTypeEnum(enum.Enum):
    LOGIN = "Login"
    ACTION_INGESTION_SYNC = "Action_Ingestion_Sync"
    TEAMS_INGESTION_SYNC = "Teams_Ingestion_Sync"
    ACTION_CREATION = "Action_Creation"
    ACTION_UPDATE = "Action_Update"
    WORKGROUP_CREATION = "Workgroup_Creation"
    WORKGROUP_UPDATE = "Workgroup_Update"
