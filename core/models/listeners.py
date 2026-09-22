from sqlalchemy import event
from sqlalchemy.orm import Session
from models.users import UserModel
from models.profiles import ProfileModel


# @event.listens_for(UserModel, "after_insert")
# def create_profile_after_user_insert(mapper, connection, target):
#     db = Session(bind=connection)
#     profile = ConsulteeProfileModel(user_id=target.id)
#     db.add(profile)
#     db.commit()


@event.listens_for(UserModel, "after_delete")
def delete_profile_after_user_delete(mapper, connection, target):
    db = Session(bind=connection)
    profile = db.query(ProfileModel).filter_by(user_id=target.id).first()
    if profile:
        db.delete(profile)
        db.commit()
