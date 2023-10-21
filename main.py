#imports
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm

#-----------------------------------------------------------------------------------------------------#



#FLASK_KEY" is the name of your environment variable.
# so Flask key is a variable that is equal to the actaul password ,
#  so instead of typing the password , we put the variable ,
#  and then acess the password just on our pc through the os library ! 



#-----------------------------------------------------------------------------------------------------#


app = Flask(__name__)
import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
ckeditor = CKEditor(app)
Bootstrap5(app)



# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# For adding random avatar profile images to the comment section
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get("DB_URI", "sqlite:///cafes.db")  
db = SQLAlchemy()
db.init_app(app)

#-----------------------------------------------------------------------------------------------------#


# CONFIGURE TABLES
class CafesList(db.Model):
    __tablename__ = "cafe"
    id = db.Column(db.Integer, primary_key=True)
     # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    name =db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets =db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.String(250), nullable=False)
    has_wifi = db.Column(db.String(250), nullable=False)
    can_take_calls = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    coffee_price =  db.Column(db.Integer, nullable=False)
     # Parent relationship to the comments
    comments = relationship("Comment", back_populates="parent_post")
    
    
#-----------------------------------------------------------------------------------------------------#



# Create a User table for all your registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    # This will act like a list of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("CafesList", back_populates="author")
    # Parent relationship: "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")


#-----------------------------------------------------------------------------------------------------#


# Create a table for the comments on the blog posts
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    # Child relationship:"users.id" The users refers to the tablename of the User class.
    # "comments" refers to the comments property in the User class.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    # Child Relationship to the CafesList
    coffe_id = db.Column(db.Integer, db.ForeignKey("cafe.id"))
    parent_post = relationship("CafesList", back_populates="comments")


#-----------------------------------------------------------------------------------------------------#



with app.app_context():
    db.create_all()

#-----------------------------------------------------------------------------------------------------#


# Create an admin-only decorator , which will only allow the admin to do a certain linked function !
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


#-----------------------------------------------------------------------------------------------------#

#Show the welcome page that is presented in the index.html page along with the nav bar and footer ! 
@app.route("/")
def home():
    return render_template("index.html")

#-----------------------------------------------------------------------------------------------------#



#show the coffes list in a separate page inorder to be viewed by the User!

@app.route('/Cafes')
def show_cafes_list():
    result = db.session.execute(db.select(CafesList))
    cafes = result.scalars().all()
    return render_template("show_all_cofes.html", all_cafes=cafes, current_user=current_user ,ability_to_view=True)


#-----------------------------------------------------------------------------------------------------#


# show the requested cofe details !
@app.route("/coffe/<int:coffee_id>", methods=["GET", "POST"])
def show_cafe_details(coffee_id):
    #get the coffee from the database according to the id provided ! 
    requested_coffee = db.get_or_404(CafesList, coffee_id)
    # Add the CommentForm to the route , to show the comments on that specific coffee !
    comment_form = CommentForm()
    # Only allow logged-in users to comment on presented coffe !
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        #when the user see the post details , if he put a comment using ckeditor , and submit the comment , then save that comment
        # that is related to the coffes post we have commented on  
        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_coffee #the coffe we want to comment on ! 
        )

        db.session.add(new_comment)
        db.session.commit()

    return render_template("show_coffe_details.html", selected_coffee=requested_coffee,
                                                      current_user=current_user,
                                                      form=comment_form)


#-----------------------------------------------------------------------------------------------------#

# Use a decorator so only an admin user can create new posts
@app.route("/new-post", methods=["GET", "POST"])
def add_new_coffee():
        form = CreatePostForm()
        if form.validate_on_submit():

            #the user have to login or register in order to have the ability to add to the database
            if not current_user.is_authenticated:
                    flash("You need to login or register to Add Your Best Coffe!.")
                    return redirect(url_for("login"))

            #adding the new coffee post with its detail(we get from the create post form) to the database,
            #  inorder to be executed in the coffees list in the next time !
            #else: add what he entered!
            new_coffee = CafesList(
                name=form.name.data,
                map_url=form.map_url.data,
                img_url=form.img_url.data,
                location=form.location.data,
                has_sockets=form.has_sockets.data,
                has_toilet=form.has_toilet.data,
                has_wifi=form.has_wifi.data,
                can_take_calls=form.can_take_calls.data,
                seats=form.seats.data,
                coffee_price=form.coffee_price.data,
                author=current_user)
                

                
            db.session.add(new_coffee)
            db.session.commit()
            return redirect(url_for("show_cafes_list"))
        

        return render_template("add_coffee.html",
                            form=form,
                            current_user=current_user)



#-----------------------------------------------------------------------------------------------------#


# Use a decorator so only an admin user can edit a post
@app.route("/edit_coffe_post/<int:coffee_id>", methods=["GET", "POST"])
def edit_coffe_post(coffee_id):

    coffe_post = db.get_or_404(CafesList, coffee_id)
    
    #fill the edit form we want to send to the add.html page,
    #  with data of the post we want to edit to avoid repetition !
   
    edit_form = CreatePostForm(
                    name=coffe_post.name,
                    map_url=coffe_post.map_url,
                    img_url=coffe_post.img_url,
                    location=coffe_post.location,
                    has_sockets=coffe_post.has_sockets,
                    has_toilet=coffe_post.has_toilet,
                    has_wifi=coffe_post.has_wifi,
                    can_take_calls=coffe_post.can_take_calls,
                    seats=coffe_post.seats,
                    coffee_price=coffe_post.coffee_price
                     )



    #editing the data sended again from the edit form in the database special for that post ,
    #  or we are reforming the dtata related to that post !
    if edit_form.validate_on_submit():
    
        coffe_post.name=edit_form.name.data,
        coffe_post.map_url=edit_form.map_url.data,
        coffe_post.img_url=edit_form.img_url.data,
        coffe_post.location=edit_form.location.data,
        coffe_post.has_sockets=edit_form.has_sockets.data,
        coffe_post.has_toilet=edit_form.has_toilet.data,
        coffe_post.has_wifi=edit_form.has_wifi.data,
        coffe_post.can_take_calls=edit_form.can_take_calls.data,
        coffe_post.seats=edit_form.seats.data,
        coffe_post.coffee_price=edit_form.coffee_price.data,
        coffe_post.author = current_user
  

        db.session.commit()
        return redirect(url_for("show_cafe_details", coffee_id=coffe_post.id))
    
    return render_template("add_coffee.html", form=edit_form, is_edit=True, current_user=current_user)

#-----------------------------------------------------------------------------------------------------#





# Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:coffee_id>")
@admin_only
def delete_coffee(coffee_id):
    coffee_to_delete = db.get_or_404(CafesList, coffee_id)
    db.session.delete(coffee_to_delete)
    db.session.commit()
    return redirect(url_for('show_cafes_list'))



#-----------------------------------------------------------------------------------------------------#


#Managing Users and Authentication! 




# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if the user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("show_cafes_list"))
    return render_template("register.html", form=form, current_user=current_user)


#-----------------------------------------------------------------------------------------------------#




@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('show_cafes_list'))

    return render_template("login.html", form=form, current_user=current_user)

#-----------------------------------------------------------------------------------------------------#


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('show_cafes_list'))


#-----------------------------------------------------------------------------------------------------#




if __name__ == "__main__":
    app.run(debug=False, port=5001)