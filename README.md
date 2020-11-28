# Unified social profiles
__Description__

Δηµιουργία εφαρµογής παρουσίασης ενοποιηµένων προφίλ χρηστών από διαφορετικά κοινωνικά δίκτυα (π.χ. Twitter, Facebook, Instagram) και αλληλεπίδραση µε αυτά

## First meeting notes (09/11/2020)

**Goals**
* Choose either Python or Java
* Focus on three platforms (Facebook, Twitter, Instagram)
* A passive user can gathers all information posted on all different platforms from an entity of his interest such as athlete, radio station, news agency, without losing any update.
* All information will be displayed on a "new" profile.

_To be considered also_
* Ability to interact with every platform (retweet, like, ...)
* Post messages to all platforms

**Actions**
1. Collect and store information from own accounts
2. Collect and store information from account not owned

**Key questions for next meeting**
* Which information to keep and which to discard
* How to design the DB (content, tables, relationships)

## Fourth meeting notes (28/11/2020)

**Goals**
* Finalize the database model with correct attributes' types
* Unify the database to include also Facebook structure
* Scrap links of media from Facebook, consider how to assign unique ID at them
* Store domain part of urls too.

**Limitations**
* (facebook_scraper) Cannot access private profiles that require user credentials at Facebook

**Actions**
1. Make response presentable at a table through Jinga render html templates
2. Apply twitter and Facebook crawl at 5 selected users

**Key questions for next meeting**
* Function that apply the domain part transformation in Python
