import requests
import json
from pprint import pprint
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions
import time


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    api_key = kwargs.get("api_key")
    print("GET from {} ".format(url))
    try:
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    print(payload)
    response = requests.post(url, params=kwargs, json=payload)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
       
        dealers = json_result["body"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc.get("address"), city=dealer_doc.get("city"), full_name=dealer_doc.get("full_name"),
                                   id=dealer_doc.get("id"), lat=dealer_doc.get("lat"), long=dealer_doc.get("long"),
                                   short_name=dealer_doc.get("short_name"),
                                   st=dealer_doc.get("st"),state=dealer_doc.get("state"), zip=dealer_doc.get("zip"))
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, id):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, id=id)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["body"]["data"]["docs"]
        # For each dealer object
        for review in reviews:
            # Get its content in `doc` object
            dealer_review_doc = review#["doc"]
            # Create a CarDealer object with values in `doc` object
            review_obj = DealerReview(dealership=dealer_review_doc.get("dealership"), name=dealer_review_doc.get("name"), review=dealer_review_doc.get("review"),
                                   id=dealer_review_doc.get("id"), purchase=dealer_review_doc.get("purchase"), purchase_date=dealer_review_doc.get("purchase_date"),
                                   car_make=dealer_review_doc.get("car_make"),
                                   car_model=dealer_review_doc.get("car_model"),car_year=dealer_review_doc.get("car_year"))

            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)

    return results

def get_dealer_by_id_from_cf(url, id):
    json_result = get_request(url, id=id)

    if json_result:
        dealers = json_result["body"]

    
        dealer_doc = dealers[0]
        dealer_obj = CarDealer(address=dealer_doc.get("address"), city=dealer_doc.get("city"),
                                id=dealer_doc.get("id"), lat=dealer_doc.get("lat"), long=dealer_doc.get("long"),  short_name=dealer_doc.get("short_name"),full_name=dealer_doc.get("full_name"),
                                st=dealer_doc.get("st"),state=dealer_doc.get("state"), zip=dealer_doc.get("zip"))
    return dealer_obj

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/1b919340-dc17-41f3-b44c-1c8318a0e82a"
    api_key = "OX1OFFkLEpg0rMJNOcwbsTOAFOAALNIQE18iEfsKtZfS"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze( text=text,features=Features(sentiment=SentimentOptions(targets=[text]))).get_result()
    label=json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    return label



