import http.client
dirPath = dirPath = '/Users/albertocottica/Documents/Edgeryders the company/SSNA_data_export/poprebel test folder/'
conn = http.client.HTTPSConnection("api.data.world")
headers = { 'authorization': "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJwcm9kLXVzZXItY2xpZW50OmhhaWt1NjYiLCJpc3MiOiJhZ2VudDpoYWlrdTY2Ojo4YmUxMzQ2OS1jMmFhLTRmODctOTYzMi02NDRmZDg5ZTY3OTIiLCJpYXQiOjE1ODI3MjM1MzEsInJvbGUiOlsidXNlcl9hcGlfcmVhZCIsInVzZXJfYXBpX3dyaXRlIl0sImdlbmVyYWwtcHVycG9zZSI6dHJ1ZSwic2FtbCI6e319.spyFA9YazqhCIGAA6EjhDXjm4sBvhwinmfx4XwnQlRJs3s-DpQbQKHojjPA49OSiB0q0NLuI4U_scmHCVbtGUA" }
conn.request("GET", "/v0/user/datasets/own", headers=headers)
response = conn.getresponse()
data = response.read()
print(data.decode("utf-8"))

import requests
call = 'https://api.data.world/v0/download/haiku66/poprebel-ssn-data'
response = requests.get(call, headers = headers)
open(dirPath + 'dataworldDownload.zip', 'wb').write(response.content)

##with open (dirPath + 'dataworldDownload.csv', 'w', encoding = 'utf-8') as dwfile:
    
    
