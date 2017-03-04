# gotit-readinglist-api
A Reading List RESTful API, with Token Authenication

To run the app in Debug mode:  
1. Set up the database using the db.sql for now (db migration is not ready).  
2. Use config.py to configure settings if necessary (e.g., default database account is build:build).  
3. Run the following:  
```bash
pip install -r requirements.txt
source env/bin/activate
python app.py
```

# To-do List
- More error catching
- Rate limit using Redis
- Database migration automation
- Relationships table foreign key relationship
- Input validation check (ISBN, Email address, etc.)
- Flask-Blueprint for API version management

# Reading List REST API Documentation

The reading list API allows users to manage their private and public reading lists, and to share and explore them.

## Base URL

All URLs referenced in the documentation have the following base:

```
http://127.0.0.1:5000/
```

To ensure data privacy, the API is also served over HTTPS.


## Errors

You will see a HTML 4XX status code and an error message if an exception happens.

```json
403 Forbidden
{
  "error": "Wrong user, permission denied."
}
```


## User Authenication

### Create User

Make a HTTP POST to:

```
/register
```

with the following parameters (in JSON):

```json
{
  "email": "ok@ok.com",
  "password": "python"
}
```

API would respond:

```json
{
  "user_id": 10
}
```

indicating that a registration is successful, and a user_id is created.

### Login and Get a Token

Make a HTTP request to:

```
/user
```

with your login credentials, API would respond with your home address and a token:

```json
200 OK
{
  "home": "/user/6",
  "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ4ODM1MjkzNCwiaWF0IjoxNDg4MzUyMzM0fQ.eyJpZCI6Nn0.pBES4gYM3xCytdq4sEjYkAbomReiIX1HXbP49Y0kxGc"
}
```

Note that by default all functions does not accept credentials but a token, and a token is valid within 10 minutes. Make another request once a token is expired.


## List Management (Token Needed)

### Read All Lists (User Home)

Make a HTTP GET to:

```
/user/<user_id>
```

with your token, and get all lists infomation:

```json
200 OK
{
  "lists": [
    {
      "address": "/list/1", 
      "isprivate": true, 
      "list_id": 1
    }, 
    {
      "address": "/list/2", 
      "isprivate": false, 
      "list_id": 2
    }
  ], 
  "owner": {
    "user_id": 6
  }
}
```

### Create a New List

Make a HTTP POST to:

```
/user/<user_id>
```

with your token and properties of the new list:

```json
{
  "isprivate": true
}
```

API will return the following message if succeeded.

```json
201 CREATED
{
  "address": "/list/3",
  "isprivate": true,
  "list_id": 3
}
```

### Delete a List and All of its Contents

Make a HTTP DELETE to:

```
/user/<user_id>
```

with your token and properties of the list to be deleted:

```json
{
  "list_id": 2
}
```

API will return the following message if succeeded.

```json
201 CREATED
{
  "status": "List successfully deleted."
}
```

### Show All Books in a List

Make a HTTP GET to:

```
/list/<list_id>
```

with your token, and get all books in a list with brief information.

```json
200 OK
{
  "books": [
    {
      "author": "sample_author_1",
      "book_id": 1,
      "title": "sample_title_1"
    },
    {
      "author": "sample_author_2",
      "book_id": 3,
      "title": "sample_title_2"
    }
  ],
  "list_info": {
    "isprivate": false,
    "list_id": 2,
    "user_id": 6
  }
}
```

### Add a Book to the List

Make a HTTP POST to:

```
/list/<list_id>
```

with your token and properties of the new book:

```json
{
	"isbn": "0000000000000",
	"title": "sample_title_1",
	"author": "sample_author_1",
	"category": "sample_category_1",
	"coverurl": "sample_url_1",
	"summary": "sample_summary_1"
}
```

API will return the following message if succeeded.

```json
201 CREATED
{
  "book_id": 1
}
```

Note: If you add a book with the same ISBN with an existing book, a new book will not be created and the existing one will be linked to the reading list.

### Delete a Book in the List

Make a HTTP DELETE to:

```
/list/<list_id>
```

with your token and properties of the book to be deleted:

```json
{
  "book_id": 2
}
```

API will return the following message if succeeded.

```json
201 CREATED
{
  "status": "Book successfully deleted."
}
```

Note that if a book is shared within multiple lists, only the relationship will be deleted.

### Return Details of a Book

Make a HTTP GET to:

```
/book/<book_id>
```

and get back the details:

```json
200 OK
{
  "author": "sample_author_2",
  "book_id": 3,
  "category": "sample_category_2",
  "coverurl": "sample_url_2",
  "isbn": "0000000000001",
  "summary": "sample_summary_2",
  "title": "sample_title_2"
}
```

## Discovery for Anonymus Users

### See Public Reading Lists

Make a HTTP GET to:

```
/discovery
```

and get back the public reading lists:

```json
200 OK
{
  "books": [
    {
      "author": "sample_author_1",
      "book_id": 1,
      "title": "sample_title_1"
    },
    {
      "author": "sample_author_2",
      "book_id": 3,
      "title": "sample_title_2"
    }
  ],
}
```

### See Details of a Public Reading List

Make a HTTP GET to:

```
/discovery/<list_id>
```

and get back the details of a public reading list:

```json
200 OK
{
  "books": [
    {
      "author": "sample_author_1",
      "book_id": 1,
      "title": "sample_title_1"
    }
  ],
  "list_info": {
    "list_id": "2"
  }
}
```

### See Book Details

The behavior is similar to registered users.
