The GlobalResultsPage and PollOfficeResultsPage share almost the same view. The only
difference is the app bar which contains the Poll Office name in the case of
PollOfficeResultsPage.

Factorize the GlobalResultsPage in a separate widget called ResultsView and then reuse it
in PollOfficeResultsPage and GlobalResultsPage.