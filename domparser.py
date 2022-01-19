
import os
import json
import pprint
from bs4 import BeautifulSoup
import traceback

UNKNOWN_ERROR = 1 
NO_TAG_PROVIDED_BY_BE = 2
NO_VALUE_PROVIDED_BY_BE = 3
NO_SEARCH_TYPE_PROVIDED_BY_BE = 4
ACTION_NOT_VALID_FOR_ANALYSIS = 5
STEP_INDEX_GREATER_THAN_NUMBER_OF_SELECTORS_FOUND = 6
ONE_SELECTOR_FOUND_FOR_NTAGSELECTOR = 7
NO_SELECTOR_FOUND_WITH_SPECIFIC_VALUE = 8  
SELECTOR_FOUND_WITH_CORRECT_INDEX = 9
SELECTOR_FOUND_WITH_INCORRECT_INDEX = 10  
MULTIPLE_SELECTORS_FOUND_WITH_EXPECTED_VALUE_CORRECT_INDEX = 11 
MULTIPLE_SELECTORS_FOUND_WITH_EXPECTED_VALUE_INCORRECT_INDEX = 12
NO_SELECTOR_FOUND_WITH_NTAGSELECTOR = 13
SELECT_ELEMENT_INCORRECT_VALUE = 14

# Description:
#   This method will be called to handle the result of filter operation done  
#   on the selectors found.
#   
#   There are 3 options for the result:
#    1) No selectors were found having the value we are expecting. On this case,
#       information returned will be the element with the index that was expected.
#
#    2) We found only one selector, we have two options here:
#       a) Found the correct selector: Return the original element.
#       b) Found the incorrect selector. Return two elements, one with the original index and other with the found index.
# 
#    3) We found two or more selectors with the same src. We have two options here:
#       a) The correct selector was found. Return the original element. 
#       b) The correct selector was not found. Return two elements, one with the original index and other with all the indexes found.
#   
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
#
def processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, attribute):
   jsonObject = {}
   elements = []

   if(selectorsFound == 0):
      # No selectors were found with the expected value
      if(expectedIndex <= len(selectors)):
         element = {}
         element["index"] = expectedIndex
         if(attribute == "text"):
            element["value"] = selectors[expectedIndex].text if (selectors[expectedIndex].text != "") else "" 
         else:   
            element["value"] = selectors[expectedIndex][attribute] if (attribute in selectors[expectedIndex]) else ""
         element["selector"] = "found"
         elements.append(element) 
         returnCode = NO_SELECTOR_FOUND_WITH_SPECIFIC_VALUE
      else:
         returnCode = STEP_INDEX_GREATER_THAN_NUMBER_OF_SELECTORS_FOUND   
   elif(selectorsFound == 1):
      if(expectedIndex in selectorIndexes):
        # The expected selector was found and it is the only selector.
         element = {}
         element["index"] = expectedIndex
         if(attribute == "text"):
            element["value"] = selectors[expectedIndex].text
         else:   
            element["value"] = selectors[expectedIndex][attribute]
         element["selector"] = "original"
         elements.append(element) 
         returnCode = SELECTOR_FOUND_WITH_CORRECT_INDEX
      else:
         # The incorrect selector was found and this is the only selector with the expected value
         element = {}
         element["index"] = expectedIndex
         element["selector"] = "original"
         if(expectedIndex <= len(selectors)):
            if(attribute == "text"):
               element["value"] = selectors[expectedIndex].text
            else:   
               element["value"] = selectors[expectedIndex][attribute]
         else:
            element["value"] = expectedValue
         elements.append(element) 

         element = {}
         element["index"] = selectorIndexes[selectorsFound -1]
         if(attribute == "text"):
            element["value"] = selectors[selectorIndexes[selectorsFound -1]].text
         else:   
            element["value"] = selectors[selectorIndexes[selectorsFound -1]][attribute]
         element["selector"] = "found"
         elements.append(element) 
         returnCode = SELECTOR_FOUND_WITH_INCORRECT_INDEX
   elif(selectorsFound > 1):
      # Several selectors were found with same value
      if(expectedIndex in selectorIndexes):
         # The expected element was found on the selectors
         element = {}
         element["index"] = expectedIndex
         if(attribute == "text"):
            element["value"] = selectors[expectedIndex].text
         else:   
            element["value"] = selectors[expectedIndex][attribute]
         element["selector"] = "original"
         elements.append(element) 
         returnCode = MULTIPLE_SELECTORS_FOUND_WITH_EXPECTED_VALUE_CORRECT_INDEX
      else:
         # The expected element was NOT found on the selectors
         element = {}
         element["index"] = expectedIndex
         element["selector"] = "original"
         if(expectedIndex <= len(selectors)):
            if(attribute == "text"):
               element["value"] = selectors[expectedIndex].text
            else:   
               element["value"] = selectors[expectedIndex][attribute]
         else: 
            element["value"] = expectedValue
         elements.append(element) 
   
         element = {}
         if(attribute == "text"):
            element["value"] = expectedValue
         else:   
            element["value"] = expectedValue
         element["index"] = str(selectorIndexes)   
         element["selector"] = "found"
         elements.append(element) 
         returnCode = MULTIPLE_SELECTORS_FOUND_WITH_EXPECTED_VALUE_INCORRECT_INDEX

   jsonObject["numberOfElementsWithSameSelectorAndValue"] = selectorsFound   
   jsonObject["selectors"] = elements
   jsonObject["rc"] = returnCode

   return jsonObject

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the text value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters: 
#    selectors: Array of selectors found with the same ntagselector.
#    searchInfo: Object containing infromation related to the DOM analysis (value to find, element type, etc.).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseTextSelector(selectors, searchInfo, expectedIndex, tag):
   jsonObject = {}
   selectorIndexes = []
   selectorIndex = 0
   selectorsFound = 0
   expectedValue = searchInfo["value"]

   if(expectedValue == ""):
     jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0   
     jsonObject["selectors"] = []
     jsonObject["rc"] = NO_VALUE_PROVIDED_BY_BE
     return jsonObject

   for selector in selectors:
      selectorText = selector.text.replace("'", "")
      if(selectorText.strip() == expectedValue.strip()):
         selectorsFound += 1
         selectorIndexes.append(selectorIndex)
      selectorIndex+=1   
   
   return processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "text")

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the src value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters: 
#    selectors: Array of selectors found with the same ntagselector.
#    searchInfo: Object containing infromation related to the DOM analysis (value to find, element type, etc.).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseImageSelector(selectors, searchInfo, expectedIndex, tag):
   selectorIndexes = []
   selectorIndex = 0
   selectorsFound = 0
   expectedValue = searchInfo["value"]

   for selector in selectors:
      if(selector['src'] == expectedValue ):
         selectorsFound += 1
         selectorIndexes.append(selectorIndex)
      selectorIndex+=1   

   return processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "src")

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the href value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters: 
#    selectors: Array of selectors found with the same ntagselector.
#    searchInfo: Object containing infromation related to the DOM analysis (value to find, element type, etc.).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseHypertextSelector(selectors, searchInfo, expectedIndex, tag):
   jsonObject = {}
   selectorIndexes = []
   filteredIndexes = []
   selectorIndex = 0
   selectorsFound = 0
   expectedValue = searchInfo["value"]
   if hasattr(searchInfo, 'text'):   
      expectedText = searchInfo["text"]
   else:
      expectedText = "" 

   if(expectedValue == ""):
     jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0   
     jsonObject["selectors"] = []
     jsonObject["rc"] = NO_VALUE_PROVIDED_BY_BE
     return jsonObject

   for selector in selectors:
      if(selector and selector.has_attr('href')):
         if(selector['href'] == expectedValue):
            selectorsFound += 1
            selectorIndexes.append(selectorIndex)
      selectorIndex+=1   
   
   # If more than 1 selector was found using the same value, lest's filter now by text and update
   # the selectorIndexes with the new indexes (hopefully only one!).
   if(selectorsFound > 1 and expectedText != ""):
     for i in selectorIndexes:
        if(str(selectors[i].string) == expectedText):
           filteredIndexes.append(i)
     if(len(filteredIndexes) > 0 ):
      selectorIndexes = []
      selectorsFound = len(filteredIndexes)
      for index in filteredIndexes:
         selectorIndexes.append(index)

   return processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "href")

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters: 
#    selectors: Array of selectors found with the same ntagselector.
#    searchInfo: Object containing infromation related to the DOM analysis (value to find, element type, etc.).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseValueSelector(selectors, searchInfo, expectedIndex, type, tag):
   selectorIndexes = []
   selectorIndex = 0
   selectorsFound = 0
   expectedValue = searchInfo["value"] if ('value' in searchInfo) else ""
   expectedText = searchInfo["text"] if ('text' in searchInfo) else ""

   for selector in selectors:
      if(('value' in selector) and selector['value'] == expectedValue ):
         selectorsFound += 1
         selectorIndexes.append(selectorIndex)
      selectorIndex+=1   

   # If we have text information available and this is a select element, let's try to
   # find the correct value using the text
   if(selectorsFound == 0 and expectedText != "" and tag == "select"):
      return handleSelectElement(selectors, expectedText, expectedIndex, selectorIndexes, tag)
   
   return processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "value")

