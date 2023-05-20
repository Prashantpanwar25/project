import logging
import time
from flask import Flask, request, jsonify
from settings import invalidChars
from database_con import get_database
from common_tools import check_campaignId_exist, get_hotword_array, update_hotword_array
log = logging.getLogger("hotwordDetection")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(funcName)15s %(levelname)8s - %(lineno)3s - %(message)s",filename = '/var/log/czentrix/hotwordDetection/hotwordapp.log')


#Load the model
from model import Model
model = Model()

app = Flask(__name__)

@app.route('/status')
def home():
    """
    test url for status
    """
    log.debug('status route')
    return {'status': 'running'}

def detect_hotword(text_data, hotword_array):

    log.info("model predicting...")
    found_hotwords = model.predict(text_data, hotword_array) #
    log.info("prediction done")
    log.info(f"found_hotwords: {found_hotwords}")
    return {"hotword":found_hotwords, "status":"ok"}

@app.route("/hotwordDetection/v1",  methods=["POST"])
def detectHotword() -> jsonify:
    """
    This API is used to predict the hotwords. This API takes campaign_id, textData, and some other required fields as input.
    Returns:
        jsonify: The detected hotwords are returned as a list.
    """
    t1 = time.time()
    output = {"status": None, "message": ""}
    data: dict = request.json
    log.info(f"___________________________")
    log.info(f"input packet: {data}")

    try:
        #Validate the request packet
        if data is None or type(data) is not dict:
            log.info('Please provide valid json')
            raise Exception("Please provide valid json")
        
        for keys in data:
            if data[keys]=='':
                output["status"] = "fail"
                output["message"] = "Required field cannot be blank"
                return jsonify(output)

        #pop the required field from the request packet
        text_data = data.pop("textData", None)
        app_id = data.pop("appId", None)
        session_id = data.pop("sessionId", None)
        campaignId = data.pop("campaignId", None)        

        app_flag = False
        session_flag = False
        for item in invalidChars:
            if item in session_id:
                session_flag = False
            if item in app_id:
                app_flag = True
        if session_flag == True or app_flag == True:
            output["status"] = "fail"
            output["message"] = "App Id includes only Numeric values and Alphabets"
            return jsonify(output)

    except KeyError as e:
        log.exception("Please provide valid json")
        output["status"] = "fail"
        output["message"] = str(e)
        return jsonify(output)

    except Exception as e:
        output["status"] = "fail"
        output["message"] = str(e)
        log.exception(f"Error while reading: {e}")
        return jsonify(output)

    #Get Dabatase
    db = get_database()
    collection = db["hotwordDetection"]
    
    if check_campaignId_exist(collection, campaignId):
        hotword_array = get_hotword_array(collection, campaignId)
        resp = detect_hotword(text_data, hotword_array)
    else:
        output["status"] = "fail"
        output["message"] = "campaign_id does not exist"
        return jsonify(output)

    total_time = time.time() - t1
    log.info(f"Total time to compute the request: {total_time}")
    log.info(f"output packet: {resp}")
    return jsonify(resp)


@app.route("/hotwordDetection/campaign",  methods=["POST"])
def storeHotword() -> jsonify:
    """
        This endpoint is used to store the campaign id and hotwords
    """
    log.info("___________________________")
    log.info("request for store hotword")
    output = {"status": None, "message": ""}
    data: dict = request.json
    log.info(f"input packet: {data},")
    log.info("packet validating...")

    try:
        #Validate the request Packet
        if data is None or type(data) is not dict:
            raise Exception("Please provide valid json")

        for keys in data:
            if keys != 'optionalKeys':
                if data[keys]=='':
                    output["status"] = "ERROR"
                    output["message"] = "Required field cannot be blank"
                    log.info(output)
                    return jsonify(output)

        campaign_id = data.pop("campaign_id", None)

        hotwords = data.pop("hotwords", None)
        if type(hotwords) is not list:
            output["status"] = "ERROR"
            output["message"] = "hotwords should be array/list type"
            log.info(output)
            return jsonify(output)
        log.info("packet validated")

        db = get_database()
        collection = db["hotwordDetection"]

        #check campaign_id id is exist in db or not
        if check_campaignId_exist(collection, campaign_id):
            if update_hotword_array(collection, campaign_id, hotwords):
                output["status"] = "ok"
                output["message"] = "request accepted"
            else:
               output["status"] = "ERROR"
               output["message"] = "not able to update"
        else:
            collection.insert_one({"campaign_id":campaign_id, "hotwords":hotwords})
            output["status"] = "ok"
            output["message"] = "request accepted"

    except Exception as e:
        output["status"] = "ERROR"
        output["message"] = str(e)
        log.exception("Error while reading")
        log.info(e)
        return jsonify(output)
    log.info(output)
    return jsonify(output)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=7879)

