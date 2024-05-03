from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from datetime import timedelta,datetime
from dateutil.parser import parse
from wtforms import StringField, PasswordField, validators
from flask import jsonify
from datetime import date, timedelta, datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id= db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))
    
    def init(self, emp_id, email, password):
        self.emp_id= emp_id
        self.email = email
        self.password = password
        
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))


    def _init_(self, email, password):
        self.email = email
        self.password=password
        
        
class AdminLicense(db.Model):
    license_id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    license_name = db.Column(db.String(50))
    vendor_name=db.Column(db.String(50))
    license_model=db.Column(db.String(50))
    license_type=db.Column(db.String(50))
    owner=db.Column(db.String(50))
    user=db.Column(db.String(50))
    project=db.Column(db.String(50))
    price = db.Column(db.Float, nullable=True)
    renew_cost=db.Column(db.Float, nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)  # New column
    renew_date = db.Column(db.Date, nullable=True)

    def _init_(self, admin_id, license_name,price,license_model,license_type,vendor_name,owner,user,project,renew_cost=None,purchase_date=None, renew_date=None):
        self.admin_id = admin_id
        self.license_name = license_name
        self.vendor_name=vendor_name
        self.license_model=license_model
        self.license_type=license_type
        self.owner=owner
        self.user=user
        self.project=project
        self.price = price
        self.renew_cost=renew_cost if renew_cost else None
        self.purchase_date = purchase_date
        self.renew_date = renew_date
        
class License(db.Model):
    l_id = db.Column(db.Integer, primary_key=True)
    emp_id=db.Column(db.String(80), db.ForeignKey('users.emp_id')) 
    license_name = db.Column(db.String(50),db.ForeignKey('admin_license.license_name'))
    technical_lead = db.Column(db.String(50))
    purchase_date = db.Column(db.Date)
    renew_date = db.Column(db.Date)
    price = db.Column(db.Float, nullable=True)  
    license_model=db.Column(db.String(50))
    license_type=db.Column(db.String(50))
    vendor_name=db.Column(db.String(50))
   
    def init(self, emp_id,license_name, technical_lead,purchase_date,renew_date,price,license_model,license_type,vendor_name):
        self.emp_id = emp_id
        self.license_name=license_name
        self.technical_lead= technical_lead
        self.purchase_date= purchase_date
        self.renew_date = renew_date
        self.price=price
        self.license_model=license_model
        self.license_type=license_type
        self.vendor_name=vendor_name
        
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_name= db.Column(db.String(80))
    email = db.Column(db.String(120))
    website_link = db.Column(db.String(80))
    license_name = db.Column(db.String(50),db.ForeignKey('admin_license.license_name'))
    
class LicenseVendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    license_name = db.Column(db.String(50))
    
    def init(self, vendor_name, email, website_link,license_name):
        self.vendor_name= vendor_name
        self.email = email
        self.website_link = website_link
        self.license_name=license_name
        
        

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        password = request.form["passw"]

        found_user = Users.query.filter_by(email=email).first()
        if found_user.email=="admin@gmail.com":
            session.permanent = True
            email = request.form["email"]
            password = request.form["passw"]
            admin = Admin.query.filter_by(email=email, password=password).first()
            if admin:
             if admin.password==password:
                session["admin"] = admin.email
                flash("Login Successful!")
                return redirect(url_for("admin_dashboard"))
             else:
                 flash("Invalid admin credentials!")
       
            

        elif found_user :
            if check_password_hash(found_user.password, password):
                session["email"] = found_user.email
                flash("Login Successful!")
                licenses = AdminLicense.query.all()
                existing_vendors = [vendor[0] for vendor in db.session.query(Vendor.vendor_name).distinct().all()]
                print(existing_vendors)
                print("hi")
                return render_template("display_license.html",licenses=licenses,vendors=existing_vendors,username=found_user.emp_id)
            else:
                flash("Incorrect password!")
        else:
            flash("User not found. Please Ask Admin to register first.")

    return render_template("login.html")

@app.route("/admin")
def index_admin():
    return render_template("admin/adminlogin.html")

@app.route("/adminlogin", methods=["GET", "POST"])
def adminlogin():
    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        password = request.form["passw"]
        admin = Admin.query.filter_by(email=email, password=password).first()
        if admin:
            if admin.password==password:
                session["admin"] = admin.email
                flash("Login Successful!")
                return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials!")
    return render_template("admin/adminlogin.html")


# @app.route("/show_userlicense")
# def show_userlicense():
#     licenses =License.query.all()
#     return render_template("admin/show_userlicense.html", licenses=licenses)

