import json
import requests
from requests.auth import HTTPBasicAuth

# Description:
#   This method will call the BS APIs to obtain the latest execution and extract the .  
#   video link that will be uploaded to S3. 
#
# Returns:
#    Nothing. 
def getBSVideo(browser, extraSettingsJson, videoNameFile):
   endPoint = ""
   user_name = ""
   password = ""
   buildName = ""
   if 'browserstack' in extraSettingsJson and 'caps' in extraSettingsJson['browserstack']:
    for cap in extraSettingsJson['browserstack']['caps']:
      project = cap.get('project')
      if project == browser:
         endPoint = "automate/builds.json?limit=10"
         user_name = cap.get("browserstack.username")
         password = cap.get("browserstack.accessKey")
         build_name = extraSettingsJson["organizationName"]
         response = send_browserstack_request(endPoint, user_name, password )
         for build in response:
            if('automation_build' in build and 'name' in build['automation_build']):
               name = build['automation_build']['name']
               tag = build['automation_build']['build_tag']
               if(name == build_name and tag == "selenium" ):
                  build_id = build['automation_build']['hashed_id']
                  endPoint = "automate/builds/" + build_id + "/sessions.json?limit=1"
                  sessionResponse = send_browserstack_request(endPoint, user_name, password)
                  videoLink = sessionResponse[0]['automation_session']['video_url']
                  download_browserstack_video(videoLink, videoNameFile)

# Description:
#   This method downloads the video from the url link provided and
#   saved to local file system. 
#
# Returns:
#    Nothing. 
def download_browserstack_video(url: str, file_path: str):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Open a writable file to save the downloaded content
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print('download_browserstack_video - File downloaded successfully:', file_path)
    except Exception as e:
        print('download_browserstack_video - Failed to download file:', e)


# Description:
#   This method sends a request to browser stack API.
#
# Returns:
#    response (object with data). 
def send_browserstack_request(endpoint: str, user_name: str, password: str):
    response = {}
    base_url = "https://" + user_name + ":" + password + "@api.browserstack.com/"    
    try:
        resp = requests.get(base_url + endpoint)
        response = resp.json() 
    except Exception as e:
        print('send_browserstack_request - Failed to obtain request:', e)
    
    return response
