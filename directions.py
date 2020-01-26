# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, redirect
#from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from twilio.http.http_client import TwilioHttpClient
import googlemaps
from datetime import datetime
from geopy.geocoders import Nominatim


matrixKey = MY_MATRIX_KEY

gmaps = googlemaps.Client(key=MY_GMAPS_KEY)
geolocator = Nominatim(user_agent="specify_your_app_name_here")
location = geolocator.geocode("175 5th Avenue NYC")

# URL = "https://maps.googleapis.com/maps/api/distancematrix/json"

proxy_client = TwilioHttpClient()
proxy_client.session.proxies = {'https': os.environ['https_proxy']}

app = Flask(__name__)


account_sid=MY_SID
account_token=MY_TOKEN
phone=MY_NUMBER

client= Client(account_sid,account_token, http_client=proxy_client)

question = 1

starting = ""

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    content=request.values.get('Body',None)
    contact= request.values.get('From',None)
    resp= MessagingResponse()

    if question == 1:
        response="Welcome to Textination, Where are you right now?"
        globallyChange()
        client.messages.create(to=contact,from_=phone,body=response)

    elif question == 2:
        globallyChange()
        updateStart(content)
        response = "Sounds good, Where would you like to go?"
        client.messages.create(to=contact,from_=phone,body=response)

    elif question == 3:
        globallyChange()
        destination = content
        tempresponse = "Sweet! Let me calculate the fastest route for you"
        client.messages.create(to=contact,from_=phone,body=tempresponse)
        response = str(getDirections(starting,destination))
        result_list = response.split("\n")
        if len(result_list) > 20:
          third = int(len(result_list) / 3)
          twoThird = third * 2
          response1 = '\n'.join(result_list[0:third])
          response2 = '\n'.join(result_list[third:twoThird])
          response3 = '\n'.join(result_list[twoThird:len(result_list)])
          client.messages.create(to=contact,from_=phone,body=response1)
          client.messages.create(to=contact,from_=phone,body=response2)
          client.messages.create(to=contact,from_=phone,body=response3)

        else:
          client.messages.create(to=contact,from_=phone,body=response)

    else:
        response = "Resetting"
        client.messages.create(to=contact,from_=phone,body=response)
        globallyReset()


    return("Worked")




def globallyChange():
    global question
    question = question + 1

def updateStart(content):
    global starting
    starting = content

def updateDest(content):
    global destination
    destination = content


def globallyReset():
    global question
    question = 1

def getStart(starting):

  geolocator = Nominatim(user_agent="Textination")
  location = geolocator.geocode(starting)
  coord01 = location.latitude
  coord02 = location.longitude
  coordFinal = str(coord01) + "," + str(coord02)

  print(coordFinal)
  return str(coordFinal)


def getDest(dest):


    geolocator = Nominatim(user_agent="Textination")
    location = geolocator.geocode(dest)
    coord03 = location.latitude
    coord04 = location.longitude

    coordFinal = str(coord03) + "," + str(coord04)


    print(coordFinal)
    return str(coordFinal)



def getDirections(start, dest):

  try:

    if start != dest:

      gmaps = googlemaps.Client(key=MY_KEY)

      coords_0 = getStart(start)
      coords_1 = getDest(dest)

      # Init client
      # Request directions
      now = datetime.now()
      directions_result = gmaps.directions(coords_0, coords_1, mode="driving", departure_time=now, avoid='tolls')

      legs = directions_result[0].get("legs")
      x = 0
      leg = legs[0]
      steps = leg.get('steps')
      final_string = ""

      for x in range (len(steps)-1):
          value = steps[x].get('html_instructions')
          distan = steps[x].get('distance')
          distan = distan.get('text')
          distan = str(distan)
          value = str(value.replace('<div style="font-size:0.9em">',''))
          value = str(value.replace('/<wbr/>',' '))
          value = str(value.replace('</div>',''))


          newvalue = value.replace("<b>", "")
          newvalue = newvalue.replace("</b>", "")
          newvalue = str(newvalue)
          firstword = newvalue[0:4]
          if firstword == "Head":
              final_string = final_string + str(x+1) + ". " + newvalue + " For " + distan + "\n"
          else:
            final_string = final_string + str(x+1) + ". " + "In " + str(distan) +" " +  str(newvalue) + "\n"

          x = x + 1

      y = len(steps)
      value = steps[x].get('html_instructions')
      distan = steps[x].get('distance')
      distan = distan.get('text')
      distan = str(distan)
      value = str(value.replace('<div style="font-size:0.9em">',''))
      value = str(value.replace('/<wbr/>',' '))
      value = str(value.replace('</div>',''))


      newvalue = value.replace("<b>", "").replace("</b>", "")
      newvalue = str(newvalue)
      firstword = newvalue[0:4]
      if firstword == "Head":
          final_string = final_string + str(y) + ". " + newvalue + " For " + distan + "\n"
      else:
          final_string = final_string + str(y) + ". " "In " + str(distan) +" " +  str(newvalue) + "\n"

      final_string = "\n" + final_string + "\n" + "You have arrived at your destination, thank you for using textination!"

      return final_string

    else:
      return "You are at your destination"

  except:
    return "Location Not Found, Please enter a full address or a well known POI nearby"