import logging
import time
from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List
from common_tools import get_hotword_array, update_hotword_array, check_campaignId_exist
from model import Model
from settings import invalidChars
import uvicorn
from database_con import get_database
from schema import HotwordInput,CampaignInput

log = logging.getLogger("hotwordDetection")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(funcName)15s %(levelname)8s - %(lineno)3s - %(message)s",filename = './log/hot_word_app.log'
)

# Load the model
from model import Model
model = Model()

app = FastAPI()

@app.get('/status')
async def home():
    """
    test url for status
    """
    log.debug('status route')
    return {'status': 'running'}

async def detect_hotword(text_data, hotword_array):
    
    log.info("model predicting...")
    found_hotwords = model.predict(text_data, hotword_array)
    log.info("prediction done")
    log.info(f"found_hotwords: {found_hotwords}")
    return {"hotword":found_hotwords, "status":"ok"}

@app.post("/hotwordDetection/v1")
async def detect_hotword_endpoint(data_input: HotwordInput):
    """
    This API is used to predict the hotwords. This API takes campaign_id, textData, and some other required fields as input.
    Returns:
        JSONResponse: The detected hotwords are returned as a list.
    """
    t1 = time.time()
    output = {"status": None, "message": ""}
    d = data_input
    data = data_input.dict()
    print(data)
    log.info(f"data in data is : {d}")
    log.info(f"___________________________")
    log.info(f"input packet: {data}")

    try:
        # Validate the request packet
        # if data is None or type(data) is not dict:
        #     log.info('Please provide valid json')
        #     raise Exception("Please provide valid json")
        
        # for keys in data:
        #     if data[keys]=='':
        #         output["status"] = "fail"
        #         output["message"] = "Required field cannot be blank"
        #         return JSONResponse(output)

        #pop the required field from the request packet

        text_data = data.get("textData")
        app_id = data.get("appId")
        session_id = data.get("sessionId")
        campaign_id = data.get("campaignId")

        # app_flag = False
        # session_flag = False
        # for item in invalidChars:
        #     if item in session_id:
        #         session_flag = False
        #     if item in app_id:
        #         app_flag = True

        # if any(char in invalidChars for char in app_id) or any(char in invalidChars for char in session_id):
        #     output["status"] = "fail"
        #     output["message"] = "App Id includes only Numeric values and Alphabets"
        #     return JSONResponse(output)

    except KeyError as e:
        log.exception("Please provide valid json")
        output["status"] = "fail"
        output["message"] = str(e)
        return JSONResponse(output)

    except Exception as e:
        output["status"] = "fail"
        output["message"] = str(e)
        log.exception(f"Error while reading: {e}")
        return JSONResponse(output)

    # Get Database
    db = get_database()
    collection = db["hotwordDetection"]

    if check_campaignId_exist(collection, campaign_id):
        hotword_array = get_hotword_array(collection, campaign_id)
        resp = await detect_hotword(text_data, hotword_array)
    else:
        output["status"] = "fail"
        output["message"] = "campaign_id does not exist"
        return JSONResponse(output)
    
    total_time = time.time() - t1
    log.info(f"Total time to compute the request: {total_time}")
    log.info(f"output packet: {resp}")
    return JSONResponse(resp)

@app.post("/hotwordDetection/campaign")
async def store_hotword(input_data: CampaignInput):
    """
    This endpoint is used to store the campaign id and hotwords
    """
    log.info("___________________________")
    log.info("request for store hotword")
    output = {"status": None, "message": ""}
    data = input_data.dict()
    log.info(f"input packet: {data},")
    log.info("packet validating...")

    try:
        # Validate the request Packet
        if data is None or type(data) is not dict:
            raise Exception("Please provide valid json")

        for keys in data:
            if keys != 'optionalKeys':
                if data[keys]=='':
                    output["status"] = "ERROR"
                    output["message"] = "Required field cannot be blank"
                    log.info(output)
                    return JSONResponse(output)

        campaign_id = data.get("campaignId")

        hotwords = data.get("hotwords")
        if type(hotwords) is not list:
            output["status"] = "ERROR"
            output["message"] = "hotwords should be array/list type"
            log.info(output)
            return JSONResponse(output)
        log.info("packet validated")

        db = get_database()
        collection = db["hotwordDetection"]
        log.info(campaign_id)
        log.info(collection)
        # Check campaign_id id is exist in db or not
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
        return JSONResponse(output)
    log.info(output)
    return JSONResponse(output)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
