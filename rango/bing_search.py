import json
import urllib, urllib2

def run_query(search_terms):
    root_url = "https://api.datamarket.azure.com/Bing/Search/v1/"
    source = 'Web'

    # offset means where from the result list to start, if results_
    # per_page = 10, offset = 11, it will start from page 2
    results_per_page = 10
    offset = 0

    # As per Bing's requirement, the query must be wrapped in quotes,
    # We then store the variable into query for later usage
    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)

    # Construct the latter part of the serach request URL
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
            root_url,
            source,
            results_per_page,
            offset,
            query)

    # The username must be blank!
    username = ''
    bing_api_key = '59wVOA4POjABZM1vJ2jWiuRr0sDTYpwEZziqO1Qjklg'

    # Create a password manage which handles authentication for us
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, bing_api_key)

    # Create our results list which we will populate
    results = []

    try:
        # Prepare for connection to Bing's server
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        # Connect to the server and read the response
        response = urllib2.urlopen(search_url).read()

        # Convert the response to Python dict type
        json_response = json.loads(response)

        # Loop through each page returned, append to our results list
        for result in json_response['d']['results']:
            results.append({
                'title': result['Title'],
                'link': result['Url'],
                'summary': result['Description']})
    except urllib2.URLError, e:
        print "Error while querying the Bing API: ", e

    return results





