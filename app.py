from flask import Flask, render_template, request
from flask_pymongo import PyMongo
import random
import smtplib
import json
import time

def finder(a):
    if a=='Ertiga':
        index=db.Ertiga
    elif a=='hyundai_verna':
        index=db.hyundai_verna
    elif a=='Kia_Carens':
        index=db.Kia_Carens
    elif a=='Mahindra_XUV_700':
        index=db.Mahindra_XUV_700
    elif a=='Maruti_Baleno':
        index=db.Maruti_Baleno
    elif a=='Ertiga2':
        index=db.Ertiga2
    elif a=='Ertiga3':
        index=db.Ertiga3
    elif a=='Tata_Nexon':
        index=db.Tata_Nexon
    elif a=='Tata_Nexon2':
        index=db.Tata_Nexon2
    elif a=='Maruti_Baleno2':
        index=db.Maruti_Baleno2
    
    return index

def email_save(email,phone_no):
    active_time = time.ctime()
    db.user_name.insert_one({"email":email,"phone_no":phone_no,"active_time":active_time})

def size_check(start,available,valid=False):
    strday = start[3]+start[4]
    strmonth = start[0]+start[1]
    stryear = start[6]+start[7]+start[8]+start[9]
    
    availableday = available[3]+available[4]
    availablemonth = available[0]+available[1]
    availableyear = available[6]+available[7]+available[8]+available[9]
    
    if availableyear <= stryear:
        if availablemonth <= strmonth:
            if availableday < strday:
                valid = True

    return valid   

def date_check(available_list,trip_list,frontend=-1,backend=-2,valid = False):
    for index,i in enumerate(available_list):
        if size_check(trip_list[0],available_list[index][0]):
            if size_check(trip_list[0],available_list[index][1]):
                frontend = index
        if index == len(available_list)-2:
            if size_check(available_list[index+1][0],trip_list[1]):
                    backend = index
        elif size_check(trip_list[0],available_list[index][0]):
            if size_check(trip_list[0],available_list[index][1]):
                    backend = index

    if frontend == backend:
        valid = True

    return valid

def run(car_list,a,num=0):    
    date=[]
    data = car_list[num].find({})
    for i in data:
        date.append([i["tripstart"],i["tripend"]])

    if date_check(date,a):
        return car_list[num]
    else:
        return
    
# run flask here\/
app = Flask(__name__, static_url_path='/static')
app.config["SECRET_KEY"] = '469f4c19a0b489ccb8ff3630fcc762349f1eb868'
app.config["MONGO_URI"] = "mongodb+srv://uditya:Uditya%402004@cluster0.xrfgs2y.mongodb.net/rentalcars"
db = PyMongo(app).db


@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/date', methods=['POST'])
def date():
    global tripstar,tripen
    tripstart =  request.form.get('trip_start')
    tripend = request.form.get('trip_end')
    print(tripstart)

    tripstar=str(tripstart[5])+str(tripstart[6])+'/'+str(tripstart[8])+str(tripstart[9])+'/'+str(tripstart[0])+str(tripstart[1])+str(tripstart[2])+str(tripstart[3])
    tripen=str(tripend[5])+str(tripend[6])+'/'+str(tripend[8])+str(tripend[9])+'/'+str(tripend[0])+str(tripend[1])+str(tripend[2])+str(tripend[3])

# list of cars
    car_list=['Ertiga','hyundai_verna','Kia_Carens','Mahindra_XUV_700','Maruti_Baleno','Ertiga2','Ertiga3','Tata_Nexon','Tata_Nexon2','Maruti_Baleno2']
    car_list_db=[db.Ertiga,db.hyundai_verna,db.Kia_Carens,db.Mahindra_XUV_700,db.Maruti_Baleno,db.Ertiga2,db.Ertiga3,db.Tata_Nexon,db.Tata_Nexon2,db.Maruti_Baleno2]
    trip=[tripstar,tripen]
    
    car=[]
    for i in range(len(car_list_db)):
        if run(car_list_db,trip,num=i) == car_list_db[i]:
           car.append(car_list[i])

    return render_template('dashboard.html',cars=json.dumps(car))

@app.route('/button', methods=['GET','POST'])
def button():
    global car_name
    car_name=''
    if request.method == 'POST':
        click_button = request.form.get('button')
        car_name = click_button
        return render_template('email_verification.html',car=click_button)
    
@app.route('/send_mail', methods=['POST'])
def send_mail():
    global sender_email,sender_phone_no

    sender_email = request.form.get('email')
    sender_phone_no = request.form.get('phone_no')
    email_save(sender_email,sender_phone_no)

    re_send_otp()
    return render_template('otp.html')

@app.route('/re_send_otp', methods=['POST'])
def re_send_otp():
    global otp,server
    otp = random.randint(1111,9999)
    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login("pateluditya2004@gmail.com","xqyfzjwcolimfwtx")
    server.sendmail("pateluditya2004@gmail.com",sender_email,str(otp))

    return render_template('otp.html')


@app.route('/confirm_otp', methods=['POST'])
def confirm_otp():
    global tripen,tripstar
    sender_otp = request.form.get('otp')
    btn=car_name

    if int(sender_otp) == otp:
        enter = {"sender_email":sender_email,"tripstart":tripstar,"tripend":tripen,"sender_phone_no":sender_phone_no}
        finder(btn).insert_one(enter)
        return render_template('payment.html')
    else:
        return render_template('otp.html',status = "otp is wrong")
  
if __name__ == '__main__':
    app.run(debug=True)