"""

This Program Will split the ECC file that comes from ECC, into 2 different files based on the databases inputted

i.e.
input
    ECC.xml
    Geelong Database.csv
    Ballarat Database.csv
output
    Geelong.xml
    Ballarat.xml

"""

import xml.etree.ElementTree as ElementTree
import csv, os, datetime, sys
from tkinter.filedialog import askopenfilename


# starts the file creation
FileStart = """<?xml version="1.0" encoding="UTF-8"?>
<DeviceDataCodes xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Devices>
"""
# Define the model of machine in new Device 
def DeviceStart(Date, Model, SerialNo):

    return f"""    <Device>
      <ReportedDate>{Date}</ReportedDate>
      <Model>{Model}</Model>
      <SerialNumber>{SerialNo}</SerialNumber>
      <Category05 />
      <Category08>
"""
# Defines a code from the machine 
def Code08(Code, Value, Subcode=None):
    if Subcode == None:
        return f"""        <Code>
          <MainCode>{Code}</MainCode>
          <Value>{Value}</Value>
        </Code>
"""
    else:
        return f"""        <Code>
          <MainCode>{Code}</MainCode>
          <SubCode>{Subcode}</SubCode>
          <Value>{Value}</Value>
        </Code>
"""
# String that is the same from the end of all devices
DeviceEnd = """      </Category08>
      <Category13 />
    </Device>
"""
# String that caps the file
FileEnd = """  </Devices>
</DeviceDataCodes>
"""

class XmlListConfig(list):          # These 2 classes where found on a fourm but i dont know who created it
    def __init__(self, aList):
        for element in aList:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)

class XmlDictConfig(dict):
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                else:
                    aDict = {element[0].tag: XmlListConfig(element)}
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            elif element.items():
                self.update({element.tag: dict(element.items())})
            else:
                self.update({element.tag: element.text})


# Asks for the input XML file
ECC_XML_File = askopenfilename(initialdir= os.getcwd(), title= "Please select the ECC XML file:", filetypes=[("xml files", "*.xml")])
if ECC_XML_File == "":
    sys.exit()
tree = ElementTree.parse(ECC_XML_File) # Converts the file from XML to a python dict
root = tree.getroot()
xmldict = XmlDictConfig(root)

NoLocations = 2 # this can be set to any number and given there are the proper amount of machine serial number files

LocationDevices = {}

for i in range(NoLocations):
    csvFilePath = askopenfilename(initialdir= os.getcwd(), title= "Please select the locations CSV file:", filetypes=[("csv files", "*.csv")])  # asks for data file that contains location spicific serial numbers
    if csvFilePath == "":
        sys.exit()
    TempName = csvFilePath.split("/")[-1].split(" ")[0]     # gets a name for the new file
    LocationDevices[TempName] = []
    with open(csvFilePath, "r") as csvFile:                 # opens the new file and reads the new serial numbers of the location and puts together the data for the new files
        csvFileRead = csv.DictReader(csvFile)
        for row in csvFileRead:
            if row["Serial No"] != "":
                LocationDevices[TempName].append(row["Serial No"])
        csvFile.close()

Devices = xmldict["Devices"]
Devices = Devices["Device"]

NewFileDict = {}
for i in LocationDevices:
    NewFileDict[i] = {"Device":[]}

for i in Devices:
    for j in LocationDevices:
        if i["SerialNumber"] in LocationDevices[j]:
            NewFileDict[j]["Device"].append(i)

FinishedFiles = {}

for p in NewFileDict:
    XMLString = FileStart
    for i in NewFileDict[p]["Device"]:
        XMLString += DeviceStart(i["ReportedDate"], i["Model"], i["SerialNumber"])
        for j in i["Category08"]["Code"]:
            if len(j) == 2:
                XMLString += Code08(j["MainCode"], j["Value"])
            else:
                XMLString += Code08(j["MainCode"], j["Value"], Subcode=j["SubCode"])
        XMLString += DeviceEnd
    XMLString += FileEnd
    FinishedFiles[p] = XMLString

for i in LocationDevices:
    File = open (f"DeviceDataCodes_{i + str(datetime.date.today())}.xml", "w")
    File.write(FinishedFiles[i])
    File.close()