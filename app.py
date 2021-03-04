from flask import Flask,jsonify,request
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_jwt import jwt
import datetime


app = Flask(__name__)
cors = CORS(app=app,resources={r"/api/*":{"origins":"*"}})
app.config["MONGO_URI"] = "mongodb://localhost:27017/twigatest"
app.config["SECRET_KEY"] = "2uhebr3u3480ed20dx9awwqixsa9wuqw7eyurhfnwewdyuhdcxw"
mongo = PyMongo(app)
Loaders = mongo.db["Loaders"]
Carriers = mongo.db["Carriers"]
Farms = mongo.db["Farms"]
Users = mongo.db["Users"]
Produce = mongo.db["Produce"]
WeeklyProduce = mongo.db["WeeklyProduce"]


def create_token(data):
    payload = {
        "exp" : datetime.datetime.utcnow() + datetime.timedelta(days=0,minutes=60),
        "iat" : datetime.datetime.utcnow(),
        'sub' : data
    }
    return jwt.encode(payload,app.config.get("SECRET_KEY"),algorithm='HS256')


def decode_token(token):
    try:
        jwt.decode(token,app.config.get("SECRET_KEY"))
        return True
    except:
        return False

@app.route("/api/addloader",methods=["POST"])
def add_loaders():
    Headers = request.headers
    Authenticated = decode_token(Headers["x-access-token"])
    if(Authenticated):
        jsondata = request.json
        loader = jsondata["user"]
        dbdata = {
            "Name":loader["Name"],
            "Id":loader["Id"],
            "DOB":loader["DOB"],
            "Phone":loader["Phone"],
            "Age":20
        }
        try:
            Loaders.insert_one(dbdata)
            return jsonify({"Added":True})
        except:
            return jsonify({"Added":False})
            
@app.route("/api/loader")
def get_loaders(): 
    Headers = request.headers
    Authenticated = decode_token(Headers["x-access-token"])
    if(Authenticated):
        data = Loaders.find()
        dat = list(data)
        resdata = []
        for x in dat:
            resdat ={}
            resdat["Name"] = x["Name"]
            resdat["Phone"] = x["Phone"]
            resdat["Id"] = x["Id"]
            resdat["DOB"] = x["DOB"]
            resdat["Age"] = x["Age"]
            resdata.append(resdat)
        return jsonify(resdata)
    return jsonify({"Auth":False})

@app.route("/api/loader/<string:loader>")
def get_loader(loader):
    Headers = request.headers
    Authenticated = decode_token(Headers["x-access-token"])
    if(Authenticated):
        data = Loaders.find_one({"Name":loader})
        resdat = {
            "Name":data[0]["Name"],
            "Phone":data[0]["Phone"],
            "Id":data[0]["Id"]
        }
        return resdat
    return jsonify({"Auth":False})

@app.route("/api/addcarrier",methods=["POST"])
def carriers():
    Headers = request.headers
    Authenticated = decode_token(Headers["x-access-token"])
    if(Authenticated):
        jsondata = request.json
        carrier = jsondata["user"]
        dbdata = {
            "Name":carrier["Name"],
            "Id":carrier["Id"],
            "DOB":carrier["DOB"],
            "Phone":carrier["Phone"],
            "Age":20
        }
        try:
            Carriers.insert_one(dbdata)
            return jsonify({"Added":True})
        except:
            return jsonify({"Added":False})
    return jsonify({"Auth":False})

@app.route("/api/carrier")
def get_carrier():
    Headers = request.headers
    Authenticated = decode_token(Headers["x-access-token"])
    print("Authenticate:",Authenticated)
    if(Authenticated):
        res = list(Carriers.find())
        resdata = []
        for x in res:
            resdict = {
                "Name":x["Name"],
                "Age":x["Age"],
                "Id":x["Id"],
                "Phone":x["Phone"],
                "DOB":x["DOB"]
            }
            resdata.append(resdict)
        return jsonify(resdata)
    return jsonify({"Auth":False})

@app.route("/api/addfarm",methods=["GET","POST"])
def farm():
    Headers = request.headers
    Authenticated = decode_token(Headers["x-access-token"])
    if(Authenticated):
        jsondata = request.json
        Farm = jsondata["user"]
        farmdata = {
            "Owner":Farm["Name"],
            "Id":Farm["Id"],
            "DOR":Farm["DOR"],
            "Phone":Farm["Phone"],
            "Produce":Farm["Produces"]
        }
        try:
            Farms.insert_one(farmdata)
            return jsonify({"Added":True})
        except:
            return jsonify({"Added":False})
    return jsonify({"Auth":False})

@app.route("/api/farm")
def get_farms():
    Headers = request.headers
    Authenticated = decode_token(Headers["x-access-token"])
    print("Authenticate:",Authenticated)
    if(Authenticated):
        res = list(Farms.find())
        resdata = []
        for x in res:
            resdict = {
            "Owner":x["Owner"],
            "Id":x["Id"],
            "DOR":x["DOR"],
            "Phone":x["Phone"],
            "Produce":x["Produce"]
            }
            resdata.append(resdict)
        return jsonify(resdata)
    return jsonify({"Auth":False})


