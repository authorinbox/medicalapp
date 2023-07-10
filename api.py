# Importing all the necessary modules

# For interacting with API
import requests
# For searching patterns inside responses
import re
# For system functionalities
import os
# For interactions with the XML Tree
import xml.etree.ElementTree as ET

# --------------------------------------------------

# Getting the number of records in a database for a term in a time period

def get_count(database, term, from_date="", to_date=""):

    # Defining payload for the request
    params = {
    "db": database,
    "term": term
    }
    
    if from_date:
        params["mindate"] = from_date
    if to_date:
        params["maxdate"] = to_date

    # Requesting the API for the data
    request = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params=params)
    response_path = os.path.join(os.getcwd(), "response.xml")

    # Writing the response to a temporary file
    with open(response_path, "wb") as response_file:
        response_file.write(request.content)
    
    # Converting the file to an XML tree
    response_tree = ET.parse(response_path)
    response_root = response_tree.getroot()

    # Parsing the count from the response
    for item in response_root.findall("./Count"):
            count = str(ET.tostring(item))
            return count[count.find("<Count>")+7:count.find("</Count>")]

# Getting the list of IDs for a term in a database in a time period

def get_records(database, term, count, start=0, from_date="", to_date=""):

    # Dealing with the edge cases
    if database == "pubmed" and start > 9995:
        start = 0

    # Defining payload for the request
    params = {
    "db": database,
    "term": term,
    "retmax": str(count)
    }
    
    if from_date:
        params["mindate"] = from_date
    if to_date:
        params["maxdate"] = to_date
    if start:
        params["retstart"] = start

    # Requesting the API for the data
    request = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params=params)
    response_path = os.path.join(os.getcwd(), "response.xml")

    # Writing the response to a temporary file
    with open(response_path, "wb") as response_file:
        response_file.write(request.content)
    
    # Converting the file to an XML tree
    response_tree = ET.parse(response_path)
    response_root = response_tree.getroot()
    
    output = []

    for item in response_root.findall("./Count"):
            count = str(ET.tostring(item))
            output.append(count[count.find("<Count>")+7:count.find("</Count>")])

    for item in response_root.findall("./RetMax"):
            max = str(ET.tostring(item))
            output.append(max[max.find("<RetMax>")+8:max.find("</RetMax>")])

    # Parsing the list of IDs from the response
    ids = []
    for item in response_root.findall("./IdList/Id"):
        id = str(ET.tostring(item))
        ids.append(id[id.find("<Id>")+4:id.find("</Id>")])

    return [output, ids]

def get_email(database, id):

    # Defining payload for the request
    params = {
        "db": database,
        "id": str(id)
    }

    # Requesting the API for the data
    request = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params=params)
    response_path = os.path.join(os.getcwd(), "response.xml")

    # Writing the response to a temporary file
    with open(response_path, "wb") as response_file:
        response_file.write(request.content)
    
    # Converting the file to an XML tree
    response_tree = ET.parse(response_path)
    response_root = response_tree.getroot()

    # Defining procedures for PMC
    if database.lower() == "pmc":
        responses = {}
        for contributor in response_root.findall(".//contrib"):
            # Get the full name of each author
            full_name = ""
            email_text = ""
            for author in contributor.findall(".//name"):
                full_name = ""
                names = list(author.iter())[1:]
                full_name = ""
                for name_tag in names:
                    name = str(ET.tostring(name_tag))
                    if name_tag.tag == "surname":
                        full_name = full_name + f' {name[name.find(">")+1:name.find("</")]}'
                    else:
                        full_name = name[name.find(">")+1:name.find("</")] + f' {full_name}'
            for email in contributor.findall(".//email"):
                # If the author has an email, add it to response
                email = str(ET.tostring(email))
                email_text = email[email.find(">")+1:email.find("</")]
                responses[email_text] = full_name
        return responses
            
    # Defining procedures for PubMed
    elif database == "pubmed":
        responses = {}
        for author in response_root.findall(".//Author"):
            # Get the full name of each author
            names = list(author.iter())[1:]
            full_name = ""
            email_text = ""
            for name_tag in names:
                name = str(ET.tostring(name_tag))
                if name_tag.tag == "LastName":
                    full_name = full_name + f' {name[name.find(">")+1:name.find("</")]}'
                elif name_tag.tag == "ForeName":
                    full_name = name[name.find(">")+1:name.find("</")] + f' {full_name}'
            for item in author.findall(".//Affiliation"):
                # If the author has an email, add it to response
                item = str(ET.tostring(item))
                values = item[item.find(">")+1: item.find("</Affiliation>")]
                values = values.split(" ")
                for value in values:
                    if len(re.findall(".+@.+..+", value)) < 0 or "gmail" in value:
                        email_text = value
                        responses[email_text] = full_name
        return responses
        
# General wrapper function for calling the higher functions

def get_lists_of_emails(database, term, count, start=0, from_date="", to_date=""):

    no_of_records = get_count(database, term, from_date=from_date, to_date=to_date)

    if str(count).lower() == "all":
        responses = get_records(database, term, count=int(no_of_records)+10, start=start, from_date=from_date, to_date=to_date)
    else:
        responses = get_records(database, term, count=count, start=start, from_date=from_date, to_date=to_date)
    
    print("Total records found -", responses[0][0])
    print("Fitered records found -", responses[0][1])
    ids = responses[1]
    i = 1
    import time
    start = time.time()
    for record in ids:
        response = get_email(database, record)
        print(response, i)
        if response != {}:
            output = {}
            for key, value in response.items():
                output[key] = " ".join(value.split("  "))
            print(f"{i}.", record, "-", output)
        else:
            print(f"{i}.", record, "-", "No Emails")
        i += 1
    print("Total -", time.time()-start)
    print("Total Per Unit -", (time.time()-start)/i)

def get_lists_of_emails_api(database, term, count, start=0, from_date="", to_date=""):

    no_of_records = get_count(database, term, from_date=from_date, to_date=to_date)

    if str(count).lower() == "all":
        responses = get_records(database, term, count=int(no_of_records)+10, start=start, from_date=from_date, to_date=to_date)
    else:
        responses = get_records(database, term, count=count, start=start, from_date=from_date, to_date=to_date)
    
    print(responses[1], len(responses[1]))

    ids = responses[1]
    output = {}
    i = 0
    for record in ids:
        print(i/len(responses[1])*100, "%")
        response = get_email(database, record)
        if response != {} and response != None:
            for email, name in response.items():
                i += 1
                output[name] = email
    
    return [output, i]

# --------------------------------------------------

# Database - pmc or pubmed (required)
# Term - any keyword title (required)
# Count - no of pubmed/pmc ids or 'all' (no. of results you will get, not last index) (required)
# Start - from where to start from (default = 0)
# From - from what date to start (format - YYYY, YYYY/MM, YYYY/MM/DD)
# To - to what date at end (format - YYYY, YYYY/MM, YYYY/MM/DD)

# 8000 term
# date filter - 2016-2018 - left records are 6000
# 
#

if __name__ == "__main__":
    get_lists_of_emails_api("Pmc", "cancer", count=100, start=1, from_date="2023/01/01", to_date="2023/04/10")
