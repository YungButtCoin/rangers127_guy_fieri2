from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, DecimalField
from wtforms.validators import DataRequired, EqualTo, Email 



#create our Login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[ DataRequired(), Email() ])
    password = PasswordField('Password', validators = [ DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


#create our Register Form
class RegisterForm(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    username = StringField('Username', validators=[ DataRequired() ])
    email = StringField('Email', validators=[ DataRequired(), Email() ])
    password = PasswordField('Password', validators = [ DataRequired()])
    verify_password = PasswordField('Confirm Password', validators=[ DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

#Form for adding products
class CarForm(FlaskForm):
    make = StringField('Car Make', validators=[DataRequired()])
    model = StringField('Car Model', validators=[DataRequired()])
    year = StringField('Car Year', validators=[DataRequired()])
    color = StringField('Car Color', validators=[DataRequired()])
    image = StringField('Img Url **Optional**')
    description = StringField('Product Description **Optional**')
    price = DecimalField('Price', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Submit')
