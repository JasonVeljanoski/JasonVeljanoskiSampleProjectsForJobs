from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .base import Base


class OrganisationalUnit(Base):
    """
    Static table from snowflake:

        SELECT DISTINCT
            "Tier04FullName" as Area,"Tier05FullName" as Department,"Tier06FullName" as Team
        FROM
            EDW.SELFSERVICE."OrganisationalUnit"

    todo: --
    SELECT DISTINCT
    "Tier04FullName" as Area,"Tier05FullName" as Department,"Tier06FullName" as Team
        FROM
            EDW.SELFSERVICE."OrganisationalUnit"
        WHERE "Tier04FullName" != '' and "Tier05FullName" != ''
        ORDER BY 1,2,3

    * rarely changes
    """

    area = Column(String, nullable=False)
    department = Column(String)
    team = Column(String)

    __table_args__ = (UniqueConstraint("area", "department", "team", name="uq_ou_area_dep_team"),)


class Floc(Base):
    node = Column(String, nullable=False)

    parent_id = Column(Integer, ForeignKey("floc.id"))
    equipment_id = Column(Integer, ForeignKey("equipment.id"))

    equipment = relationship("Equipment", backref="floc", uselist=False)
    parent = relationship("Floc", uselist=False)


class Equipment(Base):
    description = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint("description"),)


# class Equipment(Base):
#     """
#     Static table from snowflake:
#         # todo: --- floc tree idea? that may have an equipment? try round this thought exp out
#         SELECT
#             CASE WHEN LEN("FLOC"."functional_location") = 17 THEN CONCAT("FLOC"."functional_location",' ')
#             WHEN LEN("FLOC"."functional_location") = 24 THEN CONCAT("FLOC"."functional_location",' ')
#             ELSE "FLOC"."functional_location"
#             END as "functional_location",
#             "FLOC"."catalog_profile",
#             "FLOC"."equipment_description",
#             "FLOC"."object_type",
#             "Site"."Description" as "site",
#                     CASE
#                         WHEN "FLOC"."functional_location" LIKE '%-WTRS-%' THEN 'Dewatering'

#                         -- [start]
#                         WHEN "FLOC"."functional_location" LIKE '%MP-HAUL-%' THEN 'Haul Truck'
#                         WHEN "FLOC"."functional_location" LIKE '%MP-EXCV-%' THEN 'Diggers and Drills'
#                         WHEN "FLOC"."functional_location" LIKE '%MP-DRLL-%' THEN 'Diggers and Drills'
#                         WHEN "FLOC"."functional_location" LIKE '%MP-LOAD-%' THEN 'Ancillary'
#                         WHEN "FLOC"."functional_location" LIKE '%MP-DOZR-%' THEN 'Ancillary'
#                         WHEN "FLOC"."functional_location" LIKE '%MP-GRDR-%' THEN 'Ancillary'
#                         -- [end]

#                         ELSE "Department"."Description"
#                     END as "department"