@app.route("/admin_profile")
def admin_profile():
    data ={'email':'admin@gmail.com','password':'admin123'}
    return render_template("admin/admin_profile.html", admin=data)

    


@app.route("/show_adminlicense")
def show_adminlicense():
    licenses =AdminLicense.query.all()
    return render_template("admin/show_adminlicense.html", licenses=licenses)


@app.route("/display_license")
def display_license():
    licenses =AdminLicense.query.all()
    return render_template("display_license.html", licenses=licenses,vendors=existing_vendors)


@app.route("/request_license",methods=["GET", "POST"])
def request_license():
    licenses=AdminLicense.query.all()
    return render_template("display_license.html",licenses=licenses)


@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" in session:
        flash("Login Successful!")
        return render_template("admin/admin_dashboard.html")
    else:
        flash("Please log in as an admin.")
        return redirect(url_for("adminlogin"))
    
    

@app.route('/edit_adminlicense/<int:license_id>', methods=['GET', 'POST'])
def edit_adminlicense(license_id):
    print(id)
    license = AdminLicense.query.get_or_404(license_id)
    print(license)
    if request.method == 'POST':
        license.license_name = request.form['license_name']
        license.price = float(request.form['price'])
        license.vendor_name=request.form["vendor_name"]
        license.owner=request.form["owner"]
        license.user=request.form["user"]
        license.project=request.form["project"]
        license.license_model=request.form["license_model"]
        license.license_type=request.form["license_type"]
        license.renew_cost = float(request.form['renew_cost'])
        purchase_date_str = request.form["purchase_date"]
        renew_date_str = request.form["renew_date"]
        license.purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d").date()
        license.renew_date = datetime.strptime(renew_date_str, "%Y-%m-%d").date()
        db.session.commit()
        flash('License edited successfully', 'success')
        return redirect(url_for('show_adminlicense'))

    return render_template('admin/edit_adminlicense.html', license=license)


@app.route('/delete_adminlicense/<int:license_id>', methods=['GET','POST'])
def delete_adminlicense(license_id):
    license = AdminLicense.query.get_or_404(license_id)
    db.session.delete(license)
    db.session.commit()
    flash('License deleted successfully', 'success')
    return redirect(url_for('show_adminlicense'))

@app.route('/register_vendor', methods=['POST','GET'])
def register_vendor():
    if request.method == "POST":
        vendor_name = request.form.get('vendor_name')
        email = request.form.get('email')
        website_link = request.form.get('website_link')
        license_names = request.form.getlist('license_name')
        print(license_names)
        license_names=list(license_names)
 
        # Loop through each selected license name
        for license_name in license_names:
            # Create a new Vendor record for each license name
            new_vendor = Vendor(vendor_name=vendor_name, email=email, website_link=website_link, license_name=license_name)
            db.session.add(new_vendor)

        # Commit the changes to add vendors
        db.session.commit()

        # Loop through each selected license name again
        for license_name in license_names:
            # Create a new License record for each license name
            new_license = License(vendor_name=vendor_name, license_name=license_name)
            db.session.add(new_license)
        
        # Commit the changes to add licenses
        db.session.commit()
        
        return render_template('admin/create_license.html')
    else:
        return render_template('admin/register_vendor.html')
    
@app.route('/show_vendor')
def show_vendor():
    vendors =Vendor.query.all()
    return render_template("admin/show_vendor.html",vendors=vendors)

@app.route('/edit_vendor/<int:vendor_id>', methods=['GET', 'POST'])
def edit_vendor(vendor_id):
    # Your code to handle editing the vendor
    vendor = Vendor.query.get_or_404(vendor_id)
    return render_template('admin/edit_vendor.html', vendor=vendor)
   
    

@app.route('/delete_vendor/<int:vendor_id>',methods=['POST','GET'])
def delete_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    db.session.delete(vendor)
    db.session.commit()
    flash('Vendor deleted successfully', 'success')
    return redirect(url_for('show_vendor'))

    
@app.route("/logout_admin")
def logout_admin():
    session.pop("admin", None)
    flash("You have been logged out as admin.")
    return redirect(url_for("index_admin"))

@app.route('/update_vendor/<int:vendor_id>', methods=['POST'])
def update_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    vendor.vendor_name = request.form['vendor_name']
    vendor.email = request.form['email']
    vendor.website_link = request.form['website_link']
    vendor.license_name = request.form['license_name']
    db.session.commit()
    return redirect(url_for('show_vendor')) 


