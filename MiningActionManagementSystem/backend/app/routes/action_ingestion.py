import base64
import csv
import datetime as dt
import json
import time
import urllib
import uuid
from importlib.metadata import metadata
from urllib import response
from urllib.parse import urlencode

import pytz
import requests
from app import config, crud, models, schemas, utils
from app.models.base import Base
from app.schemas import Priority, PriorityEnum, PrivacyEnum, StatusEnum
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import parse_obj_as
from pydantic.dataclasses import dataclass
from sqlalchemy import select

router = APIRouter()
utc = pytz.UTC

# ---------------------------------------------------------------------------------------------

# METADATA CLASSES - Metadata for differet source types
@dataclass
class Metadata_Sap_Notification:
    notification_type: str
    system_status: str
    user_status: str

    def __init__(self, notificationType, systemStatus, userStatus):
        self.notification_type = notificationType
        self.system_status = systemStatus
        self.user_status = userStatus


@dataclass
class Metadata_Legacy_Ace:
    created_by: str
    last_updated_by: str

    def __init__(self, createdBy, lastUpdatedBy):
        self.created_by = createdBy
        self.last_updated_by = lastUpdatedBy


@dataclass
class Metadata_BMS:
    discipline: str
    category: str
    location: str

    def __init__(self, discipline, category, location):
        self.discipline = discipline
        self.category = category
        self.location = location


@dataclass
class Metadata_Sap_WO:
    order_type: str
    system_status: str
    user_status: str
    notification_number: str
    group: str

    def __init__(self, orderType, systemStatus, userStatus, notificationNumber, group):
        self.order_type = orderType
        self.system_status = systemStatus
        self.user_status = userStatus
        self.notification_number = notificationNumber
        self.group = group


@dataclass
class Metadata_SMH:
    classification: str
    last_comments: str

    def __init__(self, classification, lastComments):
        self.classification = classification
        self.last_comments = lastComments


@dataclass
class Metadata_AHM:
    notification_number: str
    asset_id: str
    equipment_description: str
    object_type: str
    technology: str

    def __init__(self, notificationNumber, assetId, equipmentDescription, objectType, technology):
        self.notification_number = notificationNumber
        self.asset_id = assetId
        self.equipment_description = equipmentDescription
        self.object_type = objectType
        self.technology = technology


# ---------------------------------------------------------------------------------------------


@router.get("/legacy-ace-actions")
async def get_legacy_ace_actions(
    db=Depends(utils.get_db), valid=Depends(utils.token_auth), text_file_source=True
):

    # DELETE ALL ACTION RECORDS + WORKGROUP RECORDS FIRST
    # crud.workgroup.delete_all(db)
    # crud.ace_action.delete_all(db)

    json_file_name_workgroups = "/app/app/ingest/prod_workgroups_json.txt"
    json_file_name_actions = "/app/app/ingest/prod_actions_json.txt"

    # Workgroup ingest
    class Workgroup(Base):
        id: int
        created: dt.datetime = None  # Source Created
        updated: dt.datetime = None  # Source Updated
        title: str = None  # title
        description: str = None  # description
        functional_location: str = None  # functional_location
        closed: bool = None
        date_closed: dt.datetime = None
        is_confidential: bool = None
        privacy_rating: int = None
        is_archived: bool = None
        archived_by: str = None
        updated_by: str = None
        owner_ids: list[str] = None
        admin_ids: list[str] = None
        action_ids: list[int] = None

    # Ingest WORKGROUPS
    if text_file_source:
        with open(json_file_name_workgroups) as f:
            data = json.load(f)
    else:
        ace_url = "https://ace.fmgl.com.au/api/workgroup/all_ingest"
        response = requests.get(ace_url, verify=False)
        data = response.json()

    items = parse_obj_as(list[Workgroup], data)

    # Set workgroup owners to certain preson
    workgroup_owner_user = crud.user.get_kw_single(db, email="relrington@fmgl.com.au")
    workgroup_owner_user_id = workgroup_owner_user.id

    workgroup_originalId_newId = {}
    for item in items:
        workgroup = crud.workgroup.create(db, schemas.Workgroup())
        workgroup_originalId_newId[item.id] = workgroup.id

        workgroup.title = item.title
        workgroup.description = item.description
        workgroup.functional_location = item.functional_location
        workgroup.owner_id = workgroup_owner_user_id

        if item.is_archived:
            workgroup.is_archived = item.is_archived
            archived_by_user = crud.user.get_kw_single(db, email=item.archived_by)
            if archived_by_user:
                workgroup.archive_user_id = archived_by_user.id

        if not item.is_active:
            workgroup.is_active = item.is_active

        # workgroup.privacy = item.privacy_rating
        db.commit()
        # Workgroup Admin Association (from owner ids)
        for owner in item.owner_ids:
            owner_user = crud.user.get_kw_single(db, email=owner)
            w_a_a = crud.workgroup_admin_association.create(
                db, schemas.Workgroup_Admin_Association()
            )
            w_a_a.workgroup_id = workgroup.id
            w_a_a.user_id = owner_user.id if owner_user else None

        # Workgroup Member Association (from admin ids)
        for admin in item.admin_ids:
            admin_user = crud.user.get_kw_single(db, email=admin)
            w_m_a = crud.workgroup_member_association.create(
                db, schemas.Workgroup_Member_Association()
            )
            w_m_a.workgroup_id = workgroup.id
            w_m_a.user_id = admin_user.id if admin_user else None

        db.commit()

    # Actions
    class Owners_Object(Base):
        id: int
        created: dt.datetime = None
        updated: dt.datetime = None
        action_id: int = None
        user_email: str = None

    class Comments_Object(Base):
        id: int
        created: dt.datetime = None
        updated: dt.datetime = None
        action_id: int = None
        user_id: int = None
        comment: str = None
        fullname: str = None
        user_email: str = None

    class Legacy_ACE_Action(Base):
        id: int
        created: dt.datetime = None  # Source Created
        updated: dt.datetime = None  # Source Updated
        title: str = None  # title
        description: str = None  # description
        function_location: str = None  # functional_location
        priority: int = None  # priority get_priority
        start_date: dt.datetime = None  # start_date
        date_due: dt.datetime = None  # date_due
        supervisor_user_email: str = None  # supervisor_id MAPPED
        completion: int = None  # completed
        action_status: str = None  # status get_status
        action_tag: str = None  # NOT USED
        date_closed: dt.datetime = None  # date_closed
        linked_system: str = None  # NOT USED
        linked_system_event_id: str = None  # NOT USED
        created_by: str = None  # metadata
        last_updated_by: str = None  # metadata
        workgroup_id: int = None
        is_confidential: bool = None  # privacy MAPPED
        is_archived: bool = None  # is_archived
        archived_by: str = None  # archive_user_id MAPPED

        comments: list[Comments_Object] = None  # comment objects
        owners: list[Owners_Object] = None  # Action_Member_Association (members)

    if text_file_source:
        with open(json_file_name_actions) as f:
            data = json.load(f)
    else:
        ace_url = "https://ace.fmgl.com.au/api/action/all_admin_ingest"
        response = requests.get(ace_url, verify=False)
        data = response.json()

    items = parse_obj_as(list[Legacy_ACE_Action], data)

    # Build Action objects
    def get_priority(priorityInt: int):
        if priorityInt == 2:
            return PriorityEnum.LOW
        if priorityInt == 1:
            return PriorityEnum.MEDIUM
        if priorityInt == 0:
            return PriorityEnum.HIGH

        return PriorityEnum.UNKNOWN

    def get_status(actionStatus: str):
        if actionStatus == "0":
            return StatusEnum.OPEN
        if actionStatus == "1":
            return StatusEnum.ON_HOLD
        if actionStatus == "2":
            return StatusEnum.CLOSED

        return None

    ids = [item.id for item in items]

    for item in items:
        action = crud.ace_action.get_create(db, source_id=str(item.id))

        """
        # only update if the source has been updated
        ingested_source_updated = item.updated.replace(tzinfo=utc) if item.updated else None
        current_source_updated = (
            action.source_updated.replace(tzinfo=utc) if action.source_updated else None
        )

        if (
            current_source_updated
            and ingested_source_updated
            and current_source_updated >= ingested_source_updated
        ):
            continue
        """

        action.source_created = item.created
        action.source_updated = item.updated
        action.title = item.title
        action.description = item.description
        action.functional_location = item.function_location
        action.priority = get_priority(item.priority)
        action.status = get_status(item.action_status)
        action.start_date = item.start_date
        action.date_due = item.date_due
        action.date_closed = item.date_closed

        # Supervisor_id (from supervisor_user_email)
        supervisor = None
        if item.supervisor_user_email:
            supervisor = crud.user.get_kw_single(db, email=item.supervisor_user_email)
            action.supervisor_id = supervisor.id if supervisor else None

        action.completed = item.completion
        action.is_archived = item.is_archived
        # archive_user_id (from archived_by)
        if item.archived_by:
            archived_by_user = crud.user.get_kw_single(db, email=item.archived_by)
            if archived_by_user:
                action.archive_user_id = archived_by_user.id

        if item.is_confidential == True:
            action.privacy = PrivacyEnum.CONFIDENTIAL
        else:
            action.privacy = PrivacyEnum.PUBLIC

        # metadata (created_by, last_updated_by)
        metadata_object = Metadata_Legacy_Ace(item.created_by, item.last_updated_by)
        action.action_metadata = metadata_object.__dict__

        # Comments
        for comment in item.comments:
            a_comment = crud.action_comment.get_create(db, action_id=action.id)
            comment_user = crud.user.get_kw_single(db, email=comment.user_email)
            a_comment.created = comment.created
            a_comment.updated = comment.updated
            if comment_user:
                a_comment.user_id = comment_user.id
            a_comment.comment = comment.comment
            a_comment.type = "Action"

        # Action_Member_Association's from owners
        member_users = []

        for owner in item.owners:
            user = crud.user.get_kw_single(db, email=owner.user_email)
            if user:
                member_users.append(user)

        action.members = member_users

        if item.workgroup_id:
            workgroups = []
            wkgp = crud.workgroup.get_kw_single(
                db, id=workgroup_originalId_newId[item.workgroup_id]
            )
            workgroups.append(wkgp)
            action.workgroups = workgroups

        db.commit()

        # workgroup_id ====================== fk link
    db.commit()


