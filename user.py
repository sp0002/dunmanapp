from flask_login import UserMixin

from db import get_db

class User(UserMixin):
    def __init__(self, id_, classid, name, email, profile_pic, admin):
        self.id = id_
        self.classid = classid
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.admin = admin

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], classid=user[1], name=user[2], email=user[3], profile_pic=user[4], admin=user[5]
        )
        return user

    @staticmethod
    def create(id_, classid, name, email, profile_pic, admin):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, classid, name, email, profile_pic, admin) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (id_, classid, name, email, profile_pic, admin),
        )
        db.commit()