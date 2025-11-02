from sqlalchemy.orm import Session

from app import utils


def init_db(db: Session):
    pass


init_db(next(utils.get_db()))