@router.get("/bms")
async def bms(
    syncUUID,
    db=Depends(utils.get_db),
    sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    slidingWindow = True

    class BMS_Action(Base):
        # common fields
        bms_action_id: str  # source_id
        BMS_Type: str = None  # type
        action_title: str = None  # title
        detailed_description: str = None  # description

        criticality: str = None  # priority *
        Status: str = None  # status *
        link: str = None  # link *
        EffectiveFromDate: dt.datetime = None  # source_updated *
        date_raised: dt.datetime = None  # start_date *
        due_date: dt.datetime = None  # date_due *
        employee_email: str = None  # owner_email *
        supervisor_email: str = None  # supervisor_email *
        TeamEmail: str = None  # member_emails *

        # metadata fields
        discipline: str = None  # meta_discipline *
        category: str = None  # meta_category *
        location: str = None  # meta_location *

    # Get record with latest source_updated for each type
    # So in SF queries can get only new records
    if slidingWindow:
        query_result_bms_act = (
            db.query(schemas.BMS_ACT_Action)
            .order_by(schemas.BMS_ACT_Action.source_updated.desc())
            .limit(1)
            .all()
        )
        latest_source_updated_act = (
            str(query_result_bms_act[0].source_updated.date())
            if len(query_result_bms_act) > 0
            else None
        )

        query_result_bms_hzd = (
            db.query(schemas.BMS_HZD_Action)
            .order_by(schemas.BMS_HZD_Action.source_updated.desc())
            .limit(1)
            .all()
        )
        latest_source_updated_hzd = (
            str(query_result_bms_hzd[0].source_updated.date())
            if len(query_result_bms_hzd) > 0
            else None
        )

        query_result_bms_cr = (
            db.query(schemas.BMS_CR_Action)
            .order_by(schemas.BMS_CR_Action.source_updated.desc())
            .limit(1)
            .all()
        )
        latest_source_updated_cr = (
            str(query_result_bms_cr[0].source_updated.date())
            if len(query_result_bms_cr) > 0
            else None
        )

        query_result_bms_itr = (
            db.query(schemas.BMS_ITR_Action)
            .order_by(schemas.BMS_ITR_Action.source_updated.desc())
            .limit(1)
            .all()
        )
        latest_source_updated_itr = (
            str(query_result_bms_itr[0].source_updated.date())
            if len(query_result_bms_itr) > 0
            else None
        )

    sql = """
             With "FLocation" ("Location", "FLOC")
                as
                (
                Select distinct  "Location",
                    Case 
                        When charindex('CB - OPF - Crusher', "Location") > 0 Then 'CLB-PP-CRSH'
                        When charindex('CB - OPF - Desand', "Location") > 0 Then 'CLB-PP-DSND'
                        When charindex('CB - OPF - In Feed', "Location") > 0 Then 'CLB-PP-RMIN'
                        When charindex('CB - OPF - Infeed', "Location") > 0 Then 'CLB-PP-RMIN'
                        When charindex('CB - OPF - Screen', "Location") > 0 Then 'CLB-PP-SSCR'        
                        When charindex('CB - OPF - Stockpile', "Location") > 0 Then 'CLB-PP-TRLO'
                        When charindex('CB - OPF -  Train Load Out', "Location") > 0 Then 'CLB-PP-TRLO'
                        When charindex('CB - OPF - Wet Front End', "Location") > 0 Then 'CLB-PP-WSCR'
                        When charindex('CB - OPF', "Location") > 0 Then 'CLB-PP'
                        
                        When charindex('CC - OPF1', "Location") > 0 Then 'CLB-P1'
                        When charindex('CC - OPF2', "Location") > 0 Then 'CLB-P2'
                        
                        When charindex('EW - OPF', "Location") > 0 Then 'ELW-P1'
                        When charindex('EW - Stockyards', "Location") > 0 Then 'ELW-SY'
                        When charindex('EW - Train Load Out', "Location") > 0 Then 'ELW-SY-TRLO'
                        When charindex('EW - Primary Crushing', "Location") > 0 Then 'ELW-P1-RMIN'
                        
                        //When charindex('IB - Ore Processing Facility', "Location") > 0 Then 'IBO-P1-RMIN'
                        
                        When charindex('Sol - Firetail OPF', "Location") > 0 Then 'SOL-FT'
                        When charindex('Sol - Firetail Crushing Hub', "Location") > 0 Then 'SOL-FT-CRSH'
                        When charindex('Sol - Trainloader', "Location") > 0 Then 'SOL-SY-TRLO'
                        When charindex('Sol - Kings OPF', "Location") > 0 Then 'SOL-KV'
                        When charindex('Sol - Kings Crushing Hub A', "Location") > 0 Then 'SOL-KV-CRSH'
                        When charindex('Sol - Kings Crushing Hub B', "Location") > 0 Then 'SOL-KV-CRSH'
                        When charindex('Sol - Stockyards', "Location") > 0 Then 'SOL-SY'
                        
                        When charindex('Anderson Point Port', "Location") > 0 Then 'APT'
                        When charindex('Port - Inloading', "Location") > 0 Then 'APT-IL'
                        When charindex('Port - RC701', "Location") > 0 Then 'APT-OL-RCLM-RC701'
                        When charindex('Port - RC702', "Location") > 0 Then 'APT-OL-RCLM-RC702'
                        When charindex('Port - RC703', "Location") > 0 Then 'APT-OL-RCLM-RC703'
                        When charindex('Port - SK701', "Location") > 0 Then 'APT-IL-STKG-SK701'
                        When charindex('Port - SK702', "Location") > 0 Then 'APT-IL-STKG-SK702'
                        When charindex('Port - SK704', "Location") > 0 Then 'APT-IL-STKG-SK704'
                        When charindex('Port - SK705', "Location") > 0 Then 'APT-IL-STKG-SK705'
                        When charindex('Port - SL701', "Location") > 0 Then 'APT-IL-STKG-SL701'
                        When charindex('Port - SL702', "Location") > 0 Then 'APT-IL-STKG-SL702'
                        When charindex('Port - SL703', "Location") > 0 Then 'APT-IL-STKG-SL703'
                        When charindex('Port - SS903', "Location") > 0 Then 'APT-IL-STKG-SS903'
                        When charindex('Port - SS944', "Location") > 0 Then 'APT-IL-STKG-SS944'
                        When charindex('Port - SS945', "Location") > 0 Then 'APT-IL-STKG-SS945'
                        When charindex('Port - TS901', "Location") > 0 Then 'APT-IL-STKG-TS901'
                        When charindex('Port - TS902', "Location") > 0 Then 'APT-IL-STKG-TS902'
                        When charindex('Port - TS903', "Location") > 0 Then 'APT-IL-STKG-TS903'
                        When charindex('Port - TS904', "Location") > 0 Then 'APT-IL-STKG-TS904'
                        When charindex('Port - TS905', "Location") > 0 Then 'APT-IL-STKG-TS905'
                        When charindex('Port - TS906', "Location") > 0 Then 'APT-IL-STKG-TS906'
                        When charindex('Port - TS908', "Location") > 0 Then 'APT-IL-STKG-TS908'
                        When charindex('Port - TS914', "Location") > 0 Then 'APT-IL-STKG-TS914'
                        When charindex('Port - TS917', "Location") > 0 Then 'APT-IL-STKG-TS917'
                        When charindex('Port - TS944', "Location") > 0 Then 'APT-IL-STKG-TS944'
                        When charindex('Port - TS945', "Location") > 0 Then 'APT-IL-STKG-TS945'
                        When charindex('Port - TS950', "Location") > 0 Then 'APT-IL-STKG-TS950'
                        When charindex('Port - TS951', "Location") > 0 Then 'APT-IL-STKG-TS951'
                        When charindex('Port - TS954', "Location") > 0 Then 'APT-IL-STKG-TS954'
                        When charindex('Port - TU601', "Location") > 0 Then 'APT-IL-STKG-TU601'
                        When charindex('Port - TU602', "Location") > 0 Then 'APT-IL-STKG-TU602'
                        When charindex('Port - TU603', "Location") > 0 Then 'APT-IL-STKG-TU603'
                        When charindex('Port - CV901', "Location") > 0 Then 'APT-IL-STKG-CV901'
                        When charindex('Port - CV903', "Location") > 0 Then 'APT-IL-STKG-CV903'
                        When charindex('Port - CV905', "Location") > 0 Then 'APT-IL-STKG-CV905'
                        When charindex('Port - CV906', "Location") > 0 Then 'APT-IL-STKG-CV906'
                        When charindex('Port - CV908', "Location") > 0 Then 'APT-IL-STKG-CV908'
                        When charindex('Port - CV911', "Location") > 0 Then 'APT-IL-STKG-CV911'
                        When charindex('Port - CV912', "Location") > 0 Then 'APT-IL-STKG-CV912'
                        When charindex('Port - CV913', "Location") > 0 Then 'APT-IL-STKG-CV913'
                        When charindex('Port - CV914', "Location") > 0 Then 'APT-IL-STKG-CV914'
                        When charindex('Port - CV915', "Location") > 0 Then 'APT-IL-STKG-CV915'
                        When charindex('Port - CV916', "Location") > 0 Then 'APT-IL-STKG-CV916'
                        When charindex('Port - CV917', "Location") > 0 Then 'APT-IL-STKG-CV917'
                        When charindex('Port - CV921', "Location") > 0 Then 'APT-IL-STKG-CV921'
                        When charindex('Port - CV922', "Location") > 0 Then 'APT-IL-STKG-CV922'
                        When charindex('Port - CV927', "Location") > 0 Then 'APT-IL-STKG-CV927'
                        When charindex('Port - CV932', "Location") > 0 Then 'APT-IL-STKG-CV932'
                        When charindex('Port - CV944', "Location") > 0 Then 'APT-IL-STKG-CV944'
                        When charindex('Port - CV945', "Location") > 0 Then 'APT-IL-STKG-CV945'
                        When charindex('Port - CV948', "Location") > 0 Then 'APT-IL-STKG-CV948'
                        When charindex('Port - CV950', "Location") > 0 Then 'APT-IL-STKG-CV950'
                        When charindex('Port - CV951', "Location") > 0 Then 'APT-IL-STKG-CV951'
                        When charindex('Port - CV953', "Location") > 0 Then 'APT-IL-STKG-CV953'
                        When charindex('Port - CV968', "Location") > 0 Then 'APT-IL-STKG-CV968'
                        
                        Else "Location"
                    End FLOC
                From "EDW"."SELFSERVICE"."Location"
                )
            --/* 

                SELECT
                    'BMS-ACT' as "BMS_Type",
                    concat("Action_BK",'_', "Employee_BK") as "bms_action_id",
                    "Title" as "action_title",
                    "Action"."DetailedDescription" as "detailed_description",
                    "DateRaised" as "date_raised",
                    "DueDate" as "due_date",
                    "employee_email",
                    "supervisor_email",
                    "Incident"."BriefDescription" as "incident_title",
                    "Criticality" as "criticality",
                    "Discipline" as "discipline",
                    "Category" as "category",
                    ifnull("FLocation"."FLOC","Action"."Location") as "location",
                    "CompletionDate",
                    "Action"."Status",
                    Concat('https://bms.fmgl.com.au/NetForms/#/view/Actions/', "Action_BK") as "link",
                    "EffectiveFromDate",
                    "TeamMembers",
                    "TeamEmail"
                FROM "EDW"."SELFSERVICE"."Action_History" as "Action"
                    INNER JOIN (
                        --this adds redundancy for null email
                        SELECT
                            E1."Employee_BK",
                            lower(
                                CASE
                                    WHEN E1."Email" IS NULL THEN E2."Email"
                                    ELSE E1."Email"
                                END
                            ) as "employee_email",
                            E2."Email" as "supervisor_email"
                        FROM
                            "EDW"."SELFSERVICE"."Employee" E1
                            INNER JOIN "EDW"."SELFSERVICE"."Employee" E2 ON E1."Key_Employee_Supervisor" = E2."Employee_BK"
                        WHERE  e1."BasisOfEmployment" = 'Full-Time'
                        and e2."BasisOfEmployment" = 'Full-Time'
                        and e1."PositionStatus" = 'Current'
                        and e2."PositionStatus" = 'Current'
                    ) "email_lookup" --end redundancy
                    ON "email_lookup"."Employee_BK" = "Action"."Key_Employee_Responsible"
                    
                    LEFT OUTER JOIN "FLocation" ON "FLocation"."Location" = "Action"."Location"
                    LEFT OUTER JOIN "EDW"."SELFSERVICE"."Incident" ON "Action"."Key_Incident" = "Incident"."Incident_BK"
                    
                    LEFT OUTER JOIN 
                                    (Select "Key_Action", listagg(Concat(ifnull("PreferredName", "FirstName"), ' ', "LastName"), ',') "TeamMembers", listagg("Email", ',') "TeamEmail"
                                    from EDW.SELFSERVICE."DA_HEALTHANDSAFETY_Action_to_TeamMember"as TM
                                        INNER JOIN EDW.SELFSERVICE."Employee" as E 
                                                ON TM."Key_Employee" = E."Employee_BK"
                                    
                                        GROUP BY "Key_Action") as TM ON TM."Key_Action" = "Action"."Action_BK"
                WHERE
                    "Action"."Status" != 'Closed'
                    AND "EffectiveToDate" = '9999-12-31'
                    AND "Action"."DeletionFlag" = 'No'
                    """
    if slidingWindow and latest_source_updated_act != None:
        sql = sql + f""" and "Action"."EffectiveFromDate" > '{latest_source_updated_act}'"""
    sql = (
        sql
        + """
                    
                UNION ALL
                // HAZARD
                SELECT 
                    'BMS-HZD' as "BMS_Type",
                    concat("Hazard_BK",'_', e."Employee_BK") as "bms_action_id",
                    "BriefDescription" as "action_title",
                    "Hazard"."DetailedDescription" as "detailed_description",
                    "HazardReportedDate" as "date_raised",
                    NULL as "due_date",
                    ifnull(e."Email",s."Email") as "employee_email",
                    s."Email" as "supervisor_email",
                    "RecommendedCorrectiveAction" as "incident_title",
                    "RiskRating" as "criticality",
                    "HazardType" as "discipline",
                    "Discipline" as "category",
                    ifnull("FLocation"."FLOC","Hazard"."Location") as "location",
                    "SignOffDate",
                    "Status",
                    Concat('https://bms.fmgl.com.au/NetForms/#/view/Hazard-Register/', "Hazard_BK") as "link",
                    "EffectiveFromDate",
                    NULL as "TeamMembers",
                    NULL as "TeamEmail"
                    FROM "EDW"."SELFSERVICE"."Hazard_History" as "Hazard" 
                    LEFT OUTER JOIN "FLocation" ON "FLocation"."Location" = "Hazard"."Location"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" e ON "Key_Employee_HazardOwner" = e."Employee_BK"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" s ON e."Key_Employee_Supervisor" = s."Employee_BK"     
                
                WHERE
                    "EffectiveToDate" = '9999-12-31'
                    AND "Hazard"."Status" = 'Open'
                    --AND "Hazard_BK" = 'HAZ-374217'
                    """
    )
    if slidingWindow and latest_source_updated_hzd != None:
        sql = sql + f""" AND "EffectiveFromDate" > '{latest_source_updated_hzd}'"""
    sql = (
        sql
        + """
                    
                UNION ALL
                --*/
                // CHANGE REQUEST REVIEW
                SELECT 
                    'BMS-CR' as "BMS_Type",
                    concat("ChangeRequest_BK",'_', e."Employee_BK") as "bms_action_id",
                    Concat('CR Review: ',"TitleofChangeRequest") as "action_title",
                    "DescribetheProposedChange" as "detailed_description",
                    "ApplicationDate" as "date_raised",
                    "StakeholderChangeReviewDueDate" as "due_date",
                    ifnull(e."Email",s."Email") as "employee_email",
                    s."Email" as "supervisor_email",
                    null as "incident_title",
                    Case 
                        when "StakeholderChangeReviewDueDate" > current_date() + 30 then 'Low'
                        when "StakeholderChangeReviewDueDate" > current_date() + 7 then 'Medium'
                        when "StakeholderChangeReviewDueDate" >= current_date() then 'High'
                        when "StakeholderChangeReviewDueDate" < current_date() then 'Urgent'
                    End as "criticality",
                    "ChangeOf" as "discipline",
                    "ChangeTrigger" as "category",
                    ifnull("FLocation"."FLOC",l."Location") as "location",
                    "StakeholderChangeReviewDueDate",
                    case when "StakeholderChangeReviewDueDate" >  current_date() + 1 then 'Open' else 'Overdue' end as "Status",
                    Concat('https://bms.fmgl.com.au/NetForms/#/view/Change-Request/', "ChangeRequest_BK") as "link",
                    CRR."EffectiveFromDate",
                    null as "TeamMembers",
                    null as "TeamEmail"
                FROM "EDW"."SELFSERVICE"."ChangeRequest_History" as "CR" 
                    INNER JOIN "EDW"."SELFSERVICE"."ChangeRequestReview_History" as "CRR" ON CR."ChangeRequest_BK" = CRR."Key_ChangeRequest"
                    INNER JOIN "EDW"."SELFSERVICE"."Location" l ON l."Location_BK" = CR."Key_Location"
                    LEFT OUTER JOIN "FLocation" ON "FLocation"."Location" = l."Location"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" e ON "Key_Employee_ChangeReviewer" = e."Employee_BK"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" s ON e."Key_Employee_Supervisor" = s."Employee_BK"    
                
                WHERE
                    CRR."EffectiveToDate" = '9999-12-31'
                    AND CR."EffectiveToDate" = '9999-12-31'
                    AND CRR."ReviewStatus" = 'Undefined'
                    AND "AuthorisationFinalReviewDate" is null
                    and s."BasisOfEmployment" = 'Full-Time'
                    and e."BasisOfEmployment" = 'Full-Time'
                    and e."PositionStatus" = 'Current'
                    and e."PositionStatus" = 'Current'
                    and CR."CanthisChangebeclosedFlag" = 0
                    and CR."AuthorisationStatus" = 'Undefined'
                    """
    )
    if slidingWindow and latest_source_updated_cr != None:
        sql = sql + f""" AND CRR."EffectiveFromDate" > '{latest_source_updated_cr}'"""
    sql = (
        sql
        + """
                    

                UNION ALL
                // CHANGE REQUEST APPROVAL
                SELECT 
                    'BMS-CR' as "BMS_Type", 
                    concat("ChangeRequest_BK",'_', e."Employee_BK") as "bms_action_id",
                    Concat('CR Approval: ',"TitleofChangeRequest") as "action_title",
                    "DescribetheProposedChange" as "detailed_description",
                    "ApplicationDate" as "date_raised",
                    "StakeholderChangeReviewDueDate" as "due_date",
                    ifnull(e."Email",s."Email") as "employee_email",
                    s."Email" as "supervisor_email",
                    null as "incident_title",
                    Case 
                        when "StakeholderChangeReviewDueDate" > current_date() + 30 then 'Low'
                        when "StakeholderChangeReviewDueDate" > current_date() + 7 then 'Medium'
                        when "StakeholderChangeReviewDueDate" >= current_date() then 'High'
                        when "StakeholderChangeReviewDueDate" < current_date() then 'Urgent'
                    End as "criticality",
                    "ChangeOf" as "discipline",
                    "ChangeTrigger" as "category",
                    ifnull("FLocation"."FLOC", l."Location") as "location",
                    "ReviewDate",
                    case when "ReviewDate" >  current_date() + 1 then 'Open' else 'Overdue' end as "Status",
                    Concat('https://bms.fmgl.com.au/NetForms/#/view/Change-Request/', "ChangeRequest_BK") as "link",
                    CR."EffectiveFromDate",
                    null as "TeamMembers",
                    null as "TeamEmail"
                    
                FROM "EDW"."SELFSERVICE"."ChangeRequest_History" as "CR" 
                    INNER JOIN "EDW"."SELFSERVICE"."Location" l ON l."Location_BK" = CR."Key_Location"
                    LEFT OUTER JOIN "FLocation" ON "FLocation"."Location" = l."Location"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" e ON "Key_Employee_ChangeAuthoriserCRSS" = e."Employee_BK"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" s ON e."Key_Employee_Supervisor" = s."Employee_BK"    
                    LEFT OUTER JOIN (Select CRR."Key_ChangeRequest"
                                        from "EDW"."SELFSERVICE"."ChangeRequestReview_History" as "CRR" 
                                        WHERE IFNULL(CRR."ReviewStatus", 'Undefined') = 'Undefined' 
                                        and CRR."EffectiveToDate" = '9999-12-31'
                                        Group By CRR."Key_ChangeRequest") as Review 
                                        on Review."Key_ChangeRequest" = CR."ChangeRequest_BK"
                    
                
                WHERE 1 = 1
                    and CR."EffectiveToDate" = '9999-12-31'
                    and CR."AuthorisationStatus" = 'Undefined'
                    and s."BasisOfEmployment" = 'Full-Time'
                    and e."BasisOfEmployment" = 'Full-Time'
                    and s."PositionStatus" = 'Current'
                    and e."PositionStatus" = 'Current'
                    and CR."CanthisChangebeclosedFlag" = 0
                    AND Review."Key_ChangeRequest" IS NULL
                    and "SelectifreadytosubmittoStakeholders" = 1
                    """
    )
    if slidingWindow and latest_source_updated_cr != None:
        sql = sql + f""" AND CR."EffectiveFromDate" > '{latest_source_updated_cr}'"""
    sql = (
        sql
        + """

                GROUP BY    
                    'BMS-CR' ,  
                    concat("ChangeRequest_BK",'_', e."Employee_BK"),
                    Concat('CR Approval: ',"TitleofChangeRequest") ,
                    "DescribetheProposedChange",
                    "ApplicationDate",
                    "StakeholderChangeReviewDueDate",
                    ifnull(e."Email",s."Email"),
                    s."Email",
                    "ChangeType",
                    "ChangeOf",
                    "ChangeTrigger",
                    ifnull("FLocation"."FLOC", l."Location"),
                    "ReviewDate",
                    case when "ReviewDate" <  current_date() + 1 then 'Open' else 'Overdue' end,
                    Concat('https://bms.fmgl.com.au/NetForms/#/view/Change-Request/', "ChangeRequest_BK"),
                    CR."EffectiveFromDate"
                    
                UNION ALL
                // Identify Then Rectify
                --*/
                SELECT 
                    'BMS-ITR' as "BMS_Type",
                    concat("IdentifyRectify_BK" ,'_', e."Employee_BK")as "bms_action_id",
                    "IdentifyRectify_BriefDescription" as "action_title",
                    "IdentifyRectify_ListExpectedBenefits" as "detailed_description",
                    "IdentifyRectify_DateIdentified" as "date_raised",
                    null as "due_date",
                    ifnull(e."Email",s."Email") as "employee_email",
                    s."Email" as "supervisor_email",
                    null as "incident_title",
                    "Assessment_Priority" as "criticality",
                    null as "discipline",
                    "IdentifyRectify_CategoryOfIdea" as "category",
                    "IdentifyRectify_SpecificLocation" as "location",
                    null as "ReviewDate",
                    ITR."CurrentStatus",
                    Concat('https://bms.fmgl.com.au/NetForms/#/view/Identify-then-Rectify/', "IdentifyRectify_BK") as "link",
                    ITR."EffectiveFromDate",
                    null as "TeamMembers",
                    null as "TeamEmail"
                FROM "EDW"."SELFSERVICE"."IdentifyThenRectify_History" as "ITR" 

                    INNER JOIN "EDW"."SELFSERVICE"."Location" l ON l."Location_BK" = ITR."Key_Location"
                    LEFT OUTER JOIN "FLocation" ON "FLocation"."Location" = l."Location"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" e ON ifnull("Key_Employee_ProposedSMEChampion", "Key_Employee_ProposedSupervisor") = e."Employee_BK"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" s ON e."Key_Employee_Supervisor" = s."Employee_BK"    
                
                WHERE
                    ITR."IdentifyRectify_CompleteFlag" = 'No'
                    and ITR."EffectiveToDate" = '9999-12-31'
                    and s."BasisOfEmployment" = 'Full-Time'
                    and e."BasisOfEmployment" = 'Full-Time'
                    and s."PositionStatus" = 'Current'
                    and e."PositionStatus" = 'Current'
    """
    )
    if slidingWindow and latest_source_updated_itr != None:
        sql = sql + f""" and ITR."EffectiveFromDate" > '{latest_source_updated_itr}'"""

    items = sf.execute(sql).fetchall()

    items = parse_obj_as(list[BMS_Action], items)

    def get_priority(criticality: str):

        if criticality == None:
            return PriorityEnum.UNKNOWN

        crit = criticality.lower().strip()
        if (
            crit == "> 2 years"
            or crit == "1 - 2 years"
            or crit == "undefined"
            or crit == "low 1"
            or crit == "low 2"
            or crit == "low 3"
            or crit == "low 4"
            or crit == "low 5"
            or crit == "low 6"
            or crit == "1 - negligible"
            or crit == "2 - low"
        ):
            return PriorityEnum.LOW
        if (
            crit == "3 - 6 months"
            or crit == "6 - 12 months"
            or crit == "moderate 10"
            or crit == "moderate 11"
            or crit == "moderate 7"
            or crit == "moderate 8"
            or crit == "moderate 9"
            or crit == "3 - medium"
        ):
            return PriorityEnum.MEDIUM
        if (
            crit == "> 1 month"
            or crit == "1 - 3 months"
            or crit == "high 12"
            or crit == "high 13"
            or crit == "high 14"
            or crit == "high 15"
            or crit == "high 16"
            or crit == "high 17"
            or crit == "high 18"
            or crit == "high 19"
            or crit == "4 - high"
        ):
            return PriorityEnum.HIGH
        if (
            crit == "1 - 7 days"
            or crit == "immediately"
            or crit == "extreme 21"
            or crit == "extreme 22"
            or crit == "extreme 23"
            or crit == "extreme 24"
            or crit == "extreme 25"
            or crit == "5 - extreme"
        ):
            return PriorityEnum.URGENT

        if crit == "low":
            return PriorityEnum.LOW
        if crit == "medium":
            return PriorityEnum.MEDIUM
        if crit == "high":
            return PriorityEnum.HIGH
        if crit == "urgent":
            return PriorityEnum.URGENT

        return PriorityEnum.UNKNOWN

    def get_status(status: str):

        open_statuses = [
            "AwaitingActionCompletion",
            "AwaitingActionCreation",
            "DevelopImplementationPlan/MOC/Actions",
            "Idea",
            "ImplementedAwaitingCompletion",
            "Open",
            "SMEChampionAssessment",
            "StatusUnknown",
            "SupervisorAssessment",
            "Undefined",
        ]
        closed_statuses = [
            "Closed",
            "HazardCreated",
            "HealthSafetyReview",
            "HealthSafetyReviewNotSupportedAwaitingClosure",
            "HealthSafetyReviewSupported",
        ]

        if status in open_statuses:
            return StatusEnum.OPEN
        if status in closed_statuses:
            return StatusEnum.CLOSED

        # BMS-CR type
        if status == "Overdue":
            return StatusEnum.OVERDUE

        return None

    ids = [item.bms_action_id for item in items]

    # Stats for Sync Log
    numCreated = 0
    numUpdated = 0
    numArchived = 0

    for item in items:
        # Determine type of BMS Action
        action = None
        if item.BMS_Type == "BMS-ACT":
            action = crud.bms_act_action.get_create(db, source_id=item.bms_action_id)
        elif item.BMS_Type == "BMS-CR":
            action = crud.bms_cr_action.get_create(db, source_id=item.bms_action_id)
        elif item.BMS_Type == "BMS-HZD":
            action = crud.bms_hzd_action.get_create(db, source_id=item.bms_action_id)
        elif item.BMS_Type == "BMS-ITR":
            action = crud.bms_itr_action.get_create(db, source_id=item.bms_action_id)

        # only update if the source has been updated
        ingested_source_updated = (
            item.EffectiveFromDate.replace(tzinfo=utc) if item.EffectiveFromDate else None
        )
        current_source_updated = (
            action.source_updated.replace(tzinfo=utc) if action.source_updated else None
        )

        if (
            current_source_updated
            and ingested_source_updated
            and current_source_updated >= ingested_source_updated
        ):
            continue

        if action.title == None:
            numCreated = numCreated + 1
        else:
            numUpdated = numUpdated + 1

        # generic
        action.title = item.action_title
        action.description = item.detailed_description
        action.priority = get_priority(item.criticality)
        action.status = get_status(item.Status)
        action.link = item.link

        # users
        owner = None
        if item.employee_email:
            owner = crud.user.get_kw_single(db, email=item.employee_email.lower())
        action.owner_id = owner.id if owner else None

        supervisor = None
        if item.supervisor_email:
            supervisor = crud.user.get_kw_single(db, email=item.supervisor_email.lower())
        action.supervisor_id = supervisor.id if supervisor else None

        members = []
        if item.TeamEmail:
            for email in item.TeamEmail.split(","):
                member = crud.user.get_kw_single(db, email=email.lower())
                if member and not any(x.id == member.id for x in members):
                    action.members.append(member)

        # dates
        action.source_updated = item.EffectiveFromDate
        action.start_date = item.date_raised
        action.date_due = item.due_date

        # unique to BMS
        metadata_object = Metadata_BMS(item.discipline, item.category, item.location)
        action.action_metadata = metadata_object.__dict__

        db.commit()

    db.commit()

    # Make another query request to get just all Action ID's to compare to data we have
    # and delete records that are no longer there
    ids_sql = """
           --/* BMS UNIONED DATA FOR ACE
                With "FLocation" ("Location", "FLOC")
                as
                (
                Select distinct  "Location",
                    Case 
                        When charindex('CB - OPF - Crusher', "Location") > 0 Then 'CLB-PP-CRSH'
                        When charindex('CB - OPF - Desand', "Location") > 0 Then 'CLB-PP-DSND'
                        When charindex('CB - OPF - In Feed', "Location") > 0 Then 'CLB-PP-RMIN'
                        When charindex('CB - OPF - Infeed', "Location") > 0 Then 'CLB-PP-RMIN'
                        When charindex('CB - OPF - Screen', "Location") > 0 Then 'CLB-PP-SSCR'        
                        When charindex('CB - OPF - Stockpile', "Location") > 0 Then 'CLB-PP-TRLO'
                        When charindex('CB - OPF -  Train Load Out', "Location") > 0 Then 'CLB-PP-TRLO'
                        When charindex('CB - OPF - Wet Front End', "Location") > 0 Then 'CLB-PP-WSCR'
                        When charindex('CB - OPF', "Location") > 0 Then 'CLB-PP'
                        
                        When charindex('CC - OPF1', "Location") > 0 Then 'CLB-P1'
                        When charindex('CC - OPF2', "Location") > 0 Then 'CLB-P2'
                        
                        When charindex('EW - OPF', "Location") > 0 Then 'ELW-P1'
                        When charindex('EW - Stockyards', "Location") > 0 Then 'ELW-SY'
                        When charindex('EW - Train Load Out', "Location") > 0 Then 'ELW-SY-TRLO'
                        When charindex('EW - Primary Crushing', "Location") > 0 Then 'ELW-P1-RMIN'
                        
                        //When charindex('IB - Ore Processing Facility', "Location") > 0 Then 'IBO-P1-RMIN'
                        
                        When charindex('Sol - Firetail OPF', "Location") > 0 Then 'SOL-FT'
                        When charindex('Sol - Firetail Crushing Hub', "Location") > 0 Then 'SOL-FT-CRSH'
                        When charindex('Sol - Trainloader', "Location") > 0 Then 'SOL-SY-TRLO'
                        When charindex('Sol - Kings OPF', "Location") > 0 Then 'SOL-KV'
                        When charindex('Sol - Kings Crushing Hub A', "Location") > 0 Then 'SOL-KV-CRSH'
                        When charindex('Sol - Kings Crushing Hub B', "Location") > 0 Then 'SOL-KV-CRSH'
                        When charindex('Sol - Stockyards', "Location") > 0 Then 'SOL-SY'
                        
                        When charindex('Anderson Point Port', "Location") > 0 Then 'APT'
                        When charindex('Port - Inloading', "Location") > 0 Then 'APT-IL'
                        When charindex('Port - RC701', "Location") > 0 Then 'APT-OL-RCLM-RC701'
                        When charindex('Port - RC702', "Location") > 0 Then 'APT-OL-RCLM-RC702'
                        When charindex('Port - RC703', "Location") > 0 Then 'APT-OL-RCLM-RC703'
                        When charindex('Port - SK701', "Location") > 0 Then 'APT-IL-STKG-SK701'
                        When charindex('Port - SK702', "Location") > 0 Then 'APT-IL-STKG-SK702'
                        When charindex('Port - SK704', "Location") > 0 Then 'APT-IL-STKG-SK704'
                        When charindex('Port - SK705', "Location") > 0 Then 'APT-IL-STKG-SK705'
                        When charindex('Port - SL701', "Location") > 0 Then 'APT-IL-STKG-SL701'
                        When charindex('Port - SL702', "Location") > 0 Then 'APT-IL-STKG-SL702'
                        When charindex('Port - SL703', "Location") > 0 Then 'APT-IL-STKG-SL703'
                        When charindex('Port - SS903', "Location") > 0 Then 'APT-IL-STKG-SS903'
                        When charindex('Port - SS944', "Location") > 0 Then 'APT-IL-STKG-SS944'
                        When charindex('Port - SS945', "Location") > 0 Then 'APT-IL-STKG-SS945'
                        When charindex('Port - TS901', "Location") > 0 Then 'APT-IL-STKG-TS901'
                        When charindex('Port - TS902', "Location") > 0 Then 'APT-IL-STKG-TS902'
                        When charindex('Port - TS903', "Location") > 0 Then 'APT-IL-STKG-TS903'
                        When charindex('Port - TS904', "Location") > 0 Then 'APT-IL-STKG-TS904'
                        When charindex('Port - TS905', "Location") > 0 Then 'APT-IL-STKG-TS905'
                        When charindex('Port - TS906', "Location") > 0 Then 'APT-IL-STKG-TS906'
                        When charindex('Port - TS908', "Location") > 0 Then 'APT-IL-STKG-TS908'
                        When charindex('Port - TS914', "Location") > 0 Then 'APT-IL-STKG-TS914'
                        When charindex('Port - TS917', "Location") > 0 Then 'APT-IL-STKG-TS917'
                        When charindex('Port - TS944', "Location") > 0 Then 'APT-IL-STKG-TS944'
                        When charindex('Port - TS945', "Location") > 0 Then 'APT-IL-STKG-TS945'
                        When charindex('Port - TS950', "Location") > 0 Then 'APT-IL-STKG-TS950'
                        When charindex('Port - TS951', "Location") > 0 Then 'APT-IL-STKG-TS951'
                        When charindex('Port - TS954', "Location") > 0 Then 'APT-IL-STKG-TS954'
                        When charindex('Port - TU601', "Location") > 0 Then 'APT-IL-STKG-TU601'
                        When charindex('Port - TU602', "Location") > 0 Then 'APT-IL-STKG-TU602'
                        When charindex('Port - TU603', "Location") > 0 Then 'APT-IL-STKG-TU603'
                        When charindex('Port - CV901', "Location") > 0 Then 'APT-IL-STKG-CV901'
                        When charindex('Port - CV903', "Location") > 0 Then 'APT-IL-STKG-CV903'
                        When charindex('Port - CV905', "Location") > 0 Then 'APT-IL-STKG-CV905'
                        When charindex('Port - CV906', "Location") > 0 Then 'APT-IL-STKG-CV906'
                        When charindex('Port - CV908', "Location") > 0 Then 'APT-IL-STKG-CV908'
                        When charindex('Port - CV911', "Location") > 0 Then 'APT-IL-STKG-CV911'
                        When charindex('Port - CV912', "Location") > 0 Then 'APT-IL-STKG-CV912'
                        When charindex('Port - CV913', "Location") > 0 Then 'APT-IL-STKG-CV913'
                        When charindex('Port - CV914', "Location") > 0 Then 'APT-IL-STKG-CV914'
                        When charindex('Port - CV915', "Location") > 0 Then 'APT-IL-STKG-CV915'
                        When charindex('Port - CV916', "Location") > 0 Then 'APT-IL-STKG-CV916'
                        When charindex('Port - CV917', "Location") > 0 Then 'APT-IL-STKG-CV917'
                        When charindex('Port - CV921', "Location") > 0 Then 'APT-IL-STKG-CV921'
                        When charindex('Port - CV922', "Location") > 0 Then 'APT-IL-STKG-CV922'
                        When charindex('Port - CV927', "Location") > 0 Then 'APT-IL-STKG-CV927'
                        When charindex('Port - CV932', "Location") > 0 Then 'APT-IL-STKG-CV932'
                        When charindex('Port - CV944', "Location") > 0 Then 'APT-IL-STKG-CV944'
                        When charindex('Port - CV945', "Location") > 0 Then 'APT-IL-STKG-CV945'
                        When charindex('Port - CV948', "Location") > 0 Then 'APT-IL-STKG-CV948'
                        When charindex('Port - CV950', "Location") > 0 Then 'APT-IL-STKG-CV950'
                        When charindex('Port - CV951', "Location") > 0 Then 'APT-IL-STKG-CV951'
                        When charindex('Port - CV953', "Location") > 0 Then 'APT-IL-STKG-CV953'
                        When charindex('Port - CV968', "Location") > 0 Then 'APT-IL-STKG-CV968'
                        
                        Else "Location"
                    End FLOC
                From "EDW"."SELFSERVICE"."Location"
                )
                --/* 

                SELECT
                    concat("Action_BK",'_', "Employee_BK") as "bms_action_id"
                FROM "EDW"."SELFSERVICE"."Action_History" as "Action"
                    INNER JOIN (
                        --this adds redundancy for null email
                        SELECT
                            E1."Employee_BK",
                            lower(
                                CASE
                                    WHEN E1."Email" IS NULL THEN E2."Email"
                                    ELSE E1."Email"
                                END
                            ) as "employee_email",
                            E2."Email" as "supervisor_email"
                        FROM
                            "EDW"."SELFSERVICE"."Employee" E1
                            INNER JOIN "EDW"."SELFSERVICE"."Employee" E2 ON E1."Key_Employee_Supervisor" = E2."Employee_BK"
                        WHERE  e1."BasisOfEmployment" = 'Full-Time'
                        and e2."BasisOfEmployment" = 'Full-Time'
                        and e1."PositionStatus" = 'Current'
                        and e2."PositionStatus" = 'Current'
                    ) "email_lookup" --end redundancy
                    ON "email_lookup"."Employee_BK" = "Action"."Key_Employee_Responsible"
                    
                    LEFT OUTER JOIN "FLocation" ON "FLocation"."Location" = "Action"."Location"
                    LEFT OUTER JOIN "EDW"."SELFSERVICE"."Incident" ON "Action"."Key_Incident" = "Incident"."Incident_BK"
                    
                    LEFT OUTER JOIN 
                                    (Select "Key_Action", listagg(Concat(ifnull("PreferredName", "FirstName"), ' ', "LastName"), ',') "TeamMembers", listagg("Email", ',') "TeamEmail"
                                    from EDW.SELFSERVICE."DA_HEALTHANDSAFETY_Action_to_TeamMember"as TM
                                        INNER JOIN EDW.SELFSERVICE."Employee" as E 
                                                ON TM."Key_Employee" = E."Employee_BK"
                                    
                                        GROUP BY "Key_Action") as TM ON TM."Key_Action" = "Action"."Action_BK"
                WHERE
                    "Action"."Status" != 'Closed'
                    AND "EffectiveToDate" = '9999-12-31'
                    AND "Action"."DeletionFlag" = 'No'
                    
                    
                UNION ALL
                // HAZARD
                SELECT 
                    concat("Hazard_BK",'_', e."Employee_BK") as "bms_action_id"
                    FROM "EDW"."SELFSERVICE"."Hazard_History" as "Hazard" 
                    LEFT OUTER JOIN "FLocation" ON "FLocation"."Location" = "Hazard"."Location"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" e ON "Key_Employee_HazardOwner" = e."Employee_BK"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" s ON e."Key_Employee_Supervisor" = s."Employee_BK"     
                
                WHERE
                    "EffectiveToDate" = '9999-12-31'
                    AND "Hazard"."Status" = 'Open'
                    --AND "Hazard_BK" = 'HAZ-374217'
                    
                UNION ALL

                // CHANGE REQUEST REVIEW
                SELECT 
                    concat("ChangeRequest_BK",'_', e."Employee_BK") as "bms_action_id"
                FROM "EDW"."SELFSERVICE"."ChangeRequest_History" as "CR" 
                    INNER JOIN "EDW"."SELFSERVICE"."ChangeRequestReview_History" as "CRR" ON CR."ChangeRequest_BK" = CRR."Key_ChangeRequest"
                    INNER JOIN "EDW"."SELFSERVICE"."Location" l ON l."Location_BK" = CR."Key_Location"
                    LEFT OUTER JOIN "FLocation" ON "FLocation"."Location" = l."Location"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" e ON "Key_Employee_ChangeReviewer" = e."Employee_BK"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" s ON e."Key_Employee_Supervisor" = s."Employee_BK"    
                
                WHERE
                    CRR."EffectiveToDate" = '9999-12-31'
                    AND CR."EffectiveToDate" = '9999-12-31'
                    AND CRR."ReviewStatus" = 'Undefined'
                    AND "AuthorisationFinalReviewDate" is null
                    and s."BasisOfEmployment" = 'Full-Time'
                    and e."BasisOfEmployment" = 'Full-Time'
                    and e."PositionStatus" = 'Current'
                    and e."PositionStatus" = 'Current'
                    and CR."CanthisChangebeclosedFlag" = 0
                    and CR."AuthorisationStatus" = 'Undefined'
                    

                UNION ALL
                // CHANGE REQUEST APPROVAL
                SELECT 
                    concat("ChangeRequest_BK",'_', e."Employee_BK") as "bms_action_id"
                FROM "EDW"."SELFSERVICE"."ChangeRequest_History" as "CR" 
                    INNER JOIN "EDW"."SELFSERVICE"."Location" l ON l."Location_BK" = CR."Key_Location"
                    LEFT OUTER JOIN "FLocation" ON "FLocation"."Location" = l."Location"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" e ON "Key_Employee_ChangeAuthoriserCRSS" = e."Employee_BK"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" s ON e."Key_Employee_Supervisor" = s."Employee_BK"    
                    LEFT OUTER JOIN (Select CRR."Key_ChangeRequest"
                                        from "EDW"."SELFSERVICE"."ChangeRequestReview_History" as "CRR" 
                                        WHERE IFNULL(CRR."ReviewStatus", 'Undefined') = 'Undefined' 
                                        and CRR."EffectiveToDate" = '9999-12-31'
                                        Group By CRR."Key_ChangeRequest") as Review 
                                        on Review."Key_ChangeRequest" = CR."ChangeRequest_BK"
                    
                
                WHERE 1 = 1
                    and CR."EffectiveToDate" = '9999-12-31'
                    and CR."AuthorisationStatus" = 'Undefined'
                    and s."BasisOfEmployment" = 'Full-Time'
                    and e."BasisOfEmployment" = 'Full-Time'
                    and s."PositionStatus" = 'Current'
                    and e."PositionStatus" = 'Current'
                    and CR."CanthisChangebeclosedFlag" = 0
                    AND Review."Key_ChangeRequest" IS NULL
                    and "SelectifreadytosubmittoStakeholders" = 1
                
                
                    

                GROUP BY    
                    'BMS-CR' ,  
                    concat("ChangeRequest_BK",'_', e."Employee_BK"),
                    Concat('CR Approval: ',"TitleofChangeRequest") ,
                    "DescribetheProposedChange",
                    "ApplicationDate",
                    "StakeholderChangeReviewDueDate",
                    ifnull(e."Email",s."Email"),
                    s."Email",
                    "ChangeType",
                    "ChangeOf",
                    "ChangeTrigger",
                    ifnull("FLocation"."FLOC", l."Location"),
                    "ReviewDate",
                    case when "ReviewDate" <  current_date() + 1 then 'Open' else 'Overdue' end,
                    Concat('https://bms.fmgl.com.au/NetForms/#/view/Change-Request/', "ChangeRequest_BK"),
                    CR."EffectiveFromDate"
                    
                UNION ALL
                // Identify Then Rectify
                --*/
                SELECT 
                    concat("IdentifyRectify_BK" ,'_', e."Employee_BK")as "bms_action_id"
                FROM "EDW"."SELFSERVICE"."IdentifyThenRectify_History" as "ITR" 

                    INNER JOIN "EDW"."SELFSERVICE"."Location" l ON l."Location_BK" = ITR."Key_Location"
                    LEFT OUTER JOIN "FLocation" ON "FLocation"."Location" = l."Location"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" e ON ifnull("Key_Employee_ProposedSMEChampion", "Key_Employee_ProposedSupervisor") = e."Employee_BK"
                    INNER JOIN "EDW"."SELFSERVICE"."Employee" s ON e."Key_Employee_Supervisor" = s."Employee_BK"    
                
                WHERE
                    ITR."IdentifyRectify_CompleteFlag" = 'No'
                    and ITR."EffectiveToDate" = '9999-12-31'
                    and s."BasisOfEmployment" = 'Full-Time'
                    and e."BasisOfEmployment" = 'Full-Time'
                    and s."PositionStatus" = 'Current'
                    and e."PositionStatus" = 'Current'
    
    """
    item_ids = sf.execute(ids_sql).fetchall()
    action_ids = [bms_item.bms_action_id for bms_item in item_ids]

    # delete removed rows
    """
    db.query(schemas.BMS_ACT_Action).filter(
        schemas.BMS_ACT_Action.source_id.not_in(action_ids)
    ).delete()
    db.query(schemas.BMS_CR_Action).filter(
        schemas.BMS_CR_Action.source_id.not_in(action_ids)
    ).delete()
    db.query(schemas.BMS_HZD_Action).filter(
        schemas.BMS_HZD_Action.source_id.not_in(action_ids)
    ).delete()
    db.query(schemas.BMS_ITR_Action).filter(
        schemas.BMS_ITR_Action.source_id.not_in(action_ids)
    ).delete()
    """
    numArchived1 = crud.archive_action.archive_actions(
        db, schemas.BMS_ACT_Action, action_ids, syncUUID, True
    )
    numArchived2 = crud.archive_action.archive_actions(
        db, schemas.BMS_CR_Action, action_ids, syncUUID, True
    )
    numArchived3 = crud.archive_action.archive_actions(
        db, schemas.BMS_HZD_Action, action_ids, syncUUID, True
    )
    numArchived4 = crud.archive_action.archive_actions(
        db, schemas.BMS_ITR_Action, action_ids, syncUUID, True
    )

    db.commit()

    numArchived = numArchived1 + numArchived2 + numArchived3 + numArchived4

    # Return # of actions created, updated, archived
    stats = [numCreated, numUpdated, numArchived]
    return stats


# ----------------------------------------------------------------------------------------------------


@router.get("/sap_notification")
async def sap_notification(
    syncUUID,
    db=Depends(utils.get_db),
    sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    class SAP_Notification(Base):
        # common fields
        source_id: str
        title: str = None
        priority: str = None
        functional_location: str = None
        work_center: str = None
        link: str = None

        source_created: dt.date = None
        source_updated: dt.date = None
        date_closed: dt.date = None
        start_date: dt.date = None
        date_due: dt.date = None

        # metadata fields
        meta_notification_type: str = None
        meta_system_status: str = None
        meta_user_status: str = None

    # Get record with latest source_updated
    # So in SF query can get only new records
    query_result = (
        db.query(schemas.SAP_Notification_Action)
        .filter(schemas.SAP_Notification_Action.source_updated != None)
        .order_by(schemas.SAP_Notification_Action.source_updated.desc())
        .limit(1)
        .all()
    )
    latest_source_updated_date_str = (
        str(query_result[0].source_updated) if len(query_result) > 0 else None
    )

    sql = """
        SELECT
            -- BASE ACTION
            "NotificationNumber" as "source_id",
            "NotificationDescription" as "title",
            "PriorityText" as "priority",
            "FunctionalLocationLabel" as "functional_location",
            "MainWorkCentre" as "work_center",
            
            Concat(
                'https://fiori.fmgl.com.au/sap/bc/ui5_ui5/ui2/ushell/shells/abap/Fiorilaunchpad.html#MaintenanceNotification-tcode_ECC_IW23?MaintenanceNotification=',
                regexp_replace("source_id", '(^|-)0*', ''),
                '&sap-app-origin-hint=&sap-xapp-state=ASCAP5FVBLCS6YFOIKLGPH296UF4I8SPQKJW3TL8'
            ) as "link",
            "CreatedOn" as "source_created",
            "Notification"."ChangedOn" as "source_updated",
            "CompletionDate" as "date_closed",
            "RequiredStart" as "start_date",
            "RequiredEnd" as "date_due",
            -- META DATA
            "SystemStatus" as "meta_system_status",
            "UserStatus" as "meta_user_status",
            "NotificationType" as "meta_notification_type"
        FROM
            "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."WorkCentre"
            JOIN "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."Notification" ON "Notification"."MainWorkCentre" = "WorkCentre"."WorkCenter"
        WHERE
            "WorkCentre"."WorkCenter" LIKE '____'
            AND "WorkCentre"."WorkCentreDescription" LIKE '%Engineer%'
            AND "UserStatus" != 'REJ'
            AND "OrderNumber" NOT LIKE '____________'
            AND "SystemStatus" = 'OSNO'
    """
    if latest_source_updated_date_str != None:
        sql = (
            sql + f""" and "Notification"."ChangedOn" > '{latest_source_updated_date_str}'"""
        )  # Latest records only

    items = sf.execute(sql).fetchall()

    items = parse_obj_as(list[SAP_Notification], items)

    def get_datetime(date):
        return dt.datetime.combine(date, dt.time(0, 0, 0)) if date else None

    def get_priority(priority_text: str):
        if priority_text == "Low":
            return PriorityEnum.LOW
        if priority_text == "Medium":
            return PriorityEnum.MEDIUM
        if priority_text == "High":
            return PriorityEnum.HIGH
        if priority_text == "Urgent":
            return PriorityEnum.HIGH

        return PriorityEnum.UNKNOWN

    ids = [item.source_id for item in items]

    # Stats for Sync Log
    numCreated = 0
    numUpdated = 0
    numArchived = 0

    for item in items:
        action = crud.sap_notification_action.get_create(db, source_id=item.source_id)

        # only update if the source has been updated
        ingested_source_updated = (
            get_datetime(item.source_updated).replace(tzinfo=utc) if item.source_updated else None
        )
        current_source_updated = (
            get_datetime(action.source_updated).replace(tzinfo=utc)
            if action.source_updated
            else None
        )

        if (
            current_source_updated
            and ingested_source_updated
            and current_source_updated >= ingested_source_updated
        ):
            continue

        if action.title == None:
            numCreated = (
                numCreated + 1
            )  # Action doesn't have a title, it didn't exist previously, must have created it
        else:
            numUpdated = numUpdated + 1  # Did have a title, existed before, we are updating it

        # generic
        action.title = item.title
        action.priority = get_priority(item.priority)

        # dates
        action.start_date = get_datetime(item.start_date)
        action.date_due = get_datetime(item.date_due)
        action.source_created = get_datetime(item.source_created)
        action.source_updated = get_datetime(item.source_updated)
        action.date_closed = get_datetime(item.date_closed)

        # other
        action.functional_location = item.functional_location
        action.work_center = item.work_center
        action.link = item.link

        # status always open
        action.status = StatusEnum.OPEN

        # unique to SAP Notifications
        metadata_object = Metadata_Sap_Notification(
            item.meta_notification_type, item.meta_system_status, item.meta_user_status
        )
        action.action_metadata = metadata_object.__dict__

    db.commit()

    ids_sql = """
        SELECT
            -- BASE ACTION
            "NotificationNumber" as "source_id"
        FROM
            "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."WorkCentre"
            JOIN "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."Notification" ON "Notification"."MainWorkCentre" = "WorkCentre"."WorkCenter"
        WHERE
            "WorkCentre"."WorkCenter" LIKE '____'
            AND "WorkCentre"."WorkCentreDescription" LIKE '%Engineer%'
            AND "UserStatus" != 'REJ'
            AND "OrderNumber" NOT LIKE '____________'
            AND "SystemStatus" = 'OSNO'
    """
    item_ids = sf.execute(ids_sql).fetchall()
    action_ids = [str(notification_item.source_id) for notification_item in item_ids]

    numArchived = crud.archive_action.archive_actions(
        db, schemas.SAP_Notification_Action, action_ids, syncUUID, True
    )

    db.commit()

    # Return # of actions created, updated, archived
    stats = [numCreated, numUpdated, numArchived]
    return stats


# ----------------------------------------------------------------------------------------------------


@router.get("/sap_work_orders")
async def get_sap_work_orders(
    syncUUID,
    db=Depends(utils.get_db),
    sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    class SAP_WO_Action(Base):
        # common fields
        title: str = None

        priority: str = None

        start_date: dt.date = None
        finish_date: dt.date = None

        source_created: dt.date = None
        source_updated: dt.date = None
        date_closed: dt.date = None

        source_id: str

        functional_location: str = None
        link: str = None
        work_center: str = None

        # metadata fields
        meta_order_type: str = None
        meta_system_status: str = None
        meta_user_status: str = None
        meta_notification_number: str = None
        meta_group: str = None

    # Get record with latest source_updated
    # So in SF query can get only new records
    query_result = (
        db.query(schemas.SAP_Work_Order_Action)
        .filter(schemas.SAP_Work_Order_Action.source_updated != None)
        .order_by(schemas.SAP_Work_Order_Action.source_updated.desc())
        .limit(1)
        .all()
    )
    latest_source_updated_date_str = (
        str(query_result[0].source_updated) if len(query_result) > 0 else None
    )

    sql = """
            SELECT
                -- BASE ACTION
                "OrderNumber" as "source_id",
                "OrderDescription" as "title",
                "PriorityText" as "priority",
                "FunctionalLocationLabel" as "functional_location",
                "MainWorkCentre" as "work_center",
                Concat(
                    'https://fiori.fmgl.com.au/sap/bc/ui5_ui5/ui2/ushell/shells/abap/Fiorilaunchpad.html#MaintenanceOrder-displayFactSheet&/C_ObjPgMaintOrder("',
                    "source_id",
                    '")/?sap-iapp-state=ASCFOZMLDEFAU0YS75JYMFTI1JRVZ59Z07ZKMHSO&sap-iapp-state--history=TASP83TT2SXN3WVIZQBB8G51XCX6YPBSYHZ4OFZVX&&quot;'
                ) as "link",
                "CreatedOn" as "source_created",
                "WorkOrderHeader"."ChangedOn" as "source_updated",
                "ConfirmedActualFinishDate" as "date_closed",
                "BasicStartDate" as "start_date",
                "BasicFinishDate" as "finish_date",
                --  METADATA
                "SystemStatus" as "meta_system_status",
                "UserStatus" as "meta_user_status",
                "Group" as "meta_group",
                "NotificationNumber" as "meta_notification_number",
                "OrderType" as "meta_order_type"
            FROM
                "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."WorkCentre"
                JOIN "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."WorkOrderHeader" ON "WorkOrderHeader"."MainWorkCentre" = "WorkCentre"."WorkCenter"
            WHERE
                "WorkCentre"."WorkCenter" LIKE '____'
                AND "WorkCentre"."WorkCentreDescription" LIKE '%Engineer%'
                AND "UserStatus" NOT LIKE '%CAN%'
                AND "SystemStatus" NOT LIKE '%CNF%'
                AND "SystemStatus" NOT LIKE '%TECO%'
                AND "SystemStatus" NOT LIKE '%CLSD%'
    """
    if latest_source_updated_date_str != None:
        sql = (
            sql + f""" and "WorkOrderHeader"."ChangedOn" > '{latest_source_updated_date_str}'"""
        )  # Latest records only

    items = sf.execute(sql).fetchall()

    items = parse_obj_as(list[SAP_WO_Action], items)

    def get_priority(priority_text: str):
        if priority_text == "Low":
            return PriorityEnum.LOW
        if priority_text == "Medium":
            return PriorityEnum.MEDIUM
        if priority_text == "High":
            return PriorityEnum.HIGH
        if priority_text == "Urgent":
            return PriorityEnum.HIGH

        return PriorityEnum.UNKNOWN

    def get_datetime(date):
        return dt.datetime.combine(date, dt.time(0, 0, 0)) if date else None

    ids = [item.source_id for item in items]

    # Stats for Sync Log
    numCreated = 0
    numUpdated = 0
    numArchived = 0

    for item in items:
        action = crud.sap_work_order_action.get_create(db, source_id=item.source_id)

        # only update if the source has been updated
        ingested_source_updated = (
            get_datetime(item.source_updated).replace(tzinfo=utc) if item.source_updated else None
        )
        current_source_updated = (
            get_datetime(action.source_updated).replace(tzinfo=utc)
            if action.source_updated
            else None
        )

        if (
            current_source_updated
            and ingested_source_updated
            and current_source_updated >= ingested_source_updated
        ):
            continue

        if action.title == None:
            numCreated = numCreated + 1
        else:
            numUpdated = numUpdated + 1

        # generic
        action.title = item.title
        action.priority = get_priority(item.priority)

        # dates
        action.start_date = get_datetime(item.start_date)
        action.date_due = get_datetime(item.finish_date)
        action.source_created = get_datetime(item.source_created)
        action.source_updated = get_datetime(item.source_updated)
        action.date_closed = get_datetime(item.date_closed)

        # other
        action.functional_location = item.functional_location
        action.link = item.link
        action.work_center = item.work_center

        # status always open
        action.status = StatusEnum.OPEN

        # unique to SAP Workorders
        metadata_object = Metadata_Sap_WO(
            item.meta_order_type,
            item.meta_system_status,
            item.meta_user_status,
            item.meta_notification_number,
            item.meta_group,
        )
        action.action_metadata = metadata_object.__dict__

    db.commit()

    ids_sql = """
        SELECT
                -- BASE ACTION
                "OrderNumber" as "source_id"
            FROM
                "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."WorkCentre"
                JOIN "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."WorkOrderHeader" ON "WorkOrderHeader"."MainWorkCentre" = "WorkCentre"."WorkCenter"
            WHERE
                "WorkCentre"."WorkCenter" LIKE '____'
                AND "WorkCentre"."WorkCentreDescription" LIKE '%Engineer%'
                AND "UserStatus" NOT LIKE '%CAN%'
                AND "SystemStatus" NOT LIKE '%CNF%'
                AND "SystemStatus" NOT LIKE '%TECO%'
                AND "SystemStatus" NOT LIKE '%CLSD%'
    """
    item_ids = sf.execute(ids_sql).fetchall()
    action_ids = [str(wo_item.source_id) for wo_item in item_ids]

    numArchived = crud.archive_action.archive_actions(
        db, schemas.SAP_Work_Order_Action, action_ids, syncUUID, True
    )

    db.commit()

    # Return # of actions created, updated, archived
    stats = [numCreated, numUpdated, numArchived]
    return stats


# ----------------------------------------------------------------------------------------------------


@router.get("/smh")
async def smh(
    syncUUID,
    db=Depends(utils.get_db),
    sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    class SMH(Base):
        # common fields
        source_id: str
        title: str = None
        description: str = None
        priority: str = None
        status: str = None
        link: str = None
        source_created: dt.datetime = None
        source_updated: dt.datetime = None
        date_closed: dt.datetime = None
        start_date: dt.datetime = None
        date_due: dt.date = None
        owner_email: str = None
        member_emails: str = None
        supervisor_email: str = None

        # metadata fields
        meta_classification: str = None
        meta_last_comments: str = None

    # Get record with latest source_updated
    # So in SF query can get only new records
    query_result = (
        db.query(schemas.SMH_Action)
        .order_by(schemas.SMH_Action.source_updated.desc())
        .limit(1)
        .all()
    )
    latest_source_updated_date_str = (
        str(query_result[0].source_updated.date()) if len(query_result) > 0 else None
    )

    sql = """
        Select 
        -- BASE ACTION
        a."Id" as "source_id", 
        "ActionName" as "title", 
        "Revision" as "description",
        "PriorityName" as "priority",
        "StatusName" as "status",
        Concat('https://shuthub.fmgl.com.au/Action') as "link",
        a."CreatedAt" as "source_created",
        a."EffectiveFromDate" as "source_updated",
        "CompletedDate" as "date_closed", 
        a."CreatedAt" as "start_date",
        "DueDate" as "date_due",
        u."EmailId" as "owner_email", 
        users."UserEmails" as "member_emails",

        -- META DATA
        "ClassificationName" as "meta_classification", 
        "LastComments" as "meta_last_comments"

    from EDW.STG_SHUTMANAGEMENTHUB."Action" as a
        left outer join "EDW"."STG_SHUTMANAGEMENTHUB"."Classification" as c
            on a."ClassificationId" = c."Id"
        left outer join "EDW"."STG_SHUTMANAGEMENTHUB"."ShutdownEventDefinition" as sed
            on a."ShutdownEventDefinitionId" = sed."Id"
        left outer join "EDW"."STG_SHUTMANAGEMENTHUB"."ActionStatus" as acs
            on a."ActionStatusId" = acs."Id"
        left outer join "EDW"."STG_SHUTMANAGEMENTHUB"."ActionPriority" as ap
            on a."ActionPriorityId" = ap."Id"
        left outer join (
            Select listagg(u."EmailId", ', ') as "UserEmails", listagg(u."FullName", ', ') as "UserNames", au."ActionId"
            from "EDW"."STG_SHUTMANAGEMENTHUB"."ActionUser" as au
            inner join "EDW"."STG_SHUTMANAGEMENTHUB"."User" as u
                on au."UserId" = u."Id"
            where au."EffectiveToDate" IS NULL
                    and  u."EffectiveToDate" IS NULL
            Group By au."ActionId"
                            ) as users
                on users."ActionId" = a."Id"
        left outer join "EDW"."STG_SHUTMANAGEMENTHUB"."User" as u
                    on a."CreatedBy" = u."FullName"

        where c."EffectiveToDate" Is Null
        and sed."EffectiveToDate" Is Null
        and acs."EffectiveToDate" Is Null
        and ap."EffectiveToDate" Is Null
        and u."EffectiveToDate" IS NULL
        and a."EffectiveToDate" IS NULL
        and acs."Id" < 3
        and a."IsActive" = TRUE
    """
    if latest_source_updated_date_str != None:
        sql = (
            sql + f""" and a."EffectiveFromDate" > '{latest_source_updated_date_str}'"""
        )  # Latest records only

    items = sf.execute(sql).fetchall()

    items = parse_obj_as(list[SMH], items)

    def get_datetime(date):
        return dt.datetime.combine(date, dt.time(0, 0, 0)) if date else None

    def get_priority(PriorityName: str):
        if PriorityName == "Low":
            return PriorityEnum.LOW
        if PriorityName == "Medium":
            return PriorityEnum.MEDIUM
        if PriorityName == "High":
            return PriorityEnum.HIGH
        if PriorityName == "Urgent":
            return PriorityEnum.HIGH

        return PriorityEnum.UNKNOWN

    def get_status(StatusName: str):
        if StatusName == "Open":
            return StatusEnum.OPEN
        if StatusName == "On Hold":
            return StatusEnum.ON_HOLD
        if StatusName == "Closed":
            return StatusEnum.CLOSED
        if StatusName == "Overdue":
            return StatusEnum.OVERDUE

        return None

    ids = [item.source_id for item in items]
    action_member_associations = []

    # Stats for Sync Log
    numCreated = 0
    numUpdated = 0
    numArchived = 0

    for item in items:

        action = crud.smh_action.get_create(db, source_id=item.source_id)

        # only update if the source has been updated
        ingested_source_updated = (
            item.source_updated.replace(tzinfo=utc) if item.source_updated else None
        )
        current_source_updated = (
            action.source_updated.replace(tzinfo=utc) if action.source_updated else None
        )

        if (
            current_source_updated
            and ingested_source_updated
            and current_source_updated >= ingested_source_updated
        ):
            continue

        if action.title == None:
            numCreated = numCreated + 1
        else:
            numUpdated = numUpdated + 1

        # generic
        action.title = item.title
        action.description = item.description
        action.priority = get_priority(item.priority)
        action.status = get_status(item.status)
        action.link = item.link
        action.source_created = item.source_created
        action.source_updated = item.source_updated
        action.date_closed = item.date_closed
        action.date_due = get_datetime(item.date_due)
        action.start_date = item.start_date

        owner = None
        if item.owner_email:
            owner = crud.user.get_kw_single(db, email=item.owner_email.lower())
        action.owner_id = owner.id if owner else None

        if item.member_emails:
            for email in item.member_emails.split(","):
                member = crud.user.get_kw_single(db, email=email.strip().lower())

                if member and member.id not in action.members:
                    action_member_associations.append(
                        {"action_id": action.id, "user_id": member.id}
                    )

        # unique to SMH Notifications
        metadata_object = Metadata_SMH(item.meta_classification, item.meta_last_comments)
        action.action_metadata = metadata_object.__dict__

    db.commit()

    for association in action_member_associations:
        crud.action_member_association.get_create(db, **association)
    db.commit()

    ids_sql = """

                   Select 
        -- BASE ACTION
        a."Id" as "source_id"

    from EDW.STG_SHUTMANAGEMENTHUB."Action" as a
        left outer join "EDW"."STG_SHUTMANAGEMENTHUB"."Classification" as c
            on a."ClassificationId" = c."Id"
        left outer join "EDW"."STG_SHUTMANAGEMENTHUB"."ShutdownEventDefinition" as sed
            on a."ShutdownEventDefinitionId" = sed."Id"
        left outer join "EDW"."STG_SHUTMANAGEMENTHUB"."ActionStatus" as acs
            on a."ActionStatusId" = acs."Id"
        left outer join "EDW"."STG_SHUTMANAGEMENTHUB"."ActionPriority" as ap
            on a."ActionPriorityId" = ap."Id"
        left outer join (
            Select listagg(u."EmailId", ', ') as "UserEmails", listagg(u."FullName", ', ') as "UserNames", au."ActionId"
            from "EDW"."STG_SHUTMANAGEMENTHUB"."ActionUser" as au
            inner join "EDW"."STG_SHUTMANAGEMENTHUB"."User" as u
                on au."UserId" = u."Id"
            where au."EffectiveToDate" IS NULL
                    and  u."EffectiveToDate" IS NULL
            Group By au."ActionId"
                            ) as users
                on users."ActionId" = a."Id"
        left outer join "EDW"."STG_SHUTMANAGEMENTHUB"."User" as u
                    on a."CreatedBy" = u."FullName"

        where c."EffectiveToDate" Is Null
        and sed."EffectiveToDate" Is Null
        and acs."EffectiveToDate" Is Null
        and ap."EffectiveToDate" Is Null
        and u."EffectiveToDate" IS NULL
        and a."EffectiveToDate" IS NULL
        and acs."Id" < 3
        and a."IsActive" = TRUE

    """
    item_ids = sf.execute(ids_sql).fetchall()
    action_ids = [str(smh_item.source_id) for smh_item in item_ids]

    numArchived = crud.archive_action.archive_actions(
        db, schemas.SMH_Action, action_ids, syncUUID, True
    )

    db.commit()

    # Return # of actions created, updated, archived
    stats = [numCreated, numUpdated, numArchived]
    return stats


# ----------------------------------------------------------------------------------------------------


@router.get("/ahm")
async def ahm(
    syncUUID,
    db=Depends(utils.get_db),
    sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
    slidingWindow: bool = True,
):
    class AHM(Base):
        # common fields
        source_id: str
        title: str = None
        priority: str = None
        functional_location: str = None
        link: str = None
        source_created: dt.datetime = None
        source_updated: dt.datetime = None
        start_date: dt.date = None

        # metadata fields
        meta_notification_number: str = None
        meta_asset_id: str = None
        meta_equipment_description: str = None
        meta_object_type: str = None
        meta_technology: str = None

    # Get record with latest source_updated
    # So in SF query can get only new records
    query_result = (
        db.query(schemas.AHM_Action)
        .order_by(schemas.AHM_Action.source_updated.desc())
        .limit(1)
        .all()
    )
    latest_source_updated_date_str = (
        str(query_result[0].source_updated.date()) if len(query_result) > 0 else None
    )
    if slidingWindow:
        query_result = (
            db.query(schemas.AHM_Action)
            .order_by(schemas.AHM_Action.source_updated.desc())
            .limit(1)
            .all()
        )
        latest_source_updated_date_str = (
            str(query_result[0].source_updated.date()) if len(query_result) > 0 else None
        )

    sql = """
        SELECT "AnalysisId" as "source_id",
                Concat(
                        'No WO for ',
                        A."AssetDescription",
                        ' currently classified as ', AH."AssetHealthName", ' for ',
                        "TechnologyName",
                        ' in AHM'
                    ) as "title",
                
                "AssetNumber", 
                "AssetDescription", 
                "AssetHealthName" as "priority", 
                "AnalysisDate" as "start_date", 
                
                AN."CreatedAt" as "source_created",
                FL."FLocName"  as "functional_location",
                T."TechnologyName",
                AN."EffectiveFromDate" as "source_updated",
                Concat('https://ahm.fmgl.com.au/Analysis/Details/', "source_id") as "link",
                -- META DATA
                AN."AssetId"  as "meta_asset_id", 
                "NotificationNumber" as "meta_notification_number", 
                "EquipmentDescription" as "meta_equipment_description", 
                "ObjectTypeText" as "meta_object_type" 
        FROM "EDW"."STG_AHM"."Analysis" as AN
        INNER JOIN "EDW"."STG_AHM"."Asset" AS A ON A."AssetId" = AN."AssetId"
        INNER JOIN "EDW"."STG_AHM"."AssetHealth" AS AH ON A."AssetHealthId" = AH."AssetHealthId"
        INNER JOIN "EDW"."STG_AHM"."Equipment" AS E ON E."EquipmentNumber" = A."EquipmentNumber"
        INNER JOIN "EDW"."STG_AHM"."FunctionLocation" AS FL ON FL."FLocObjectNumber" = E."FLocObjectNumber"
        INNER JOIN "EDW"."STG_AHM"."Fault" as F on F."FaultId" = AN."FaultId" 
        INNER JOIN "EDW"."STG_AHM"."Technology" as T on T."TechnologyId" = F."TechnologyId"
        LEFT OUTER JOIN "EDW"."STG_AHM"."ObjectType" AS OT ON OT."ObjectTypeCode" = E."ObjectType"
        WHERE "WorkOrderNumber" IS NULL
        AND AN."EffectiveToDate" IS NULL
        AND AH."EffectiveToDate" IS NULL
        AND A."EffectiveToDate" IS NULL
        AND E."EffectiveToDate" IS NULL
        AND OT."EffectiveToDate" IS NULL
        AND T."EffectiveToDate" IS NULL
        AND F."EffectiveToDate" IS NULL
        AND FL."DeletionFlag" = FALSE
        AND FL."IsActive" = TRUE
        AND FL."EffectiveToDate" IS NULL
        AND A."IsActive" = TRUE
        AND AN."AssetHealthId" = 1 -- SERVERE
        AND AN."IsActive" = 1
    """

    if latest_source_updated_date_str != None:
        sql = (
            sql + f""" and AN."EffectiveFromDate" > '{latest_source_updated_date_str}'"""
        )  # Latest records only
    if slidingWindow and latest_source_updated_date_str != None:
        sql = (
            sql + f""" and AN."EffectiveFromDate" > '{latest_source_updated_date_str}'"""
        )  # Latest records only

    items = sf.execute(sql).fetchall()

    items = parse_obj_as(list[AHM], items)

    def get_datetime(date):
        return dt.datetime.combine(date, dt.time(0, 0, 0)) if date else None

    def get_priority(PriorityName: str):
        if PriorityName == "Healthy":
            return PriorityEnum.LOW
        if PriorityName == "Moderate":
            return PriorityEnum.MEDIUM
        if PriorityName == "Abnormal":
            return PriorityEnum.HIGH
        if PriorityName == "Severe":
            return PriorityEnum.URGENT
        if PriorityName == "Not Measured":
            return PriorityEnum.UNKNOWN

        return PriorityEnum.UNKNOWN

    ids = [item.source_id for item in items]

    # Stats for Sync Log
    numCreated = 0
    numUpdated = 0
    numArchived = 0

    for item in items:

        action = crud.ahm_action.get_create(db, source_id=item.source_id)

        if slidingWindow:
            # only update if the source has been updated
            ingested_source_updated = (
                item.source_updated.replace(tzinfo=utc) if item.source_updated else None
            )
            current_source_updated = (
                action.source_updated.replace(tzinfo=utc) if action.source_updated else None
            )

            if (
                current_source_updated
                and ingested_source_updated
                and current_source_updated >= ingested_source_updated
            ):
                continue

        if action.title == None:
            numCreated = numCreated + 1
        else:
            numUpdated = numUpdated + 1

        # generic
        action.title = item.title
        action.priority = get_priority(item.priority)
        action.start_date = get_datetime(item.start_date)
        action.source_created = item.source_created
        action.source_updated = item.source_updated
        action.functional_location = item.functional_location
        action.link = item.link

        # status always open
        action.status = StatusEnum.OPEN

        # unique to AHM Notifications
        metadata_object = Metadata_AHM(
            item.meta_notification_number,
            item.meta_asset_id,
            item.meta_equipment_description,
            item.meta_object_type,
            item.meta_technology,
        )
        action.action_metadata = metadata_object.__dict__

    db.commit()

    ids_sql = """
        SELECT "AnalysisId" as "source_id"
        FROM "EDW"."STG_AHM"."Analysis" as AN
        INNER JOIN "EDW"."STG_AHM"."Asset" AS A ON A."AssetId" = AN."AssetId"
        INNER JOIN "EDW"."STG_AHM"."AssetHealth" AS AH ON A."AssetHealthId" = AH."AssetHealthId"
        INNER JOIN "EDW"."STG_AHM"."Equipment" AS E ON E."EquipmentNumber" = A."EquipmentNumber"
        INNER JOIN "EDW"."STG_AHM"."FunctionLocation" AS FL ON FL."FLocObjectNumber" = E."FLocObjectNumber"
        INNER JOIN "EDW"."STG_AHM"."Fault" as F on F."FaultId" = AN."FaultId" 
        INNER JOIN "EDW"."STG_AHM"."Technology" as T on T."TechnologyId" = F."TechnologyId"
        LEFT OUTER JOIN "EDW"."STG_AHM"."ObjectType" AS OT ON OT."ObjectTypeCode" = E."ObjectType"
        WHERE "WorkOrderNumber" IS NULL
        AND AN."EffectiveToDate" IS NULL
        AND AH."EffectiveToDate" IS NULL
        AND A."EffectiveToDate" IS NULL
        AND E."EffectiveToDate" IS NULL
        AND OT."EffectiveToDate" IS NULL
        AND T."EffectiveToDate" IS NULL
        AND F."EffectiveToDate" IS NULL
        AND FL."DeletionFlag" = FALSE
        AND FL."IsActive" = TRUE
        AND FL."EffectiveToDate" IS NULL
        AND A."IsActive" = TRUE
        AND AN."AssetHealthId" = 1 -- SERVERE
        AND AN."IsActive" = 1
    """

    item_ids = sf.execute(ids_sql).fetchall()
    action_ids = [str(ahm_item.source_id) for ahm_item in item_ids]

    numArchived = crud.archive_action.archive_actions(
        db, schemas.AHM_Action, action_ids, syncUUID, True
    )

    db.commit()

    # Return # of actions created, updated, archived
    stats = [numCreated, numUpdated, numArchived]
    return stats


# ----------------------------------------------------------------------------------------------------


@router.get("/dep")
async def dep(
    syncUUID,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    class DEP(Base):
        # common fields
        id: str = None  # Source_ID
        title: str = None  # Title
        description: str = None  # description

        priority: str = None  # priority
        status: int = None  # status
        created: dt.datetime = None  # Source Created
        updated: dt.datetime = None  # Source Update
        date_closed: dt.datetime = None  # Date Closed
        date_due: dt.datetime = None  # Date Due
        owner_emails: list[str] = None
        member_emails: list[str] = None
        # Owners (this gives id array, there is a Owners object which is slightly more detailed)
        supervisor_email: str = None  # Supervisor
        functional_location: str = None

    # Get record with latest source_updated
    # So in SF query can get only new records
    query_result = (
        db.query(schemas.DEP_Action)
        .order_by(schemas.DEP_Action.source_updated.desc())
        .limit(1)
        .all()
    )
    latest_source_updated_date_str = (
        str(query_result[0].source_updated) if len(query_result) > 0 else None
    )

    if latest_source_updated_date_str == None:
        dep_url = "https://dep.fmgl.com.au/api/action/all_actions?token=" + config.DEP_API_KEY
    else:
        dep_url = (
            "https://dep.fmgl.com.au/api/action/all_actions?token="
            + config.DEP_API_KEY
            + "&last_updated="
            + str(urllib.parse.quote(latest_source_updated_date_str))
        )

    response = requests.get(dep_url, verify=False)
    data = response.json()
    items = parse_obj_as(list[DEP], data)

    # remove closed status (X)
    # items = [item for item in items if item.status != 3]
    items = [item for item in items]

    # Build Action objects
    def get_priority(priorityStr: str):
        if priorityStr == "Low":
            return PriorityEnum.LOW
        if priorityStr == "Medium":
            return PriorityEnum.MEDIUM
        if priorityStr == "High":
            return PriorityEnum.HIGH

        return PriorityEnum.UNKNOWN

    def get_status(statusStr: int):
        if statusStr == 1:
            return StatusEnum.OPEN
        if statusStr == 2:
            return StatusEnum.ON_HOLD
        if statusStr == 3:
            return StatusEnum.CLOSED
        if statusStr == 4:
            return StatusEnum.OVERDUE

        return None

    ids = [item.id for item in items]

    user_cache = {}

    def get_user(email):
        if not email:
            return None

        if email in user_cache:
            return user_cache[email]

        user = crud.user.get_kw_single(db, email=email)
        if user:
            user_cache[email] = user
            return user

        return None

    # Stats for Sync Log
    numCreated = 0
    numUpdated = 0
    numArchived = 0

    for item in items:
        action = crud.dep_action.get_create(db, source_id=item.id)

        # only update if the source has been updated
        ingested_source_updated = item.updated.replace(tzinfo=utc) if item.updated else None
        current_source_updated = (
            action.source_updated.replace(tzinfo=utc) if action.source_updated else None
        )

        if (
            current_source_updated
            and ingested_source_updated
            and current_source_updated >= ingested_source_updated
        ):
            continue

        if action.title == None:
            numCreated = numCreated + 1
        else:
            numUpdated = numUpdated + 1

        action.title = item.title
        action.description = item.description
        action.priority = get_priority(item.priority)
        action.status = get_status(item.status)
        action.source_created = item.created
        action.source_updated = item.updated
        action.date_closed = item.date_closed
        action.date_due = item.date_due
        action.functional_location = item.functional_location
        action.link = "https://dep.fmgl.com.au/actions?action_id=" + str(item.id)

        # DEP action Owners - can have up to 2 owners
        # owner_id & dep_extra_owner_id
        if item.owner_emails:
            user1 = get_user(item.owner_emails[0])
            if user1:
                action.owner_id = user1.id
            if len(item.owner_emails) == 2:
                user2 = get_user(item.owner_emails[1])
                if user2:
                    action.dep_extra_owner_id = user2.id

        # Supervisor_id - from supervisor_email
        supervisor_user = get_user(item.supervisor_email)
        if supervisor_user:
            action.supervisor_id = supervisor_user.id

        # Action_Member_Assocation's
        member_users = []

        if item.member_emails:
            for email in item.member_emails:
                user = get_user(email)
                if user:
                    member_users.append(user)

            action.members = member_users

        db.commit()

    dep_url = "https://dep.fmgl.com.au/api/action/all_action_ids?token=" + config.DEP_API_KEY
    response = requests.get(dep_url, verify=False)
    text_result = response.text
    text_result = text_result[1:-1]
    source_ids = [s.strip() for s in text_result.split(",")]

    numArchived = crud.archive_action.archive_actions(
        db, schemas.DEP_Action, source_ids, syncUUID, True
    )
    db.commit()

    # Return # of actions created, updated, archived
    stats = [numCreated, numUpdated, numArchived]
    return stats


# ----------------------------------------------------------------------------------------------


@router.get("/pims")
async def pims(
    syncUUID,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    url = "https://pims-api.fmg.local/dcs/reviews-approvals?take=-1"
    credentialsString = base64.b64encode(
        b"af_API_ReviewsApprovals:64B908BE-6D50-4210-AFB5-56AF7272CD30"
    )
    
    headers = {"Authorization": f"Basic {credentialsString}", "Accept": "application/json"}


# ----------------------------------------------------------------------------------------------


# New implementation - teams_sync is called every 30 minutes, and calls this teams method for every access token stored
# access_token = Access Token returned from Microsoft from someone logging in with their microsoft account
def get_teams_tasks(access_token: str, userName: str, syncUUID: str, db=Depends(utils.get_db)):

    # Data objects - Teams Tasks and Team Plans - represents the tasks/plan models we get from the API calls
    class Teams_Task:
        id: str
        title: str
        bucketId: str
        #  More details
        createdDateTime: dt.datetime
        percentComplete: int
        completedDateTime: dt.datetime
        dueDateTime: dt.datetime
        priority: int
        description: str

        assigned: list[
            str
        ]  # The Microsoft ID's of users assigned to this task, which represent the Action Members

    class Teams_Group:
        id: str
        name: str
        memberEmails: list[str]
        ownerEmails: list[str]
        ace_workgroup_id: int  # ID of the associated ACE workgroup

    class Teams_Plan:
        id: str
        title: str
        groupId: str  # The ID of the group (collection of members) that has access to this plan/board
        teams_group: Teams_Group  # The Group object that belongs to this plan
        tasks: list[Teams_Task]

    headers = {"Authorization": f"Bearer {access_token}"}

    def parse_datetime(val):
        if val:
            return dt.datetime.strptime(val[:19], "%Y-%m-%dT%H:%M:%S")
        else:
            return None

    def get_task_description(taskId):
        res = requests.get(
            f"https://graph.microsoft.com/v1.0/planner/tasks/{taskId}/details", headers=headers
        )

        data = res.json()
        description = ""
        if "description" in data and data["description"] != None and data["description"] != "":
            description = data["description"]

        # Checklist handling
        """
        if "checklist" in data and data["checklist"] != {}:
            description += "\n\n\nCHECKLIST:\n"
            for check in data["checklist"].values():
                line = f"({check['title']} - CHECKED: {check['isChecked']}"
                description += line + " \n"
        """

        return description

    # Get workgroups that have already been updated recently - in the last **updated_threshold_minutes** minutes - and don't update those
    updated_threshold_minutes = 120  # Set to 120 minutes (2 hours) (cron runs every 3 hours, takes roughly 2 hours to complete a teams sync in background, due to sleeps)
    updated_time_threshold = utils.get_time_now() - dt.timedelta(minutes=updated_threshold_minutes)
    already_updated_groups_query = (
        db.query(schemas.Workgroup.teams_id)
        .where(schemas.Workgroup.updated >= updated_time_threshold)
        .distinct()
    )
    groupIdsAlreadyUpdated = db.scalars(
        already_updated_groups_query
    ).all()  # Contains the Microsoft Teams_ID's of Workgroups already updated, that we want to skip

    team_plans = []  # collection of Teams_Plans
    buckets = {}  # key,value pair of teams buckets - key = ID of bucket, value = Name of bucket
    groups = (
        {}
    )  # key,value pair of teams group names - key = ID of group, value = Teams_Group object

    # Workgroup/action ids we see/process - keep track to later compare to db entries
    workgroup_ids = []
    action_ids = []

    # Stats for Sync Log
    numActionsCreated = 0
    numActionsArchived = 0
    numWorkgroupsCreated = 0
    workgroupIdsInvolved = (
        []
    )  # All Workgroup IDs (ACE IDs) that we go through in this method, as strings

    # me/planner/plans - Get all Boards/Plans user has access to
    res = requests.get("https://graph.microsoft.com/v1.0/me/planner/plans", headers=headers)
    data = res.json()

    for plan in data["value"]:
        team_plan = Teams_Plan()
        team_plan.id = plan["id"]
        team_plan.title = plan["title"]
        team_plan.groupId = plan["container"]["containerId"]

        team_plans.append(team_plan)

    # Filter out Plans that belong to Groups/Workgroups we have already updated recently
    team_plans = [tp for tp in team_plans if tp.groupId not in groupIdsAlreadyUpdated]

    # planner/plans/{plan.id}/buckets - Get Bucket IDs/Names in all plans - Set buckets dict to contain (BucketID, BucketName), later will set tasks bucket names from this dict
    for plan in team_plans:
        res = requests.get(
            f"https://graph.microsoft.com/v1.0/planner/plans/{plan.id}/buckets", headers=headers
        )
        data = res.json()
        for bucket in data["value"]:
            buckets[bucket["id"]] = bucket["name"]

    # groups/{group_id} - Get group name, e.g. "Software". Create Teams_Group object for this group, and savec into groups dict
    for plan in team_plans:
        if plan.groupId in groups:
            continue
        res = requests.get(
            f"https://graph.microsoft.com/v1.0/groups/{plan.groupId}", headers=headers
        )
        data = res.json()

        teams_group = Teams_Group()
        teams_group.id = plan.groupId
        teams_group.name = data["displayName"]
        groups[plan.groupId] = teams_group

    # groups/{group_id}/members - Gets the members that belong to a group. These members/group will make a Workgroup.
    for groupId, groupObject in groups.items():
        url = f"https://graph.microsoft.com/v1.0/groups/{groupId}/members"
        group_member_emails = []

        while url != "":
            res = requests.get(url, headers=headers)
            data = res.json()

            # If more than 100 members returned in this query, will contain a link that contains remaining results
            if "@odata.nextLink" in data and data["@odata.nextLink"] != "":
                url = data["@odata.nextLink"]
            else:
                url = ""

            for member in data["value"]:
                if member["mail"] is not None:
                    group_member_emails.append(member["mail"])

        groupObject.memberEmails = group_member_emails

    # groups/{group_id}/owners - Gets the owner users of the group. These users will be the admins of the workgroups.
    for groupId, groupObject in groups.items():
        url = f"https://graph.microsoft.com/v1.0/groups/{groupId}/owners"
        group_owner_emails = []

        while url != "":
            res = requests.get(url, headers=headers)
            data = res.json()

            # If more than 100 members returned in this query, will contain a link that contains remaining results
            if "@odata.nextLink" in data and data["@odata.nextLink"] != "":
                url = data["@odata.nextLink"]
            else:
                url = ""

            for owner in data["value"]:
                if owner["mail"] is not None:
                    group_owner_emails.append(owner["mail"])

        groupObject.ownerEmails = group_owner_emails

    # planner/plans/{plan_id}/tasks - Get all tasks that belong to each plan
    for plan in team_plans:
        res = requests.get(
            f"https://graph.microsoft.com/v1.0/planner/plans/{plan.id}/tasks", headers=headers
        )
        data = res.json()

        tasks = []
        for task in data["value"]:
            team_task = Teams_Task()
            team_task.id = task["id"]
            team_task.title = task["title"]
            team_task.bucketId = task["bucketId"]
            # More details about tasks
            team_task.createdDateTime = parse_datetime(task["createdDateTime"])
            team_task.percentComplete = task["percentComplete"]
            team_task.completedDateTime = parse_datetime(task["completedDateTime"])
            team_task.dueDateTime = parse_datetime(task["dueDateTime"])
            team_task.priority = task["priority"]

            hasDescription = task["hasDescription"]

            if "assignments" in task and task["assignments"] != None and task["assignments"] != {}:
                assign = []
                for user_id in task["assignments"]:
                    assign.append(user_id)
                team_task.assigned = assign
            else:
                team_task.assigned = None

            # Only get the description if we don't have this task in the DB already, otherwise, dont update the description
            # If we already have this task in DB, don't worry about updating description -- make less requests
            dbCount = crud.teams_action.count(db, source_id=team_task.id)
            if(dbCount == 0 and hasDescription == True):
                taskDescription = get_task_description(team_task.id)
                team_task.description = taskDescription
            else:
                team_task.description = ""

            tasks.append(team_task)
        plan.tasks = tasks

    # Here, if we iterate through each plan, and iterate through tasks in each plan, we should have all plans

    # Start creating ACE records for these.
    # Create/update workgroups from teams groups
    for groupId, groupObject in groups.items():
        workgroup = crud.workgroup.get_create(db, teams_id=groupId)

        # Stats collecting - numWorkgroupsCreated
        if workgroup.title == None:
            numWorkgroupsCreated = numWorkgroupsCreated + 1

        # Workgroup members
        member_ids = []
        for member_email in groupObject.memberEmails:
            user = crud.user.get_kw_single(db, email=member_email)
            if user == None:
                continue
            member_ids.append(user.id)
        workgroup.member_ids = member_ids

        # Workgroup Admins (from owners of Teams Group)
        admin_ids = []
        for owner_email in groupObject.ownerEmails:
            user = crud.user.get_kw_single(db, email=owner_email)
            if user == None:
                continue
            admin_ids.append(user.id)
        workgroup.admin_ids = admin_ids

        workgroup.title = "Teams - " + groupObject.name
        workgroup.privacy = PrivacyEnum.CONFIDENTIAL
        workgroup.teams_last_updated = utils.get_time_now()  # Last updated

        db.commit()
        groupObject.ace_workgroup_id = workgroup.id

        workgroup_ids.append(workgroup.id)

        # Stats collecting - workgroupIdsInvolved - using the actual ACE workgroup ID, not the teams ID
        workgroupIdsInvolved.append(str(workgroup.id))

    creatingTask = False

    for plan in team_plans:
        for task in plan.tasks:
            action = crud.teams_action.get_create(db, source_id=task.id)

            # Stats collecting - numCreated
            if action.title == None:
                numActionsCreated = numActionsCreated + 1
                creatingTask = True
            else:
                creatingTask = False

            teams_group_object = groups[plan.groupId]
            actionTitle = plan.title + " - " + buckets[task.bucketId] + " - " + task.title
            action.title = actionTitle
            action.privacy = PrivacyEnum.CONFIDENTIAL

            action.source_created = task.createdDateTime

            # Status mapping - only if fully complete
            if task.percentComplete == 100:
                action.status = StatusEnum.CLOSED
                action.date_closed = task.completedDateTime
            else:
                # If this action is already made, and has been set overdue, don't override, keep overdue.
                if(action.status != StatusEnum.OVERDUE):
                    action.status = StatusEnum.OPEN

            if task.description != "":
                action.description = task.description

            if task.dueDateTime != None:
                action.date_due = task.dueDateTime

            # Priority enum mapping
            if task.priority == 1:  # Urgent
                action.priority = PriorityEnum.HIGH
            elif task.priority == 3:  # Important
                action.priority = PriorityEnum.HIGH
            elif task.priority == 5:  # Medium
                action.priority = PriorityEnum.MEDIUM
            elif task.priority == 9:  # Low
                action.priority = PriorityEnum.LOW

            action.completed = task.percentComplete

            # Assigned To - Users - Members of the action - get their User object from the Microsoft IDs
            if task.assigned != None:
                assigned_to_users = []
                for user_microsoft_id in task.assigned:
                    user_object = crud.user.get_kw_single(db, microsoft_id=user_microsoft_id)
                    if user_object != None:
                        assigned_to_users.append(user_object)
                if len(assigned_to_users) > 0:
                    action.members = assigned_to_users

            db.commit()

            if(creatingTask == True):
                crud.workgroup_action_association.get_create(
                    db, **{"workgroup_id": teams_group_object.ace_workgroup_id, "action_id": action.id}
                )
                db.commit()

            action_ids.append(action.id)

    # Delete actions that are no longer there
    #   - Get teams actions associated to teams/groups we saw (their respective workgroup), delete ones where id didn't come through
    workgroup_action_query = (
        select(schemas.Workgroup_Action_Association.action_id)
        .where(schemas.Workgroup_Action_Association.workgroup_id.in_(workgroup_ids))
        .distinct()
    )
    action_ids_query = db.scalars(workgroup_action_query).all()
    actions_teams = crud.teams_action.get_all(db, action_ids_query)

    actions_teams = [tAction for tAction in actions_teams if tAction != None]

    actions_teams_id = [
        t_action.id for t_action in actions_teams
    ]  # IDs of Teams actions in DB that belong to workgroups we've seen

    teams_actions_to_delete_ids = set(actions_teams_id) - set(action_ids)

    numActionsArchived = crud.archive_action.archive_actions_teams(
        db, teams_actions_to_delete_ids, syncUUID
    )

    db.commit()

    print(
        "Sync - "
        + syncUUID
        + "  - User: "
        + userName
        + "   - Actions Created: "
        + str(numActionsCreated)
        + "   - Workgroups Created: "
        + str(numWorkgroupsCreated)
        + "   - Actions Archived: "
        + str(numActionsArchived)
    )

    # Returns - numActionsCreated, numActionsArchived, numWorkgroupsCreated, workgroupIdsInvolved
    stats = [numActionsCreated, numActionsArchived, numWorkgroupsCreated, workgroupIdsInvolved]
    return stats


# ----------------------------------------------------------------------------------------------


def teams_sync_complete(*, db=Depends(utils.get_db)):

    # For stats/log
    totalNumActionsCreated = 0
    totalNumActionsArchived = 0
    totalNumWorkgroupsCreated = 0
    totalWorkgroupIdsInvolved = []
    userIdsInvoled = []
    # Teams Methods Returns In Order - numActionsCreated, numActionsArchived, numWorkgroupsCreated, workgroupIdsInvolved

    syncUUID = str(uuid.uuid4())  # UUID for this sync
    print("Teams Sync - " + syncUUID + "    - Starting")

    loggedInUsers = utils.user.get_logged_in_users_tokens_redis()
    for loggedInUser in loggedInUsers:

        # Check how fresh access/refresh tokens are - get new ones if older than 50 minutes, and save them.
        if loggedInUser.timestamp + dt.timedelta(minutes=50) < utils.get_time_now():
            print(
                "User ID: " + str(loggedInUser.userId) + "    - Tokens older than 45 minutes"
            )  # TODO - remove
            newTokens = utils.user.get_new_microsoft_tokens(loggedInUser.refresh_token)
            loggedInUser.access_token = newTokens[0]
            loggedInUser.refresh_token = newTokens[1]
            utils.user.save_user_tokens_redis(
                loggedInUser.userId, loggedInUser.access_token, loggedInUser.refresh_token
            )

        # Run teams for this user
        userObject = crud.user.get(db, loggedInUser.userId)
        stats = get_teams_tasks(loggedInUser.access_token, userObject.name, syncUUID, db)

        # Collect stats for log
        userIdsInvoled.append(str(loggedInUser.userId))
        totalNumActionsCreated = totalNumActionsCreated + stats[0]
        totalNumActionsArchived = totalNumActionsArchived + stats[1]
        totalNumWorkgroupsCreated = totalNumWorkgroupsCreated + stats[2]
        totalWorkgroupIdsInvolved.extend(stats[3])

        # Sleep for 60 seconds between user, in hopes of not going over requests limit
        time.sleep(60)

    # Create Log
    workgroupIdsInvolvedString = ",".join(totalWorkgroupIdsInvolved)
    userIdsInvoledString = ",".join(userIdsInvoled)
    crud.log.create_teams_ingestion_log(
        db,
        syncUUID,
        totalNumActionsCreated,
        totalNumActionsArchived,
        totalNumWorkgroupsCreated,
        workgroupIdsInvolvedString,
        userIdsInvoledString,
    )
    print("Teams Sync - " + syncUUID + "    - Completed")

@router.get("/teams_sync")
def teams_sync(*, db=Depends(utils.get_db), valid=Depends(utils.token_auth), background_task: BackgroundTasks = None):
    background_task.add_task(
        teams_sync_complete, db=db
    )
    return "Started teams sync"