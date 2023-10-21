#imports
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField , SelectField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


#-----------------------------------------------------------------------------------------------------#


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):

    name = StringField("Cafe name", validators=[DataRequired()])

    map_url = StringField(label="Location URL" , validators=[URL()] )

    img_url = StringField("Coffee Image URL", validators=[DataRequired(), URL()])

    location = StringField("Location", validators=[DataRequired()])

    has_sockets = SelectField(label='Has Sockets?' , validators=[DataRequired()] , choices=[('No'),('Pretty Yes')])

    has_toilet = SelectField(label='Has Toilet?' , validators=[DataRequired()] , choices=[('No'),('Pretty Yes')])

    has_wifi = SelectField(label='WiFi Power?' , validators=[DataRequired()] , choices=[('Bad'),('Fairly Good'),('Medium'),('Excelent')])

    can_take_calls = SelectField(label='Can take calls?' , validators=[DataRequired()] , choices=[('No'),('Pretty Yes')])

    seats = StringField("Seats", validators=[DataRequired()])

    coffee_price = StringField("coffe_price", validators=[DataRequired()])

    submit = SubmitField('Submit')


#-----------------------------------------------------------------------------------------------------#



# Create a form to register new users
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Join!")


#-----------------------------------------------------------------------------------------------------#


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


#-----------------------------------------------------------------------------------------------------#


# Create a form to add comments
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Add a Review!", validators=[DataRequired()])
    submit = SubmitField("Submit Review")