def handleSelectElement(selectors, expectedText, expectedIndex, selectorIndexes, tag):
   jsonObject = {}
   elements = []
   value = ""
   # Let's first verify the selector with the expected index
   selectElement = selectors[expectedIndex]
   options = selectElement.find_all("option")
   for option in options:
      if(option.text.strip() == expectedText.strip()):
         value = option.get("value")
         break
   
   element = {}
   element["index"] = expectedIndex
   element["value"] = value
   element["selector"] = "found"
   elements.append(element) 

   jsonObject["numberOfElementsWithSameSelectorAndValue"] = 1   
   jsonObject["selectors"] = elements
   jsonObject["rc"] = SELECT_ELEMENT_INCORRECT_VALUE

   return jsonObject

# Description:
#   This method will . 
#
# Returns:
#    . 
def verifyAttributesOnElements(selectors, attributes):
    selectorsFound = []   
    selectorIndexes = []   
    index = 0

    # First let's try to find any selector on the list with the ID frm the element attributes 
    index = 0
    for selector in selectors:
        if(selector.has_attr('id')):
            if(selector['id'] == attributes['id']):
                selectorsFound.append(selector)
                selectorIndexes.append(index) 
                return [selectorsFound, selectorIndexes]
            index+=1        

    # If we get here it means no selector with ID was found, let's check with name
    if(len(selectorsFound) == 0):
     index = 0
     for selector in selectors:
        if(selector.has_attr('name')):
            if(selector['name'] == attributes['name']):
                selectorsFound.append(selector)
                selectorIndexes.append(index) 
                return [selectorsFound, selectorIndexes]
            index+=1     

    # If we get here it means no ID and NAME were found, let's check with text
    if(len(selectorsFound) == 0):
     index = 0
     for selector in selectors:
        if(selector.has_attr('text')):
            if(selector['text'] == attributes['text']):
                selectorsFound.append(selector)
                selectorIndexes.append(index) 
            index+=1     

    # If we get here it means no ID and NAME were found, let's check with text
    index = 0
    for selector in selectors:
        if(selector.has_attr('type')):
            if(selector['type'] == attributes['type']):
                selectorsFound.append(selector)
                selectorIndexes.append(index) 
            index+=1    

    return [selectorsFound, selectorIndexes]


