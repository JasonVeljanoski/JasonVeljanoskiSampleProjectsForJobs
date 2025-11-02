import csv
import datetime as dt
import enum
import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import case, desc, func

from app import crud, models, schemas, utils
from app.schemas.enums import TimeUsageCode

router = APIRouter()


# ------------------
# GETS
# ------------------
@router.post("/aplus_event_details")
def get_aplus_event_details(
    *,
    db_sf=Depends(utils.get_sf_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    aplus_event_ids: list[str],
):
    ids = ""
    for x in aplus_event_ids:
        ids += f"{x},"
    ids = ids[:-1]

    q = f"""
        SELECT
        SUM(CASE WHEN "EffectiveDuration" IS NOT NULL THEN "EffectiveDuration"/3600
        WHEN (CASE WHEN "StartTime" IS NOT NULL AND "EndTime" IS NOT NULL THEN 1 END) = 1 THEN DATEDIFF(sec, "StartTime", "EndTime")/3600
        ELSE 0
        END )"EffectiveDuration",
        SUM(CASE WHEN "TonnesLoss" IS NOT NULL THEN "TonnesLoss" 
        ELSE 0 
        END) "TonnesLoss"

        FROM "EDW"."SELFSERVICE"."APLUS_vwEventAllocation" 
        WHERE "Id" IN ({ids})
    """

    result = db_sf.execute(q).mappings().all()
    return result[0]


@router.post("/rems_event_details")
def get_rems_event_details(
    *,
    db_sf=Depends(utils.get_sf_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    rems_event_ids: list[str],
):
    ids = ""
    for x in rems_event_ids:
        ids += f"'{x}',"
    ids = ids[:-1]

    # q = f"""
    #     SELECT sum(datediff(s,"EventDateTime","SystemClosedDate"))/3600 as "duration"
    #     FROM "EDW"."STG_REMS"."Event"
    #     WHERE "EventID" IN ( {ids})
    #     AND "Event"."DeletionFlag" = FALSE AND "Event"."EffectiveToDate" IS NULL
    # """

    q = f"""
    SELECT 
        SUM(
        CASE WHEN (datediff(s,"EventDateTime","EventClosedDateTime")) IS NOT NULL
        THEN (datediff(s,"EventDateTime","EventClosedDateTime"))/3600
        WHEN (datediff(s,"EventDateTime","SystemClosedDate")) IS NOT NULL
        THEN (datediff(s,"EventDateTime","SystemClosedDate"))/3600  
        ELSE 0 
        END ) "duration"
        FROM "EDW"."STG_REMS"."Event"
        WHERE "EventID" IN ({ids})
        AND "Event"."DeletionFlag" = FALSE AND "Event"."EffectiveToDate" IS NULL
    """

    result = db_sf.execute(q).mappings().all()
    return result[0]


# ------------------
# CREATE
# ------------------

# ------------------
# CHARTING
# ------------------
class ChartData(BaseModel):
    id: int = Field(None, alias="Id")
    equipment_id: int = Field(None, alias="EquipmentId")
    equipment_name: str = Field(None, alias="EquipmentName")
    start_time: dt.datetime = Field(None, alias="StartTime")
    effective_duration: float = Field(None, alias="EffectiveDuration_hrs")
    problem: str = Field(None, alias="Problem")
    action: str = Field(None, alias="Action")
    cause: str = Field(None, alias="Cause")
    region_name: str = Field(None, alias="RegionName")
    area_name: str = Field(None, alias="AreaName")
    circuit: str = Field(None, alias="Circuit")
    date: dt.date = Field(None, alias="Date")
    time_usage_code: TimeUsageCode = Field(None, alias="TimeUsageCode")

    def get_sql():
        # return """
        #     SELECT
        #     "APLUS_vwEventAllocation"."Id",
        #     "APLUS_vwEventAllocation"."EquipmentId",
        #     "APLUS_vwEventAllocation"."EquipmentName",
        #     "StartTime",
        #     "EffectiveDuration"/3600 as "EffectiveDuration_hrs",
        #     "Problem",
        #     "Action",
        #     "Cause",
        #     "RegionName",
        #     "AreaName",
        #     CASE WHEN "Circuit" IS NOT NULL THEN "Circuit" ELSE 'General' END AS "Circuit",
        #     TO_DATE("StartTime") AS "Date"
        #     FROM "EDW"."SELFSERVICE"."APLUS_vwEventAllocation"
        #     LEFT OUTER JOIN "EDW"."SELFSERVICE"."APLUS_EquipmentLocation" ON "APLUS_vwEventAllocation"."EquipmentId" = "APLUS_EquipmentLocation"."EquipmentId"
        #     WHERE ("StartTime" > DATEADD(DAY, -32, CURRENT_DATE )  OR "EndTime" > DATEADD(DAY, -32, CURRENT_DATE ))
        #     AND "TimeUsageCode" IN ('UM')
        # """
        return """
            SELECT DISTINCT
            "APLUS_vwEventAllocation"."Id",
            "APLUS_vwEventAllocation"."EquipmentId",
            "APLUS_vwEventAllocation"."EquipmentName",
            "StartTime",
            "EffectiveDuration"/3600 as "EffectiveDuration_hrs",
            "Problem",
            "Action",
            "Cause",
            "RegionName",
            "AreaName",
            CASE WHEN "Circuit" IS NOT NULL THEN "Circuit" ELSE 'General' END
            "Circuit",
            TO_DATE("StartTime") AS "Date",
            "TimeUsageCode"
            FROM "EDW"."SELFSERVICE"."APLUS_vwEventAllocation"
            LEFT OUTER JOIN "EDW"."SELFSERVICE"."APLUS_EquipmentLocation" ON "APLUS_vwEventAllocation"."EquipmentId" = "APLUS_EquipmentLocation"."EquipmentId"
            WHERE (
                ("StartTime" > DATEADD(DAY, -32, CURRENT_DATE )  OR "EndTime" > DATEADD(DAY, -32, CURRENT_DATE )) AND "Level"  = 'Production'
            )
        """


def run_snowflake_query_chart_data(db, model, **kwargs):
    sql = model.get_sql(**kwargs)

    raw = db.execute(sql)

    results = raw.fetchall()
    result_list = []
    for x in results:
        item = model()
        item.id = x[0]  # keep this line to have the aplus id from snowflake
        item.equipment_id = x[1]
        item.equipment_name = x[2]
        item.start_time = x[3]
        item.effective_duration = x[4]
        item.problem = x[5]
        item.action = x[6]
        item.cause = x[7]
        item.region_name = x[8]
        item.area_name = x[9]
        item.circuit = x[10]
        item.date = x[11]
        item.time_usage_code = x[12] if x[12] else "OTHER"

        result_list.append(item)

    return result_list


@router.post("/fetch_data")
def get_chart_data(
    *,
    db=Depends(utils.get_db),
    sf_db=Depends(utils.get_sf_db),
    valid=Depends(utils.token_auth),
):
    crud.charting.delete_all(db)

    data = run_snowflake_query_chart_data(sf_db, ChartData)
    for i in data:
        check_exist = crud.charting.get(db, i.id)
        if check_exist == None:

            # ------------------------------------------------------------------------------------------------
            # DEV OPS ITEM: Product Backlog Item 181634: Filter out subset of listed causes from the APLUS data
            # Requirement to filter out all rows that have a cause of the below.
            cause_black_list = [
                None,
                "Availability Downstream",
                "Availability Upstream",
                "Bench Change",
                "Machine Move",
                "No Cause",
                "Opportune Maintenance",
                "Overloaded Wagons",
                "Preventative Maintenance",
                # "Rate Loss",
                "Scheduled Maintenance",
                "Hatch Change",
                "Bin Level",
                "High Bin Levels",
                "Unbalanced Bogies",
            ]

            if i.cause in cause_black_list:
                continue
            # ------------------------------------------------------------------------------------------------

            db.add(
                schemas.Charting(
                    id=i.id,
                    equipment_id=i.equipment_id,
                    equipment_name=i.equipment_name,
                    start_time=i.start_time,
                    date=i.date,
                    effective_duration=i.effective_duration,
                    problem=i.problem,
                    action=i.action,
                    cause=i.cause,
                    region_name=i.region_name,
                    area_name=i.area_name,
                    circuit=i.circuit,
                    time_usage_code=i.time_usage_code,
                )
            )
    db.commit()


@router.get("/get_chart", response_model=list[models.Charting_chart])
def get_chart(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    filters: str = None,
):
    filters = json.loads(filters)
    week_ago = dt.date.today() - dt.timedelta(days=7)
    start_date = dt.datetime.strptime(filters["startDate"], "%Y-%m-%dT%H:%M:%S.%fz").date()

    data = (
        db.query(
            schemas.Charting.equipment_name,
            func.sum(schemas.Charting.effective_duration).label("sum_duration"),
            func.count(schemas.Charting.equipment_name).label("equipment_count"),
            func.sum(
                case(
                    [
                        (
                            schemas.APLUS_Selected_Event_Details_Association.event_id
                            == schemas.Charting.id,
                            1,
                        )
                    ],
                    else_=0,
                )
            ).label("has_investigation"),
            func.sum(case([(schemas.Charting.date <= week_ago, 1)], else_=0)).label(
                "within_week_count"
            ),
            func.sum(
                case(
                    [
                        (
                            schemas.Charting.date <= week_ago,
                            schemas.Charting.effective_duration,
                        )
                    ],
                    else_=0,
                )
            ).label("within_week_sum"),
            func.sum(case([(schemas.Charting.date > week_ago, 1)], else_=0)).label(
                "over_week_count"
            ),
            func.sum(
                case(
                    [
                        (
                            schemas.Charting.date > week_ago,
                            schemas.Charting.effective_duration,
                        )
                    ],
                    else_=0,
                )
            ).label("over_week_sum"),
            schemas.Charting.cause,
        )
        .join(
            schemas.APLUS_Selected_Event_Details_Association,
            schemas.APLUS_Selected_Event_Details_Association.event_id == schemas.Charting.id,
            isouter=True,
        )
        .group_by(schemas.Charting.equipment_name)
        .group_by(schemas.Charting.cause)
    )
    if "startDate" in filters:
        data = data.filter(schemas.Charting.date > start_date)
    if "problemSelected" in filters:
        data = data.filter(schemas.Charting.problem.in_([*filters["problemSelected"]]))
    if "actionSelected" in filters:
        data = data.filter(schemas.Charting.action.in_([*filters["actionSelected"]]))
    if "regionSelected" in filters:
        data = data.filter(schemas.Charting.region_name.in_(filters["regionSelected"]))
    if "areaSelected" in filters:
        data = data.filter(schemas.Charting.area_name.in_(filters["areaSelected"]))
    if "circuitSelected" in filters:
        data = data.filter(schemas.Charting.circuit.in_(filters["circuitSelected"]))
    if "timeUsageSelected" in filters:
        data = data.filter(schemas.Charting.time_usage_code.in_(filters["timeUsageSelected"]))

    data = sorted(
        data.all(),
        reverse=True,
        key=lambda d: d.sum_duration if d.sum_duration != None else 0,
    )
    return data[:10]


def table_filter(data, filters, start_date, period, cause, name):
    data = data.filter(schemas.Charting.equipment_name == name).filter(
        schemas.Charting.cause == cause
    )
    if "startDate" in filters:
        data = data.filter(schemas.Charting.date > start_date)
    if "problemSelected" in filters:
        data = data.filter(schemas.Charting.problem == filters["problemSelected"])
    if "actionSelected" in filters:
        data = data.filter(schemas.Charting.action == filters["actionSelected"])
    if "regionSelected" in filters:
        data = data.filter(schemas.Charting.region_name.in_(filters["regionSelected"]))
    if "areaSelected" in filters:
        data = data.filter(schemas.Charting.area_name.in_(filters["areaSelected"]))
    if "circuitSelected" in filters:
        data = data.filter(schemas.Charting.circuit.in_(filters["circuitSelected"]))
    if "timeUsageSelected" in filters:
        data = data.filter(schemas.Charting.time_usage_code.in_(filters["timeUsageSelected"]))

    # if period == "within 7 days":
    #     period = dt.date.today() - dt.timedelta(days=7)
    #     data = data.filter(schemas.Charting.date <= period)
    # elif period == "over 7 days":
    #     period = dt.date.today() - dt.timedelta(days=7)
    #     data = data.filter(schemas.Charting.date > period)

    if "exactDate" in filters:
        data = data.filter(schemas.Charting.date == filters["exactDate"])

    return data


def get_date_ids(query=None, date=None, problem=None, action=None, circuit=None, time_usage=None):

    query = (
        query.filter(schemas.Charting.date == date)
        .filter(schemas.Charting.problem == problem)
        .filter(schemas.Charting.action == action)
        .filter(schemas.Charting.circuit == circuit)
        .filter(schemas.Charting.time_usage_code == time_usage)
    )
    return query.all()


# route for aplus table
@router.post("/get_equipment")
def get_equipment(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    name: str,
    cause: str,
    period: str,
    filters: str = None,
):
    filters = json.loads(filters)

    # start_date = dt.datetime.strptime(filters["startDate"], "%Y-%m-%dT%H:%M:%S.%fz").date()
    start_date = dt.date.today() - dt.timedelta(days=30)
    data = db.query(
        schemas.Charting.date,
        schemas.Charting.problem,
        schemas.Charting.action,
        schemas.Charting.circuit,
        func.max(schemas.Charting.id).label("id"),
        schemas.Charting.time_usage_code,
        func.sum(schemas.Charting.effective_duration).label("sum_duration"),
        func.count(schemas.Charting.equipment_name).label("equipment_count"),
    )
    data = table_filter(data, filters, start_date, period, cause, name)
    data = (
        data.group_by(schemas.Charting.date)
        .group_by(schemas.Charting.circuit)
        .group_by(schemas.Charting.problem)
        .group_by(schemas.Charting.action)
        .group_by(schemas.Charting.time_usage_code)
    ).all()

    data_date = db.query(schemas.Charting)
    data_date = table_filter(data_date, filters, start_date, period, cause, name)

    results = []

    # check if a investigation is exisit in the system
    has_invest_num = 0

    for row in data:
        # get the investigation id if existed
        row = row._asdict()
        row["investigation_id"] = None
        row["ids"] = []
        # not sure if one aplus id just have one corelated investigation id or not, otherwiese change get_kw_single to get_kw
        investigation = crud.aplus_selected_event_details_association.get_kw(db, event_id=row["id"])

        if len(investigation) != 0:
            investigation = investigation[0]
            row["investigation_id"] = investigation.investigation_id

        if row["investigation_id"] != None:
            results.insert(has_invest_num, row)
            has_invest_num += 1
        else:
            results.append(row)
        # get the ids of the group
        ids_items = get_date_ids(
            data_date,
            date=row["date"],
            problem=row["problem"],
            action=row["action"],
            circuit=row["circuit"],
            time_usage=row["time_usage_code"],
        )
        for item in ids_items:
            row["ids"].append(item.id)

    return results


@router.get("/get_filter_options", response_model=models.Charting_Filter)
def get_filter_options(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    default_day = dt.date.today() - dt.timedelta(days=30)
    problems = (
        db.query(
            schemas.Charting.problem.label("name"),
            func.count(schemas.Charting.problem).label("count"),
        )
        .filter(schemas.Charting.date >= default_day)
        .group_by(schemas.Charting.problem)
        .all()
    )
    actions = (
        db.query(
            schemas.Charting.action.label("name"),
            func.count(schemas.Charting.action).label("count"),
        )
        .filter(schemas.Charting.date >= default_day)
        .group_by(schemas.Charting.action)
        .all()
    )
    region_names = (
        db.query(
            schemas.Charting.region_name.label("name"),
            func.count(schemas.Charting.region_name).label("count"),
        )
        .filter(schemas.Charting.date >= default_day)
        .group_by(schemas.Charting.region_name)
        .all()
    )
    area_names = (
        db.query(
            schemas.Charting.area_name.label("name"),
            func.count(schemas.Charting.area_name).label("count"),
        )
        .filter(schemas.Charting.date >= default_day)
        .group_by(schemas.Charting.area_name)
        .all()
    )
    circuits = (
        db.query(
            schemas.Charting.circuit.label("name"),
            func.count(schemas.Charting.circuit).label("count"),
        )
        .filter(schemas.Charting.date >= default_day)
        .group_by(schemas.Charting.circuit)
        .all()
    )

    time_usage_codes = (
        db.query(
            schemas.Charting.time_usage_code.label("name"),
            func.count(schemas.Charting.time_usage_code).label("count"),
        )
        .filter(schemas.Charting.date >= default_day)
        .group_by(schemas.Charting.time_usage_code)
        .all()
    )

    return models.Charting_Filter(
        problems=problems,
        actions=actions,
        region_names=region_names,
        area_names=area_names,
        circuits=circuits,
        time_usage_codes=time_usage_codes,
    )


def chart_filter(data, filters, start_date, period, cause, name):
    data = data.filter(schemas.Charting.equipment_name == name).filter(
        schemas.Charting.cause == cause
    )
    if "startDate" in filters:
        data = data.filter(schemas.Charting.date > start_date)
    if "problemSelected" in filters:
        data = data.filter(schemas.Charting.problem.in_([*filters["problemSelected"]]))
    if "actionSelected" in filters:
        data = data.filter(schemas.Charting.action.in_([*filters["actionSelected"]]))
    if "regionSelected" in filters:
        data = data.filter(schemas.Charting.region_name.in_(filters["regionSelected"]))
    if "areaSelected" in filters:
        data = data.filter(schemas.Charting.area_name.in_(filters["areaSelected"]))
    if "circuitSelected" in filters:
        data = data.filter(schemas.Charting.circuit.in_(filters["circuitSelected"]))
    if "timeUsageSelected" in filters:
        data = data.filter(schemas.Charting.time_usage_code.in_(filters["timeUsageSelected"]))

    # if period == "within 7 days":
    #     period = dt.date.today() - dt.timedelta(days=7)
    #     data = data.filter(schemas.Charting.date <= period)
    # elif period == "over 7 days":
    #     period = dt.date.today() - dt.timedelta(days=7)
    #     data = data.filter(schemas.Charting.date > period)

    return data


@router.post("/get_equipment_date", response_model=list[models.Charting_Table])
def get_equipment_date(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    name: str,
    cause: str,
    period: str,
    filters: str = None,
):
    filters = json.loads(filters)
    week_ago = dt.date.today() - dt.timedelta(days=7)
    start_date = dt.datetime.strptime(filters["startDate"], "%Y-%m-%dT%H:%M:%S.%fz").date()
    data = db.query(
        schemas.Charting.date,
        func.sum(schemas.Charting.effective_duration).label("sum_duration"),
        func.count(schemas.Charting.equipment_name).label("equipment_count"),
        case([(schemas.Charting.date <= week_ago, False)], else_=True).label("within_a_week"),
    )

    data = chart_filter(data, filters, start_date, period, cause, name)

    data = data.group_by(schemas.Charting.date).all()

    return data


@router.get("/get_equipment_date", response_model=list[models.Charting_Area])
def get_filtered_area(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    filter: str,
):
    filter = json.loads(filter)

    data = (
        db.query(
            schemas.Charting.area_name,
            schemas.Charting.circuit,
            schemas.Charting.time_usage_code,
        )
        .group_by(schemas.Charting.area_name)
        .group_by(schemas.Charting.circuit)
        .group_by(schemas.Charting.time_usage_code)
    )
    if "regionSelected" in filter:
        data = data.filter(schemas.Charting.region_name.in_(filter["regionSelected"]))
    if "areaSelected" in filter:
        data = data.filter(schemas.Charting.area_name.in_(filter["areaSelected"]))
    if "circuitSelected" in filter:
        data = data.filter(schemas.Charting.circuit.in_(filter["circuitSelected"]))
    if "timeUsageSelected" in filter:
        data = data.filter(schemas.Charting.time_usage_code.in_(filter["timeUsageSelected"]))

    return data.all()


class ChartREMS(BaseModel):
    event_id: str = Field(None, alias="EventID")
    event_datetime: dt.datetime = Field(None, alias="EventDateTime")
    last_comment: str = Field(None, alias="LastComment")
    functional_location: str = Field(None, alias="FunctionalLocation")
    fleet_type: str = Field(None, alias="FleetType")
    model: str = Field(None, alias="Model")
    equipment_name: str = Field(None, alias="EquipmentName")
    site: str = Field(None, alias="Site")
    floc6: str = Field(None, alias="FLOC6")
    floc7: str = Field(None, alias="FLOC7")
    floc8: str = Field(None, alias="FLOC8")
    event_duration: float = Field(None, alias="EventDuration")

    def get_sql():
        return """
            SELECT
            "Event"."EventID",
            "Event"."EventDateTime",
            "Event"."LastComment",
            "Event"."FunctionalLocation",
            "EquipmentType"."EquipmentDescription" as "FleetType",
            "Equipment"."EquipmentModel" as "Model",
            "Event"."Equipment" as "EquipmentName",
            "Site"."SiteDescription" as "Site",
            RIGHT(LEFT("Event"."FunctionalLocation",25),6) as "FLOC6",
            CASE WHEN LENGTH("Event"."FunctionalLocation") > 26 THEN RIGHT(LEFT("Event"."FunctionalLocation",31),5) END "FLOC7",
            CASE WHEN LENGTH("Event"."FunctionalLocation") > 32 THEN RIGHT(LEFT("Event"."FunctionalLocation",37),5) END "FLOC8",
            DATEDIFF(sec,"EventDateTime",(ifnull("EventClosedDateTime", "SystemClosedDate")))/3600 as "EventDuration"

            FROM "EDW"."STG_REMS"."Event"

            LEFT OUTER JOIN "EDW"."STG_REMS"."EquipmentType" ON "Event"."EquipmentTypeCode" = "EquipmentType"."EquipmentTypeCode"
            LEFT OUTER JOIN "EDW"."STG_REMS"."Equipment" ON LEFT("Event"."FunctionalLocation",18) = "Equipment"."FunctionalLocation"
            LEFT OUTER JOIN "EDW"."STG_REMS"."SubSite" ON "Event"."SubSiteCode" = "SubSite"."SubSiteCode"
            LEFT OUTER JOIN "EDW"."STG_REMS"."Site" ON "SubSite"."SiteCode" = "Site"."SiteCode"

            WHERE  "EventDateTime" > DATEADD(MONTH, -18, CURRENT_DATE)
            AND "Event"."EffectiveToDate" IS NULL
            AND "Event"."FunctionalLocation" IS NOT NULL
            AND "Event"."EventTypeCode" = 'Unscheduled'
            AND "EquipmentType"."EffectiveToDate" IS NULL
            AND "Equipment"."EffectiveToDate" IS NULL
            AND "SubSite"."EffectiveToDate" IS NULL
            AND "Site"."EffectiveToDate" IS NULL
            AND "Event"."StatusCode" != 'CANCEL'
            AND LEFT("Event"."FunctionalLocation",3) != 'FMG'
        """


def run_snowflake_query_chart_rems(db, model, **kwargs):
    sql = model.get_sql(**kwargs)

    raw = db.execute(sql)

    results = raw.fetchall()
    result_list = []
    for x in results:
        item = model()
        item.event_id = x[0]
        item.event_datetime = x[1]
        item.last_comment = x[2]
        item.functional_location = x[3]
        item.fleet_type = x[4]
        item.model = x[5]
        item.equipment_name = x[6]
        item.site = x[7]
        item.floc6 = x[8]
        item.floc7 = x[9]
        item.floc8 = x[10]
        item.event_duration = x[11]

        result_list.append(item)

    return result_list


@router.post("/fetch_rems")
def get_chart_rems(
    *,
    db=Depends(utils.get_db),
    sf_db=Depends(utils.get_sf_db),
):
    data = run_snowflake_query_chart_rems(sf_db, ChartREMS)
    if len(data) > 0:
        crud.charting_rems.delete_all(db)
        for i in data:
            db.add(
                schemas.ChartingREMS(
                    event_id=i.event_id,
                    event_datetime=i.event_datetime,
                    last_comment=i.last_comment,
                    functional_location=i.functional_location,
                    fleet_type=i.fleet_type,
                    model=i.model,
                    equipment_name=i.equipment_name,
                    site=i.site,
                    floc6=i.floc6,
                    floc7=i.floc7,
                    floc8=i.floc8,
                    event_duration=i.event_duration,
                )
            )
        db.commit()


def filter_query(query, filters, limit=None, only_date=False, return_query=False):
    if "startDate" in filters:
        start_date = dt.datetime.strptime(filters["startDate"], "%Y-%m-%dT%H:%M:%S.%fz").date()
        query = query.filter(schemas.ChartingREMS.event_datetime >= start_date)
    if "endDate" in filters:
        end_date = dt.datetime.strptime(filters["endDate"], "%Y-%m-%dT%H:%M:%S.%fz").date()
        query = query.filter(schemas.ChartingREMS.event_datetime <= end_date)
    if "site" in filters:
        query = query.filter(schemas.ChartingREMS.site == filters["site"][0])
    if "fleeType" in filters:
        query = query.filter(schemas.ChartingREMS.fleet_type == filters["fleeType"][0])
    if "model" in filters:
        query = query.filter(schemas.ChartingREMS.model == filters["model"])
    if "floc6" in filters:
        query = query.filter(schemas.ChartingREMS.floc6 == filters["floc6"])
    if "floc7" in filters:
        query = query.filter(schemas.ChartingREMS.floc7 == filters["floc7"])
    if "floc8" in filters:
        query = query.filter(schemas.ChartingREMS.floc8 == filters["floc8"])
    if limit:
        query = query.limit(limit)
    if return_query:
        return query
    return query.all()


@router.get("/get_floc67")
def get_floc(*, db=Depends(utils.get_db), filters: str = None):
    filters = json.loads(filters)
    floc7_1 = []
    floc7_2 = []
    floc7_3 = []

    floc6 = (
        db.query(
            schemas.ChartingREMS.floc6.label("floc"),
            func.coalesce(func.sum(schemas.ChartingREMS.event_duration), 0).label("duration"),
            func.count(
                case(
                    [(schemas.ChartingREMS.floc6 != None, schemas.ChartingREMS.floc6)],
                    else_=func.upper("Just some random text"),
                )
            ).label("count"),
            func.lower("floc6").label("name"),
        )
        .group_by(schemas.ChartingREMS.floc6)
        .order_by(desc("duration"))
    )
    floc6 = filter_query(floc6, filters, 10)

    if len(floc6) >= 1:
        floc7_1 = (
            db.query(
                schemas.ChartingREMS.floc7.label("floc"),
                func.coalesce(func.sum(schemas.ChartingREMS.event_duration), 0).label("duration"),
                func.count(
                    case(
                        [(schemas.ChartingREMS.floc7 != None, schemas.ChartingREMS.floc7)],
                        else_=func.upper("Just some random text"),
                    )
                ).label("count"),
                func.lower("floc7_1").label("name"),
            )
            .filter(schemas.ChartingREMS.floc6 == floc6[0].floc)
            .group_by(schemas.ChartingREMS.floc7)
            .order_by(desc("duration"))
        )

        floc7_1 = filter_query(floc7_1, filters, 5)

    if len(floc6) >= 2:
        floc7_2 = (
            db.query(
                schemas.ChartingREMS.floc7.label("floc"),
                func.coalesce(func.sum(schemas.ChartingREMS.event_duration), 0).label("duration"),
                func.count(
                    case(
                        [(schemas.ChartingREMS.floc7 != None, schemas.ChartingREMS.floc7)],
                        else_=func.upper("Just some random text"),
                    )
                ).label("count"),
                func.lower("floc7_2").label("name"),
            )
            .filter(schemas.ChartingREMS.floc6 == floc6[1].floc)
            .group_by(schemas.ChartingREMS.floc7)
            .order_by(desc("duration"))
        )

        floc7_2 = filter_query(floc7_2, filters, 5)

    if len(floc6) >= 3:
        floc7_3 = (
            db.query(
                schemas.ChartingREMS.floc7.label("floc"),
                func.coalesce(func.sum(schemas.ChartingREMS.event_duration), 0).label("duration"),
                func.count(
                    case(
                        [(schemas.ChartingREMS.floc7 != None, schemas.ChartingREMS.floc7)],
                        else_=func.upper("Just some random text"),
                    )
                ).label("count"),
                func.lower("floc7_3").label("name"),
            )
            .filter(schemas.ChartingREMS.floc6 == floc6[2].floc)
            .group_by(schemas.ChartingREMS.floc7)
            .order_by(desc("duration"))
        )

        floc7_3 = filter_query(floc7_3, filters, 5)

    return models.Charting_Floc(floc6=floc6, floc7_1=floc7_1, floc7_2=floc7_2, floc7_3=floc7_3)


@router.get("/get_floc_item", response_model=models.Floc_All_Items)
def get_floc_item(*, db=Depends(utils.get_db), id: int = None):
    return crud.charting_rems.get(db, id)


def extract_info(query):
    ids = []
    for item in query:
        ids.append(
            models.Charting(
                id=item.id, date=item.date, problem=item.problem, start_time=item.start_time
            )
        )

    return ids


@router.get("/get_charting_items", response_model=list[models.Charting])
def get_charting_items(*, db=Depends(utils.get_db), keys: str = None):
    keys = json.loads(keys)

    # -------------------------------------------
    # When the length greater than 1 then only return the ids array
    # -------------------------------------------
    if len(keys["date"]) > 1:
        ids = []
        for index in range(len(keys["date"])):
            date = dt.datetime.strptime(keys["date"][index], "%d/%m/%Y").date()
            tomorrow = date + dt.timedelta(days=1)
            query = (
                db.query(
                    schemas.Charting,
                    # func.upper("Just some random text")
                )
                .filter(schemas.Charting.date >= date)
                .filter(schemas.Charting.date < tomorrow)
                .filter(schemas.Charting.problem == keys["problem"][index])
                .filter(schemas.Charting.action == keys["action"][index])
                .filter(schemas.Charting.circuit == keys["circuit"][index])
                .all()
            )
            ids = [*extract_info(query), *ids]
        ids = sorted(ids, key=lambda i: i.date, reverse=False)
        return ids
    else:
        keys["date"] = dt.datetime.strptime(keys["date"][0], "%d/%m/%Y").date()
        keys["tomorrow"] = keys["date"] + dt.timedelta(days=1)

        return (
            db.query(
                schemas.Charting,
            )
            .filter(schemas.Charting.date >= keys["date"])
            .filter(schemas.Charting.date < keys["tomorrow"])
            .filter(schemas.Charting.problem == keys["problem"][0])
            .filter(schemas.Charting.action == keys["action"][0])
            .filter(schemas.Charting.circuit == keys["circuit"][0])
            .all()
        )


@router.get("/get_floc8_table", response_model=list[models.Charting_Floc_Table])
def get_floc8_table(
    *,
    db=Depends(utils.get_db),
    floc6: str = None,
    floc7: str = None,
    floc8: str = None,
    floc6_table: bool = None,
    filters: str = None,
):
    filters = json.loads(filters)

    # floc6_none_only = False
    floc7_none_only = False
    floc8_none_only = False
    if floc6 and floc6[:7].upper() == "NO FLOC":
        floc6 = ""
        # floc6_none_only = True
    if floc7 and floc7[:7].upper() == "NO FLOC":
        floc7 = None
        floc7_none_only = True
    if floc8 and floc8[:7].upper() == "NO FLOC":
        floc8 = None
        floc8_none_only = True

    floc8_table = (
        db.query(schemas.ChartingREMS)
        .filter(schemas.ChartingREMS.floc6 == floc6)
        .order_by(schemas.ChartingREMS.event_duration.desc())
    )
    if floc6_table:
        if floc6 == None:
            floc8_table = (
                db.query(schemas.ChartingREMS)
                .filter(schemas.ChartingREMS.floc6 == "")
                .order_by(schemas.ChartingREMS.event_duration.desc())
            )
            return filter_query(floc8_table, filters)
        floc8_table.filter(schemas.ChartingREMS.floc6 == floc6)
        return filter_query(floc8_table, filters)

    if floc7:
        floc8_table = floc8_table.filter(
            func.upper(schemas.ChartingREMS.floc7) == func.upper(floc7)
        )
    if floc8:
        floc8_table = floc8_table.filter(
            func.upper(schemas.ChartingREMS.floc8) == func.upper(floc8)
        )

    # if floc6_none_only:
    #     floc8_table = floc8_table.filter(schemas.ChartingREMS.floc6.is_(None))
    if floc7_none_only:
        floc8_table = floc8_table.filter(schemas.ChartingREMS.floc7.is_(None))
    if floc8_none_only:
        floc8_table = floc8_table.filter(schemas.ChartingREMS.floc8.is_(None))

    floc8_table = filter_query(floc8_table, filters)

    return floc8_table


@router.get("/get_floc7_top10", response_model=list[models.Charting_Floc8])
def get_floc7_top10(
    *,
    db=Depends(utils.get_db),
    floc6: str = None,
    floc6_table: bool = None,
    filters: str = None,
):
    filters = json.loads(filters)

    if floc6_table and floc6.lower() == "no floc6":
        floc6 = ""

    floc8s = (
        db.query(
            schemas.ChartingREMS.floc7.label("floc"),
            func.coalesce(func.sum(schemas.ChartingREMS.event_duration), 0).label("duration"),
            func.count(
                case(
                    [(schemas.ChartingREMS.floc7 != None, schemas.ChartingREMS.floc7)],
                    else_=func.upper("Just some random text"),
                )
            ).label("count"),
            func.lower("floc7").label("name"),
            func.upper(floc6).label("floc6"),
        )
        .group_by(schemas.ChartingREMS.floc7)
        .filter(schemas.ChartingREMS.floc6 == floc6)
        .order_by(desc("duration"))
    )
    floc8s = filter_query(floc8s, filters, 10)

    return floc8s


@router.get("/get_floc8", response_model=list[models.Charting_Floc8])
def get_floc8(
    *, db=Depends(utils.get_db), floc6: str = None, floc7: str = None, filters: str = None
):
    is_none = (
        lambda f: schemas.ChartingREMS.floc7.is_(None)
        if f[:7] == "NO FLOC"
        else func.upper(schemas.ChartingREMS.floc7) == func.upper(f)
    )

    floc6_filter = [func.upper(schemas.ChartingREMS.floc6) == func.upper(floc6)]
    if floc6 == "NO FLOC6":
        floc6_filter = [schemas.ChartingREMS.floc6 == ""]
    filters = json.loads(filters)
    floc8 = (
        db.query(
            schemas.ChartingREMS.floc8.label("floc"),
            func.sum(func.coalesce(schemas.ChartingREMS.event_duration, 0)).label("duration"),
            func.count(
                case(
                    [(schemas.ChartingREMS.floc8 != None, schemas.ChartingREMS.floc8)],
                    else_=func.upper("No Floc"),
                )
            ).label("count"),
            func.lower("floc8").label("name"),
            func.upper(floc6).label("floc6"),
            func.upper(floc7).label("floc7"),
        )
        .filter(*floc6_filter)
        .filter(is_none(floc7))
        .group_by(schemas.ChartingREMS.floc8)
        .order_by(desc("duration"))
    )
    floc8 = filter_query(floc8, filters, 10)
    return floc8


@router.get("/get_filter_rems_options", response_model=models.Charting_Filter_REMS)
def get_filter_options_rems(*, db=Depends(utils.get_db), filters: str = None):
    filters = json.loads(filters)

    sites = (
        db.query(
            schemas.ChartingREMS.site.label("name"),
            func.count(schemas.ChartingREMS.site).label("count"),
        )
        .group_by(schemas.ChartingREMS.site)
        .order_by(desc("count"))
    )
    if "site" in filters:
        del filters["site"]
    sites = filter_query(sites, filters, only_date=False)

    flee_types = (
        db.query(
            schemas.ChartingREMS.fleet_type.label("name"),
            func.count(schemas.ChartingREMS.fleet_type).label("count"),
        )
        .group_by(schemas.ChartingREMS.fleet_type)
        .order_by(desc("count"))
    )
    if "fleeType" in filters:
        del filters["fleeType"]
    flee_types = filter_query(flee_types, filters, only_date=False)

    _models = (
        db.query(
            schemas.ChartingREMS.model.label("name"),
            func.count(schemas.ChartingREMS.model).label("count"),
        )
        .group_by(schemas.ChartingREMS.model)
        .order_by(desc("count"))
    )
    # if "model" in filters:
    #     del filters["model"]
    _models = filter_query(_models, filters, only_date=False)

    floc6s = (
        db.query(
            schemas.ChartingREMS.floc6.label("name"),
            func.count(schemas.ChartingREMS.floc6).label("count"),
        )
        .group_by(schemas.ChartingREMS.floc6)
        .order_by(desc("count"))
    )
    # if "floc6" in filters:
    #     del filters["floc6"]

    floc6s = filter_query(floc6s, filters, only_date=False)

    floc7s = (
        db.query(
            schemas.ChartingREMS.floc7.label("name"),
            func.count(schemas.ChartingREMS.floc7).label("count"),
        )
        .group_by(schemas.ChartingREMS.floc7)
        .order_by(desc("count"))
    )

    # if "floc7" in filters:
    #     del filters["floc7"]
    floc7s = filter_query(floc7s, filters, only_date=False)

    floc8s = (
        db.query(
            schemas.ChartingREMS.floc8.label("name"),
            func.count(schemas.ChartingREMS.floc8).label("count"),
        )
        .group_by(schemas.ChartingREMS.floc8)
        .order_by(desc("count"))
    )
    # if "floc8" in filters:
    #     del filters["floc8"]
    floc8s = filter_query(floc8s, filters, only_date=False)

    return models.Charting_Filter_REMS(
        sites=sites,
        flee_types=flee_types,
        models=_models,
        floc6s=floc6s,
        floc7s=floc7s,
        floc8s=floc8s,
    )


@router.post("/init")
def init(
    *,
    db=Depends(utils.get_db),
    sf_db=Depends(utils.get_sf_db),
    valid=Depends(utils.token_auth),
):
    # print("running 1/5 ingest_equipment")
    # ingest_equipment(db=db, db_sf=db_sf)
    # print("runnig 2/5 ingest_event_details")
    # injest_event_details(db=db, db_sf=db_sf)
    # print("running 3/5 ingest_defect_codes")
    # ingest_defect_codes(db=db)
    print("\n\n\nrunning 4/5 get_chart_rems\n\n\n")
    get_chart_rems(db=db, sf_db=sf_db)
    print("\n\n\nrunning 5/5 get_chart_data\n\n\n")
    get_chart_data(db=db, sf_db=sf_db)


@router.delete("/delete")
def delete_dashboard(
    *,
    db=Depends(utils.get_db),
):
    crud.dashboard.delete_all(db)


# This is to check if an investigation is exist for the event ids
@router.post("/check_event_ids")
def check_event_ids(
    *,
    event_ids: list[int],
    db=Depends(utils.get_db),
):
    event_ids = list(set(event_ids))
    has_invest = []

    for id in event_ids:
        result = (
            db.query(schemas.APLUS_Selected_Event_Details_Association)
            .filter(schemas.APLUS_Selected_Event_Details_Association.event_id == id)
            .all()
        )
        if len(result) > 0:
            has_invest.append(id)

    return has_invest
