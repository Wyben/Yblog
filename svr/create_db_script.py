import hashlib
from app import db
from app.models import User

def main():
    db.create_all()
    email = 'admin@wybengu.com'
    user = User(username='Administrator',
                email= email,
                password='123456',
                admin=True,
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email).hexdigest())
    db.session.add(user)
    db.session.commit()

if __name__ == "__main__":
    main()