# Description:
#   This method will . 
#
# Returns:
#    . 
def filterSelectorsByAttributes(selectors, attributes, searchInfo, stepId,index):
   
   print("Start analysis for step, "  + str(stepId) + " for " + str(len(selectors)) + " Selectors")
   print("Attributes, "  + str(attributes))
   #print("Selectors:, "  + str(selectors))
   selectorsFound = []   
   selectorIndexes = []   
   elements = []
   jsonObject = {}
   expectedValue = searchInfo["value"] if ('value' in searchInfo) else ""
   searchType = searchInfo["searchType"]

   [selectorsFound,selectorIndexes] = verifyAttributesOnElements(selectors, attributes); 
   print("Returned from verifyAttributesOnElements")
   print(selectorsFound)

   if(len(selectorsFound) == 1):
      element = {}
      element["index"] = index
      element["selector"] = "original"
      element["value"] = expectedValue
      elements.append(element) 
      if(index != selectorIndexes[0]):   
         element = {}
         element["index"] = selectorIndexes[0]
         element["selector"] = "found"
         if (selectorsFound[0].has_attr('value') and selectorsFound[0]['value'] != ""):
            print("Value in selector")
            element["value"] = selectorsFound[0]['value'] 
            jsonObject["numberOfElementsWithSameSelectorAndValue"] = 1
         else: 
            print("Value NOT in selector")
            element["value"] = "undef"
            jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0
         elements.append(element) 
      else:
         element = {}
         element["index"] = index
         element["selector"] = "found"
         if (selectorsFound[0].has_attr('value') and selectorsFound[0]['value'] != ""):
            print("Value in selector")
            element["value"] = selectorsFound[0]['value'] 
            jsonObject["numberOfElementsWithSameSelectorAndValue"] = 1
         else: 
            print("Value NOT in selector")
            element["value"] = "undef"
            jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0
         elements.append(element) 

      jsonObject["selectors"] = elements
      jsonObject["rc"] = SELECT_ELEMENT_INCORRECT_VALUE
   else:
      jsonObject["selectors"] = selectors
      jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0
      jsonObject["rc"] = NO_SELECTOR_FOUND_WITH_NTAGSELECTOR

   return jsonObject  

