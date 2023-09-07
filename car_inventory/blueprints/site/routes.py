from flask import Blueprint, render_template, request, flash, redirect

#internal imports
from car_inventory.models import Car, db, car_schema, cars_schema 
from car_inventory.forms import CarForm


site = Blueprint('site', __name__, template_folder='site_templates') 



@site.route('/')
def shop():

    shop = Car.query.all()

    return render_template('shop.html', shop=shop) #basically displaying our shop.html page

#create our CREATE route
@site.route('/shop/create', methods=['GET','POST'])
def create():

    createform = CarForm()

    if request.method == 'POST' and createform.validate_on_submit():

        try:
            model = createform.model.data
            make = createform.make.data
            year = createform.year.data
            color = createform.color.data
            desc = createform.description.data
            image = createform.image.data
            price = createform.price.data
            quantity = createform.quantity.data

            shop = Car(model, make, year, color, price, quantity, image, desc)

            db.session.add(shop)
            db.session.commit()

            flash(f'You have successfully added {color} {year} {make} {model} !', category='success')
            return redirect('/')
        except:
            flash('We were unable to process your request.  Please try again', category='warning')
            return redirect('/shop/create')
        
    return render_template('create.html', form=createform)

#Create our UPDATE route
@site.route('/shop/update/<id>', methods=['GET','POST'])
def update(id):

    updateform = CarForm()
    Car = Car.query.get(id) #Essentially a WHERE clause, WHERE Car.prod_id == id

    if request.method == 'POST' and updateform.validate_on_submit():

        try:
            Car.make = updateform.make.data
            Car.model = updateform.model.data
            Car.year = updateform.year.data
            Car.color = updateform.color.data
            Car.desciption = updateform.description.data
            Car.set_image(updateform.image.data, updateform.model.data, updateform.make.data, updateform.year.data, updateform.color.data) #calling upon that set_image method to set our image!
            Car.price = updateform.price.data
            Car.quantity = updateform.quantity.data

            db.session.commit() #commits the changes

            flash(f'You have successfully updated {Car.color} {Car.year} {Car.make} {Car.model}!', category='success')
            return redirect('/')
        
        except:
            flash('We were unable to process your request.  Please try again', category='warning')
            return redirect('/shop/create')
        
    return render_template('update.html', form=updateform, Car=Car)


@site.route('/shop/delete/<id>')
def delete(id):

    Car = Car.query.get(id)
    db.session.delete(Car)
    db.session.commit()

    return redirect('/')