from ..utility import db  # Something to note, each dot "." represent a directory level. Just one dot "." will highlight files/folders in models like orders.py and users.py. The more the dots, the higher you move up the level. So if you want to leave the folder, you use 2 dots ".." as the case may be. 

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(), nullable=False)
    is_staff = db.Column(db.Boolean(), default=False)
    is_active = db.Column(db.Boolean(), default=False)
    orders = db.relationship('Order', backref='user', lazy=True) # Getting data from the orders database model

    def __repr__(self): # This represents our db in a string/printable/human readable format. Though what it mostly prints out is the username in this case.
        return f"<User {self.username}>"
    
    # Creating a save function to save our created user when called. WE have to import this in the auth view.py file.
    def save(self):
        db.session.add(self) # Self here acts like a filler, it gives you to opportuity to pass an argument into it without necessarily typing it in. so by calling th function save like this new_user.save(), you are more like saying save(new_user)
        db.session.commit()

    @classmethod
    def get_by_id(self, id): # cls can be anything, we could even change it to self
        # get_by_id(cls, id)
        return self.query.get_or_404(id)