# Description:
#   This method will be call for each step and will parse the DOM files generated  
#   for the test to find the selectors for this step. If more than one selector is found,  
#   this method makes another search on the DOM using the value to filter the 
#   selectors found. 
#
# Returns:
#    jsonObject with the number of selector information. 
def obtainFeedbackFromDOM(classname, stepId, ntagselector, index, tag, type, action, searchInfo, browserName, attributes):
   #os.chdir("/home/serrano/Development/executor/local/executor")
   jsonObject = {}
   elements = []    
   path = 'build/reports/geb/' + browserName + '/'
   filename = path + classname + "_" + str(stepId) + ".html"

   if os.path.exists(filename):
      try:
         searchType = searchInfo["searchType"]
         text = open(filename, 'r').read()
         soup = BeautifulSoup(text, 'html.parser')
         selectorsFound = soup.select(ntagselector)
         numberSelectorsFound = len(selectorsFound)
         print(numberSelectorsFound)

         if(action == "mouseover"):
            jsonObject["selectors"] = []
            jsonObject["rc"] = ACTION_NOT_VALID_FOR_ANALYSIS
            jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0
         else:  
            if(numberSelectorsFound == 0 ):
               jsonObject["selectors"] = []
               jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0
               jsonObject["rc"] = NO_SELECTOR_FOUND_WITH_NTAGSELECTOR

            elif(numberSelectorsFound == 1 ):
               element = {}
               element["index"] = index
               element["value"] = searchInfo["value"]
               element["selector"] = "original"
               if(searchType == "value" and selectorsFound[0].has_attr('value')):
                  element["value"] = selectorsFound[0]["value"]
               elif(searchType == "href" and selectorsFound[0].has_attr('href')): 
                  element["value"] = selectorsFound[0]["href"]
               elif(searchType == "text" and selectorsFound[0].has_attr('text')):
                  element["value"] = selectorsFound[0].text
               elif(searchType == "imgsrc" and selectorsFound[0].has_attr('src')):
                  element["value"] = selectorsFound[0]["src"]
               else:
                  element["value"] = searchInfo["value"]
               elements.append(element)
               returnCode = ONE_SELECTOR_FOUND_FOR_NTAGSELECTOR

               if(index > 0):
                  element = {}
                  element["index"] = 0
                  element["selector"] = "found"
                  if(searchType == "value" and selectorsFound[0].has_attr('value')):
                     element["value"] = selectorsFound[0]["value"]
                  elif(searchType == "href" and selectorsFound[0].has_attr('href')):   
                     element["value"] = selectorsFound[0]["href"]
                  elif(searchType == "text" and selectorsFound[0].has_attr('text')):
                     element["value"] = selectorsFound[0].text
                  elif(searchType == "imgsrc" and selectorsFound[0].has_attr('src')):
                     element["value"] = selectorsFound[0]["src"]
                  else:
                     element["value"] = searchInfo["value"]   
                  elements.append(element)
                  returnCode = SELECTOR_FOUND_WITH_INCORRECT_INDEX

               jsonObject["selectors"] = elements
               jsonObject["numberOfElementsWithSameSelectorAndValue"] = numberSelectorsFound
               jsonObject["rc"] = returnCode

            elif(numberSelectorsFound > 1 ):
               if(searchType == "value"):
                  jsonObject = parseValueSelector(selectorsFound, searchInfo, index, type, tag)
               elif(searchType == "href"):
                  jsonObject = parseHypertextSelector(selectorsFound, searchInfo, index, tag)
               elif(searchType == "text"):
                  jsonObject = parseTextSelector(selectorsFound, searchInfo, index, tag)
               elif(searchType == "imgsrc"):
                  jsonObject = parseImageSelector(selectorsFound, searchInfo, index, tag)
               else:
                  # Backend sent an undef searchType, we will return no info
                  jsonObject["selectors"] = []
                  jsonObject["rc"] = NO_SEARCH_TYPE_PROVIDED_BY_BE
                  jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0
               
               # If we are done with the search and we were not ablt to find a selector. Let's try to use the attributes to find the element.
               if(jsonObject["rc"] == NO_SELECTOR_FOUND_WITH_SPECIFIC_VALUE or 
                  jsonObject["rc"] == NO_SEARCH_TYPE_PROVIDED_BY_BE):
                  print("Need to search using attributes now for step " + str(stepId))
                  # This code is to do analysis on the element's attributes. This will be enable on a future sprint
                  #jsonObject = filterSelectorsByAttributes(selectorsFound, attributes, searchInfo, stepId, index)
                  #newNumberSelectorsFound = len(newSelectorsFound)

         jsonObject["numberOfElementsWithSameSelector"] = numberSelectorsFound

      except Exception as ex:
         print("Failed to open file " + str(filename) + ex)
         print (ex)

   # Let's validate the data we generated is a valid json for this step
   try:
     json.loads(json.dumps(jsonObject)) 
   except Exception as ex: 
     pprint.pprint("Invalid JSON format for step " + str(stepId) +"  found, will not send feedback to BE")
     print(ex) 
     print(traceback.format_exc())    
     jsonObject = {}

   return jsonObject


