# UFRECS Reporter Client

An UFRECS reporter client is an application that connects to an UFRECS backend to provide
realtime data (stats and results).

# Structure

The app as the following page

## Authentication page

This page is built with flutter-form-builder package. The page doesn't have an app bar.
The form has 3 fields:

- elector_id: a string, mandatory
- poll_office_id: a string, mandatory, shown as a searchable dropdown field. When there is atleast 3 chars in the textfield
an http request is made to /api/polloffices/?search=[input] to retrieve the options the returned answer is like this

```json
{
  "count": 123,
  "next": "http://api.example.org/accounts/?offset=400&limit=100",
  "previous": "http://api.example.org/accounts/?offset=200&limit=100",
  "results": [
    {
      "id": 0,
      "name": "string",
      "identifier": "string",
      "country": "string",
      "state": "string",
      "region": "string",
      "city": "string",
      "county": "string",
      "district": "string",
      "created_at": "2025-09-29T14:28:54.165Z",
      "voters_count": 2147483647
    }
  ]
}
```

the identifier field is used as the value and the name and the display

- password: a string, optional, with hidden input

The form must be submitted to /api/authenticate/

with these data

```json
{
  "elector_id": "string",
  "password": "string",
  "poll_office_id": "string"
}
```

The answer is like this

```json
{
  "token": "string",
  "poll_office_id": "string",
  "s3": {
	    "base_path": "string",
	    "credentials": {
	        "bucket": "string",
	        "region": "string",
	        "prefix": "string",
	        "accessKeyId": "string",
	        "secretAccessKey": "string",
	        "sessionToken": "string",
	        "expiration": "string"
	    },
	},
}
```

The token field contains a bearer token. The s3 field contains the informations required to upload images to a s3 storage

When we get a valid response (status code == 200) we go to the Home page

## Home Page

The home page shows a cards grid:

- Votes Session: to go to the Votes Session Page
- Results Session: to go to the Results Session Page
- Poll Office List: to go to the Poll Office List page
- Settings: to go the Settings Page

There is a bottom bar with:

- Home Page button
- Votes Session Page button
- Results Session Page button
- Settings Page button

## Poll Office List page

This page show a FormBuilderImagePicker field (from form_builder_image_picker) and
a submit button.

The submit button will send these photos to the s3 storage under the sub-folder (under the s3 prefix) "poll_office_list"

## Votes Session Page

This page lets the user send the informations about each vote during the voting process.

First, a request is made to /api/pollofficestats/poll_office=[poll_office_id]

The response is like this

```json
{
  "totals": {
    "votes": 0,
    "male": 0,
    "female": 0,
    "less_30": 0,
    "less_60": 0,
    "more_60": 0,
    "has_torn": 0
  },
  "last_vote": {
    "index": 0,
    "gender": "string",
    "age": "string",
    "has_torn": 0
  }
}
```

The next_index to be used must be determined based on the last_vote -> index value. if the last_vote is empty the next_index is 1

Then a loop begins, where there is a form, when the form is submitted, the form is cleared and the next_index is changed (increased)

The form have the following fields:

- gender: string, radio input with 2 choices "male" or "female"
- age: string, radio input with the 3 choices "less_30", "less_60", "more_60"
- has_torn: boolean, checkbox default to False

The form must be submitted to /api/vote/ like this

```json
{
  "index": 0,
  "gender": "male",
  "age": "less_30",
  "has_torn": false
}
```

with the response being

```json
{
  "id": 0,
  "index": 0
}
```

If the http request fails the infos must be saved in a database in the table FailedVote with the following columns: index, gender, age, has_torn

There will be a button in the Settings Page to sync these votes with the backend. 

The form is then reset and the next_index is increased to keep the coherence.

## Results Session Page

This page lets the user send the result of each voting paper during the unpacking process.

First, a request is made to /api/pollofficeresults/poll_office=[poll_office_id]

The response is like this

```json
{
  "last_paper": {
    "index": 0,
    "party_id": "string"
  },
  "results": [
    {
      "party_id": "string",
      "ballots": 0,
      "share": 0
    }
  ],
  "total_ballots": 0
}
```

The next_index to be used must be determined based on the last_paper -> index value. if the last_vote is empty the next_index is 1

The list of candidates must be fetched via /api/candidateparties/ with a response being like this

```json
{
  "count": 123,
  "next": "http://api.example.org/accounts/?offset=400&limit=100",
  "previous": "http://api.example.org/accounts/?offset=200&limit=100",
  "results": [
    {
      "id": 0,
      "party_name": "string",
      "candidate_name": "string",
      "identifier": "string",
      "created_at": "2025-09-29T16:36:11.494Z"
    }
  ]
}
```

The list is shown as a grid with 2 columns. The card of the grid must be show the candidate and party names.

When the user select a card/candidate then a popup is displayed for him to confirm his choice.
If he doesn't confirm the popup is simply closed.
If he confirm an http request is made to /api/votingpaperresult/ with

```json
{
  "index": 0,
  "party_id": "string"
}
```

and a response like this 

```json
{
  "status": "ok"
}
```

If the request fails put the infos in a database where the table is FailedVotingPaperResult with 2 columns index and party_id.

The next_index is then increased to keep consistency.

The grid is re-organized to put the card/candidate at the beginning of the grid.

## Settings Page

 The settings page will:

 - show the elector_id
 - show how many failed votes there is in the database from the FailedVote table
 - show a button to re-send the failed votes if they are more than 0
 - show how many failed voting paper results there is in the database from the VotingPaperResult table
 - show a button to re-send the failed voting paper results if they are more than 0
 - show a contact email
 - show some phone numbers to contact
 - show the name of the developer team

 # Stack

 - flutter
 - dio: to make http requests
 - dio_smart_retry: to auto handle retries, https://pub.dev/packages/dio_smart_retry
 - flutter-form-builder: for forms
 - form_builder_image_picker: for image picking
 - sembast: for database, doc here https://pub.dev/packages/sembast

 # Visual

 Colors: primary = green; secondary = red; tertiary = yellow

 Style: Material

 Pixel perfect

 Very beautiful

 I18n ready

 Responsive

 # Guidelines

 Documentation for all classes and functions

 Comments everywhere

 Compact code

 Simple code

 Maximum usage of configuration classes to allow rapid editing