@app.route("/api/signup",methods=["POST"])
def signup():
    jsondata = request.json
    User = jsondata["user"]
    if(not Users.find_one({"Name":User["Username"]})):
        dbdata = {
            "First":User["FirstName"],
            "Second":User["SecondName"],
            "Email":User["Email"],
            "Username":User["Username"],
            "Password":User["Password"],
            "Id":User["Id"],
            "DOB":User["DOB"],
            "Phone":User["Phone"]
            }
        try:
            Users.insert_one(dbdata)
            return jsonify({"Added":True})
        except:
            return jsonify({"Added":False})
    return jsonify({"UserFound":True})

@app.route("/api/login",methods=["POST"])
def login():
    jsondata = request.json
    User = jsondata["user"]
    loginUser = Users.find_one({"Username":User["Username"]})
    if(loginUser and loginUser["Password"] == User["Password"]):
        resdata = {
            "Id":str(loginUser["_id"]),
            "Username": loginUser["Username"]
        }
        return jsonify({"Auth":True,"Token":create_token(resdata)})
    return jsonify({"Auth":False})
    
@app.route("/api/addproduce",methods=["POST"])
def add_produce():
    Headers = request.headers
    Authenticated = decode_token(Headers["x-access-token"])
    if(Authenticated):
        jsondata = request.json
        DailyProduce = jsondata["produce"]
        casuals = DailyProduce["Casualworkers"]
        loaders = DailyProduce["Loadingworkers"]
        Quantity = DailyProduce["Amount"]
        print(Quantity,int(casuals),int(loaders))
        casualPay = (float(Quantity) * 1.4) /int(casuals)
        loadersPay = (float(Quantity) * 0.2) /int(loaders)
        dbdata = {
            "Date" : DailyProduce["Date"],
            "Area" : DailyProduce["Area"],
            "Produce": DailyProduce["Name"],
            "Quantity" : DailyProduce["Amount"] ,
            "Signature" : DailyProduce["Signator"],
            "Casuals" : casuals,
            "CasualsPay": casualPay,
            "Loaders" : loaders,
            "LoadersPay" : loadersPay
        }
        try:
            WeeklyProduce.insert_one(dbdata)
            Produce.insert_one(dbdata)
            return jsonify({"Added":True})
        except:
            return jsonify({"Added":False})
    return jsonify({"Auth":False})

@app.route("/api/produce")
def get_produce():
    Headers = request.headers
    Authenticated = decode_token(Headers["x-access-token"])
    if(Authenticated):
        produces = list(Produce.find())
        resdata = []
        for produce in produces:
            produceData ={
                "Date": produce["Date"],
                "Quantity": produce["Quantity"],
                "Area" : produce["Area"],
                "Produce" : produce["Produce"],
                "Signator" : produce["Signature"],
                "Casuals" : produce["Casuals"],
                "CasualPay" : produce["CasualsPay"],
                "Loaders" : produce["Loaders"],
                "LoaderPay" : produce["LoadersPay"]
            }
            resdata.append(produceData)
        return jsonify(resdata)
    return jsonify({"Auth":False})

@app.route("/api/weeklyproduce")
def get_weekly_produce():
    Headers = request.headers
    Authenticated = decode_token(Headers["x-access-token"])
    if(Authenticated):
        produces = list(WeeklyProduce.find())
        resdata = []
        for produce in produces:
            produceData ={
                "Date": produce["Date"],
                "Quantity": produce["Quantity"],
                "Area" : produce["Area"],
                "Casuals" : produce["Casuals"],
                "CasualPay" : produce["CasualsPay"],
                "Loaders" : produce["Loaders"],
                "LoaderPay" : produce["LoadersPay"]
            }
            resdata.append(produceData)
        return jsonify(resdata)
    return jsonify({"Auth":False})

@app.route("/api/Subtotal/confirm")
def confirm():
    Headers = request.headers
    Authenticated = decode_token(Headers["x-access-token"])
    Areas = {}
    response =[]
    if(Authenticated):
        produceList = list(WeeklyProduce.find())
        for produce in produceList:
            Areas[produce["Area"]] = {
                "CasualsPay":0,
                "LoadersPay":0
            }
        for produce in produceList: 
            Area = Areas[produce["Area"]]
            Area["CasualsPay"] += produce["CasualsPay"]
            Area["LoadersPay"] += produce["LoadersPay"]
        
        for area in Areas.keys():
            working = Areas[area]
            resobj = {}
            resobj["Area"] = area
            resobj["CasualsPay"] = working["CasualsPay"]
            resobj["LoadersPay"] = working["LoadersPay"]
            response.append(resobj)

        return jsonify(response)
    return jsonify({"Auth":False})


if __name__ == "__main__":
    app.run(debug=True)