# Description:
#   This method will be call to execuete the Muuk Report analysis.  
#   for the test to find the selectors for this step. If more than one selector is found,  
#   this method makes another search on the DOM using the value to filter the 
#   selectors found. 
#
# Returns:
#    jsonObject with the number of selector information. 
def createMuukReport(classname, browserName):
   #os.chdir("/home/serrano/Development/executor/local/executor")
   print(os.getcwd())
   path = 'build/reports/'
   filename = path + classname + ".json"
   muukReport = {}
   steps = []
   if(os.path.exists(filename)):
      try:
        jsonFile = open(filename, 'r')
        elements = json.load(jsonFile)
        for element in elements['stepsFeedback']:
          type = element.get("type")
          if(type == "step"):
            valueInfo = json.loads(element.get("value"))
            attributes = json.loads(element.get("attributes"))
            attributes['value'] = valueInfo['value']
            domInfo = obtainFeedbackFromDOM(classname, element.get("id"), 
                                             element.get("selector"), 
                                             element.get("index"), element.get("tag"),
                                             element.get("objectType"), element.get("action"), 
                                             valueInfo,
                                             browserName,
                                             attributes)
            if(domInfo):                                
               element["numberOfElementsWithSameSelector"] = domInfo["numberOfElementsWithSameSelector"]
               element["numberOfElementsWithSameSelectorAndValue"] = domInfo["numberOfElementsWithSameSelectorAndValue"]
               element["rc"] = domInfo["rc"]
               element["selectors"] = domInfo["selectors"]
               steps.append(element)
          else:
            steps.append(element)     

      except Exception as ex:
          print("Exception found during DOM parsing. Exception = ")
          print(ex) 
          print(traceback.format_exc())    
      
      # Closing file
      jsonFile.close()
   else:
      print("Muuk Report was not found!")   
   
   # Let's validate the data we generated is a valid json
   try:
     json.loads(json.dumps(steps)) 
     muukReport["steps"] = steps
   except Exception as ex: 
     pprint.pprint("Invalid JSON format was found, will not send feedback to BE")
     print(ex) 
     print(traceback.format_exc())    
     muukReport["steps"] = {}

   # Print report if touch file exists 
   if(os.path.exists("TOUCH_TRACE_REPORT")):
     pprint.pprint(muukReport["steps"])

   return muukReport