@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "email" in session:
        email = session["email"]
    return render_template("user.html", email=email)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']
        hashed_password = generate_password_hash(passw)
        
        if '@' not in mail or '.' not in mail:
            flash('Enter a valid email address', 'error')
            return redirect(url_for('register'))
        
        register = Users(emp_id = uname, email = mail, password = hashed_password)
        db.session.add(register)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route('/display_user', methods=['GET', 'POST'])
def display_user():
    users = Users.query.all()
    return render_template('admin/display_user.html', users=users)

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = Users.query.get_or_404(id)
    if request.method == 'POST':
        # Update user details based on form data
        user.emp_id = request.form['emp_id']
        user.email = request.form['email']
        new_password = request.form['password']
        if new_password:
            hashed_password = generate_password_hash(new_password)
            user.password = hashed_password
        db.session.commit()
        return redirect(url_for('display_user'))
    return render_template('admin/edit_user.html', user=user)

@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    user = Users.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('display_user'))


@app.route("/create_license", methods=["POST","GET"])
def create_license():
    existing_vendors = [vendor[0] for vendor in db.session.query(Vendor.vendor_name).distinct().all()]
    if request.method == "POST":
        print("post")
        admin_id = session.get("admin")
        license_name = request.form["license_name"]
        renew_cost = request.form["renew_cost"]
        price = request.form["price"]
        vendor_name=request.form["vendor_name"]
        owner=request.form["owner"]
        user=request.form["user"]
        project=request.form["project"]
        license_model=request.form["license_model"]
        license_type=request.form["license_type"]
        purchase_date = None
        renew_date = None
        print(license_type)
        
        renew_cost = float(renew_cost) if renew_cost else None
        
        if license_model == "onetime":
            # For one-time purchase, renew_date should be null
            purchase_date = date.today()
            flash(f"License created successfully! Purchase Date: {purchase_date.strftime('%Y-%m-%d')}")
        elif license_model == "subscription":
            # For subscription, set purchase_date to today and renew_date to next year's today
            purchase_date = date.today()
            renew_date = purchase_date.replace(year=purchase_date.year + 1)
            flash(f"License created successfully! Purchase Date: {purchase_date.strftime('%Y-%m-%d')} Renew Date: {renew_date.strftime('%Y-%m-%d')}")

        new_license = AdminLicense(admin_id=admin_id, license_name=license_name, renew_cost=renew_cost, price=price,
                                   vendor_name=vendor_name,user=user,project=project,owner=owner,license_model=license_model,license_type=license_type,
                                   purchase_date=purchase_date, renew_date=renew_date)
        
        db.session.add(new_license)
        db.session.commit()

        flash("License created successfully!")
        return redirect(url_for("create_license"))

    return render_template("admin/create_license.html",vendors=existing_vendors)

#names
@app.route("/get_license_names", methods=["GET"])
def get_license_names():
    selected_vendor = request.args.get("vendor")
    print(selected_vendor)

    # Query AdminLicense directly based on vendor_name
    license_names = Vendor.query.with_entities(Vendor.license_name).filter_by(vendor_name=selected_vendor).distinct().all()
    print(license_names)
    return jsonify([name[0] for name in license_names])
   

   



@app.route('/license_data', methods=['POST', 'GET'])
def license_data():
     admin_licenses = AdminLicense.query.all()
     return render_template('licenses.html', admin_licenses=admin_licenses)
 
 
@app.route('/renew/<int:l_id>', methods=['POST','GET'])
def renew(l_id):
    license = License.query.get(l_id)
    print(license)
    if request.method == 'POST':
        flash('License renewed successfully!')
        return redirect(url_for('dashboard'))
    return render_template('renew.html', license=license)


@app.route("/dashboard",methods=['POST','GET'])
def dashboard():
    if request.method=='POST':
        print("this is dashboard")
        

@app.route('/onetime_purchase/<int:license_id>')
def onetime_purchase(license_id):
    license_details = AdminLicense.query.get(license_id)
    
    if license_details:
        return render_template('onetime.html', license_details=license_details)
    else:
        flash("License details not found.")
        return redirect(url_for('index'))


@app.route('/subscription/<int:license_id>')
def subscription(license_id):
    license_details = AdminLicense.query.get(license_id)
    print(license_details)
    if license_details:
        return render_template('subscription.html',license_details=license_details)
    else:
        flash("License details not found.")
        return redirect(url_for('index'))
    
    
with app.app_context():
    db.create_all()
    admin_user = Admin(email="admin@gmail.com", password="admin123")
    db.session.add(admin_user)
    db.session.commit()
    
if __name__ == "__main__":
    app.run(debug=True)