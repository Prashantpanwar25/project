import logging
log = logging.getLogger("hotwordDetection")

def check_campaignId_exist(collection, campaignId):
    if collection.count_documents({"campaign_id":campaignId}) > 0:
        log.info("campaignId is exist")
        return True
    else:
        log.info("campaignId is not exist")
        return False

def get_hotword_array(collection, campaignId):
    hotword_arary = collection.find({"campaign_id": campaignId}).next()["hotwords"]
    return hotword_arary

def update_hotword_array(collection, campaignId, hotwords_array):
    try:
        filter = { 'campaign_id': campaignId}
        newvalues = { "$set": { 'hotwords': hotwords_array}}
        collection.update_one(filter, newvalues)
        return True
    except Exception as e:
        log.info("Not able to update",e)
        return False

def merge_hotword_array(array1, array2):
    log.info(array1)
    log.info(array2)
    return list(set(array1 + array2))
