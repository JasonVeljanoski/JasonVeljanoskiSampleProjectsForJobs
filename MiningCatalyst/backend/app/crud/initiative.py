from app import schemas

from .base import CRUD_Base


# -----------------------------------------
# Association Tables
# -----------------------------------------
class GeneralImprovementInitiativeTriggersAssociation(CRUD_Base[schemas.InitiativeTrigger]):
    pass


general_improvement_initiative_triggers_association = (
    GeneralImprovementInitiativeTriggersAssociation()
)


# ----------------------------------------------------------------------------------------------


class Initiative(CRUD_Base[schemas.Initiative]):
    pass


initiative = Initiative()
