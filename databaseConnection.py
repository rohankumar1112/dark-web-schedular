import pymongo
from flag import sendData,sendLog
# MongoDb Connection...
client =pymongo.MongoClient("mongodb+srv://emseccomandcenter:TUXnEN09VNM1drh3@cluster0.psiqanw.mongodb.net/?retryWrites=true&w=majority")

#XPATH fetch collection
db =client['darkWebAutomation']
collection =db['websiteXPATH']
print ("Total websites we have:", collection.count_documents( {} ))
sendLog (f"Total websites we have: {collection.count_documents( {} )}")

#Data sump collection
collection2 =db['dataDumpCheck']


