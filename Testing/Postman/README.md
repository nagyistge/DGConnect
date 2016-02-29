##Postman Installation Procedure
To see the step by step instructions with visuals, see the [Postman Lesson](http://gbdxdocs.digitalglobe.com/docs/lesson-postman-api-requests).
###Get the Postman Files
Collections associated with the QGIS Plugin are kept in the Postman Collections directory of the open source project. For the full list of collections, [go here]()<br>

* Download the collections. If solely working with the associated collections, these are packaged with the rest of the project. Otherwise, the collections will be in a stand alone zip file.<br>

* Save the files to your local drive and unzip them.<br>

###Install Postman
Download and install Postman [here](http://getpostman.com).

###Set up the GBDX Environment
* Import the GBDX environment variables file. 

To do this, select the environment pull down menu, and choose "manage environments".

*  From the "manage environments menu, select "import".

* Select "choose files".

* Navigate to the file location where you saved the Postman files and select the file "GBDX.postman_environment" and open it. You'll get an "import successful" message.

* Type in the environment variables. 

To type in the environment variables from here, choose the Back button, then choose "GBDX". To get back to this menu later, choose "manage environments" from the pull down menu again.

* Type in your username, password, and API key. If you need help finding your API key, go to [Lesson: How to Find your API key](http://gbdxdocs.digitalglobe.com/v1/docs/lesson-how-to-find-your-api-key-1).

###Import the Postman Collection
* To import the GBDX Open Source Postman Collection, choose "import" from the top of the screen.

* Select "Choose Files", then navigate to the file location where you saved the GBDX Postman files. Choose the file "App-QGIS.json.postman_collection" and open it. You'll get a notification that says "Collection App-QGIS Imported.

###Get a Token
Before you can start making API requests using Postman, you need to get your Bearer Token (also referred to as an OAuth2 Token). If you've filled in your environment variables, you can use Postman to get your token.

* On the left hand side under Collections, click "GBDX". You'll see a list of files. Under "Auth" select the Post "Get User Token".

Since you've already added your environment variables, you don't need to fill in the values here. Click Send.

####About Your Token
The response body will include the token (access_token). This token is valid for seven days. You can either:

* Go to Manage Environment and add your token to the environment variables, which will automatically apply it to all requests with the associated Header

* Use it individually in each request by adding your token to the Headers section. Remove {{token}}, and replace it with your access_token.