#                     FROM
#                     (
#                 Select  "FunctionalLocation"."FunctionalLocation" as "floc_id",
#                             "FunctionalLocation"."FunctionalLocationLabel" as "functional_location",
#                             CASE WHEN "EquipmentCurrent"."EquipmentDescription" IS NOT NULL THEN "EquipmentCurrent"."EquipmentDescription"
#                             ELSE "FunctionalLocation"."FunctionalLocationDescription" END as "equipment_description",
#                             CASE WHEN "FunctionalLocation"."TechnicalObjectTypeDescription" IS NOT NULL THEN "FunctionalLocation"."TechnicalObjectTypeDescription"
#                             ELSE 'Unknown Object' END as "object_type",
#                             "FunctionalLocation"."CatalogProfile" as "catalog_profile"
#                     from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."FunctionalLocation"
#                     LEFT OUTER JOIN (SELECT * FROM
#                     "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."EquipmentCurrent"
#                     WHERE "EquipmentCurrent"."EffectiveToDate" > CURRENT_DATE) "EquipmentCurrent"
#                     ON "EquipmentCurrent"."FunctionalLocation" = "FunctionalLocation"."FunctionalLocation"
#                     WHERE  "FunctionalLocation"."EffectiveToDate" > CURRENT_DATE
#                     AND "FunctionalLocation"."FunctionalLocationLabel" LIKE '___-__-____-%'
#                     AND "FunctionalLocation"."FunctionalLocationLabel" LIKE '___-MP%'
#                     ) "FLOC"
#                     LEFT OUTER JOIN
#                     (Select "FunctionalLocationLabel" as "functional_location",
#                     "FunctionalLocationDescription" as "Description"
#                     from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."FunctionalLocation"
#                     WHERE "FunctionalLocationLabel" LIKE '___-__'
#                     AND "EffectiveToDate" > CURRENT_DATE
#                     ) "Department" ON "Department"."functional_location" = left("FLOC"."functional_location",6)
#                     LEFT OUTER JOIN
#                     (Select "FunctionalLocationLabel" as "functional_location",
#                     "FunctionalLocationDescription" as "Description"
#                     from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."FunctionalLocation"
#                     WHERE "FunctionalLocationLabel" LIKE '___'
#                     AND "EffectiveToDate" > CURRENT_DATE
#                     ) "Site" ON "Site"."functional_location" = left("FLOC"."functional_location",3)
#                     WHERE "Department"."Description" != 'Non Process Infrastructure'
#                     AND "FLOC"."functional_location" LIKE '___-MP%'
#                     UNION
#                     SELECT
#             CASE WHEN LEN("FLOC"."functional_location") = 17 THEN CONCAT("FLOC"."functional_location",' ')
#             WHEN LEN("FLOC"."functional_location") = 24 THEN CONCAT("FLOC"."functional_location",' ')
#             ELSE "FLOC"."functional_location"
#             END as "functional_location",
#                     "FLOC"."catalog_profile",
#                     "FLOC"."equipment_description",
#                     "FLOC"."object_type",
#                     "Site"."Description" as "site",
#                     CASE WHEN "FLOC"."functional_location" LIKE '%-WTRS-%' THEN 'Dewatering'
#                     ELSE "Department"."Description" END "department"
#                     FROM
#                     (
#                     Select "FunctionalLocationLabel" as "functional_location",
#                     "EquipmentDescription" as "equipment_description",
#                     "TechnicalObjectTypeDescription" as "object_type",
#                     "CatalogProfile" as "catalog_profile"
#                     from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."EquipmentCurrent"
#                     WHERE "FunctionalLocationLabel" LIKE '___-__-____-%'
#                     AND "FunctionalLocationLabel" NOT LIKE '___-MP%'
#                     AND "EffectiveToDate" > CURRENT_DATE
#                     ) "FLOC"
#                     LEFT OUTER JOIN
#                     (Select "FunctionalLocationLabel" as "functional_location",
#                     "LocationDescription" as "Description"
#                     from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."FunctionalLocation"
#                     WHERE "FunctionalLocationLabel" LIKE '___-__'
#                     AND "EffectiveToDate" > CURRENT_DATE
#                     ) "Department" ON "Department"."functional_location" = left("FLOC"."functional_location",6)
#                     LEFT OUTER JOIN
#                     (Select "FunctionalLocationLabel" as "functional_location",
#                     "FunctionalLocationDescription" as "Description"
#                     from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."FunctionalLocation"
#                     WHERE "FunctionalLocationLabel" LIKE '___'
#                     AND "EffectiveToDate" > CURRENT_DATE
#                     ) "Site" ON "Site"."functional_location" = left("FLOC"."functional_location",3)

#     * rarely changes
#     """

#     functional_location = Column(String, nullable=False)
#     equipment_description = Column(String)

#     __table_args__ = (
#         UniqueConstraint(
#             "functional_location", "equipment_description", name="uq_equip_location_description"
#         ),
#     )
