import argparse
import shutil
import os
import subprocess
from urllib import request
import requests
import json
import urllib

def run(args):
  #Gets the value from the flags
  field = args.field
  value = args.value
  noexec = args.noexec
  route = 'src/test/groovy'
  dirname = os.path.dirname(__file__)
  if field == "hashtag":
    value = "#"+value

  valueArr = []
  valueArr.append(value)
  valueArr.append("")

  # Getting the bearer token
  path = 'key.pub'
  token=''
  try:
    key_file = open(path,'r')
    key = key_file.read()
    r = requests.post("http://localhost:8081/generate_token_executer", data={'key': key})
    responseObject = json.loads(r.content)
    token = responseObject["access_token"]
  except:
    print("Key file was not found on the repository (Download it from the Muuktest portal)")
 
  auth = {'Authorization': 'Bearer ' + token}

  allowed_fields = ['tag','name', 'hashtag']
  if field in allowed_fields:
    # #Delete the old files
    if os.path.exists("test.rar"):
      os.remove('test.rar')
    shutil.rmtree(route, ignore_errors=True)
    if not os.path.exists(route):
      os.makedirs(route)

    values = {'property': field, 'value': valueArr}
    # This route downloads the scripts by the property.
    url = 'http://localhost:8081/download_byproperty/'
    data = urllib.parse.urlencode(values, doseq=True).encode('UTF-8')

    # now using urlopen get the file and store it locally
    auth_request = request.Request(url,headers=auth, data=data)
    auth_request.add_header('Authorization', 'Bearer '+token)
    response = request.urlopen(auth_request)

    # response = request.urlopen(url,data)
    file = response.read()
    fileobj = open('test.zip',"wb")
    fileobj.write(file)
    fileobj.close()

    # Unzip the file // the library needs the file to end in .rar for some reason
    shutil.unpack_archive('test.zip', extract_dir=route, format='zip')

    if noexec == False :
      #Execute the test
      os.system(dirname + '/gradlew clean test')
  else:
    print(field+': is not an allowed property')




def main():
    parser=argparse.ArgumentParser(description="MuukTest cli to download tests from the cloud")
    parser.add_argument("-p",help="property to search the test for" ,dest="field", type=str, required=True)
    parser.add_argument("-t",help="value of the test or hashtag field" ,dest="value", type=str, required=True)
    parser.add_argument("-noexec",help="(Optional). If set then only download the scripts", dest="noexec", action="store_true")
    parser.set_defaults(func=run)
    args=parser.parse_args()
    args.func(args)

if __name__=="__main__":
	main()
