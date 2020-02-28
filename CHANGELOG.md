Changelog
=========

* In case of major changes, an email should be sent to all users with the modifications.

2.2.1 (2020-02-28)
------------------
* Remove None values from Reports
* Change Report 8 name to "Products - Requirements - Dataset - Data Providers link"
* Added Data Area to report "Requirement Areas"
* Removed table barcharts from pivot reports
* Removed country from pivot reports
* Fix product count for Report Entrusted Entity component statistics
* Add links directing to help page on detail's pages for picklist values
* Add optional status field for Data, with same values as product
* Add owner field to requirement (used for the entity that created the requirement)/Change all references to the user who created the object to "author"
* Add PicklistEditor user role (the user who has this role can access a filtered version of the administration panel for adding/editing the picklists)
  [dianaboiangiu]

2.2.0 (2020-02-24)
-----------------
* Add Filtering based on Products for Requirement's list
* Add Filtering based on Requirements for Data's list
* Add user role "ProductEditor" for adding/editing products
  [dianaboiangiu]

2.1.7 (2019-11-25)
-----------------
* Add PDF download for Online Help section
  [dianaboiangiu]

2.1.6 (2019-11-01)
-----------------
* Add PDF Download for User Manual
* Fix borders in PDF Reports
* Fix Special reports download
  [dianaboiangiu]

2.1.5 (2019-10-25)
-----------------
* Finalize setup for EEA Sentry
  [dianaboiangiu]

2.1.4 (2019-10-24)
-----------------
* Upgrade raven package for Sentry support
  [dianaboiangiu]

2.1.3 (2019-10-24)
-----------------
* Move CIS2 to new Sentry
  [dianaboiangiu]

2.1.2 (2019-09-26)
-----------------
* Fix product description display
  [dianaboiangiu]

2.1.1 (2019-09-17)
------------------
* Show Records added by user on User page (click "Hello user")
* Show logging details in Homepage
* Show application statistics on About page
* Show recent incidents in About page
* Bug fix
  [dianaboiangiu]

2.1.0 (2019-09-17)
------------------
* Show Records added by user on User page (click "Hello user")
* Show logging details in Homepage
* Show application statistics on About page
* Show recent incidents in About page
  [dianaboiangiu]

2.0.1 (2019-07-05)
-----------------
* Use official name in User Manual
  [catalinjitea]

2.0.0 (2019-06-27)
------------------
* Migrate to version 2.0.0
* Update User Manual
  [dianaboiangiu]

1.5.22 (2019-05-29)
------------------
* Fix dataprovider issue on Report 8
  [dianaboiangiu]

1.5.21 (2019-05-27)
------------------
* Add 2 special reports
  [dianaboiangiu]

1.5.20 (2019-05-09)
------------------
* Fix excel download error
  [dianaboiangiu]

1.5.19 (2019-05-07)
------------------
* Set case insensitive ordering in reports
* Add count of products on Report 4
* Add notes for product and requirement on Report 1
* Remove the unusefull aggregator functions from the pivot
* Separate threshold, breakthrough and goal in reports
* Style column names in browser
* Limit the drag and drop pivot function to only the area near the field list
* Add missing attributes to reports: requirement note(report1, report 8), service and components (report 3), data name (report 7)
  [dianaboiangiu]

1.5.18 (2019-04-02)
------------------
* Fix links between data in reports
  [dianaboiangiu]

1.5.17 (2019-03-19)
------------------
* Change data note to data note link on Report 8
* Report 8 - bring all objects
  [dianaboiangiu]

1.5.16 (2019-03-14)
------------------
* Add data note to Report 8
* Add loading animation while pivot loads
* Upgrade Elasticsearch to 6.6.1
  [dianaboiangiu]

1.5.15 (2019-02-15)
-------------------
* Remove preview from reports detail page
* Modify report 8 to add all fields for requirement and data
  [dianaboiangiu]

1.5.14 (2019-01-21)
------------------
* Add read-only user account type
* Remove logging for get actions
* On changes requested status e-mail is sent to object owner.
  [dianaboiangiu]

1.5.13 (2018-12-07)
------------------
* Use different function for Internet Explorer reports export
  [dianaboiangiu]

1.5.12 (2018-12-06)
------------------
* Make logging persistent
* Hide valid button for teammates
* Fix report export for Firefox, Edge and Internet Explorer
  [dianaboiangiu]

1.5.11 (2018-11-21)
------------------
* Fix links between products and requirements
  [dianaboiangiu]

1.5.10 (2018-11-09)
------------------
* Extend acronym length on products
  [dianaboiangiu]

1.5.9 (2018-11-02)
------------------
* Add new reports
* Fix pivot excel download issue
* Fix Data in ready Data provider link (Data provider should be linked to Data only when Data is in draft status)
* Resolve ready to valid issue
  [dianaboiangiu]

1.5.8 (2018-10-08)
------------------
  * Fix style on about page
  [dianaboiangiu]

1.5.7 (2018-10-08)
------------------
  * Add debug toolbar option for staging
  [dianaboiangiu]

1.5.6 (2018-10-05)
------------------
  * Fix homepage latest changes text
  [dianaboiangiu]

1.5.5 (2018-10-02)
------------------
  * Update explorer queries for better format
  * Add latest changes to homepage
  * Fix javascript sentry error on data detail page
  [dianaboiangiu]

1.5.4 (2018-09-26)
------------------
  * Add excel export from pivot table
  * Update UserManual
  [dianaboiangiu]

1.5.3 (2018-09-24)
------------------
  * Fix reports detail 500 error.
  [dianaboiangiu]

1.5.2 (2018-09-24)
------------------
  * Fix detail page table errors
  [dianaboiangiu]

1.5.1 (2018-09-20)
------------------
  * Update User Manual with Report generation and new Edit teammates system
  * Show/hide PDF/Excel/HTML buttons accordingly
  * Move Download Excel button at the bottom of the page
  [dianaboiangiu]

1.5.0 (2018-09-13)
------------------
* Add email acceptance step for teammates.
  [dianaboiangiu]

1.4.0 (2018-09-11)
------------------
* Export Pivot table as PDF.
  [dianaboiangiu]

1.3.2 (2018-08-28)
------------------
* Fix title escape in detail pages.
  [dianaboiangiu]

1.3.1 (2018-08-22)
------------------
* Re-enable django module
  [nico4]

1.3.0 (2018-08-06)
------------------

* Add user manual (accesible in the Help section), generated automatically with Sphinx.
  [nico4]

1.2.6 - 1.2.11 - (2018-08-06)
------------------

* Fixes
* Allow regular users to download report excel

1.2.5 - (2018-08-01)
-------------------

* Disable django  module temporarily
  [dianaboiangiu]

1.2.4 - (2018-07-31)
-------------------

* Add csrf trusted origin
  [dianaboiangiu]

1.2.3 - (2018-07-31)
-------------------

* Upgrade from ElasticSearch 5.4 to 6.3
  [dianaboiangiu]

1.2.2 - (2018-07-19)
-------------------

* Fix pivot HTML download for Internet Explorer and Firefox browsers.
  [dianaboiangiu]

1.2.1 - (2018-07-18)
-------------------

* Add reports generation with excel download
* Add pivot tables with html download
  [dianaboiangiu]

1.2.0 - (2018-07-17)
--------------------

* Add uswgi
  [nico4]

1.1.8 - (2018-07-11)
-------------------

* Fix Is Network filter on Data Provider listing
* Set margin for Edit members button
* Don't show "Showing 1 to 2 of 2 entries"(table info) for less than 10 rows
* Exclude note from requirement duplicity check
* Fix links editing
  [dianaboiangiu]

1.1.7 - (2018-06-19)
------------------

* Add about page
* Add changelog
  [dianaboiangiu]

1.1.6 - (2018-06-05)
------------------

* Reindex all objects at products imports
  [dianaboiangiu]

1.1.5 - (2018-06-05)
------------------

* Fix large products import timeout
  [dianaboiangiu]

1.1.4 - (2018-05-16)
------------------

* Use safe js o title variables
  [dianaboiangiu]

1.1.3 - (2018-04-26)
------------------

* Add cancel buttons on all add forms
  [dianaboiangiu]

1.1.2 - (2018-04-24)
------------------

* Replace EmailField with CharField for Data Provider
  [catalinjitea]

1.1.1 - (2018-04-24)
------------------

* Fix url validation error for Data Provider
* Fix requirement edit validation error
  [catalinjitea]

1.1.0 - (2018-04-12)
------------------

* Add workflow for Data/Data Provider
  [dianaboiangiu]

1.0.7 - (2018-04-10)
------------------

* Fix excel corrupt file
  [dianaboiangiu]

1.0.6 - (2018-04-04)
------------------

* Add data clone
  [dianaboiangiu]

1.0.5 - (2018-03-29)
------------------

* Solve integrity error generated by imports
  [dianaboiangiu]

1.0.4 - (2018-03-29)
------------------

* Fix requirement detail exports
  [dianaboiangiu]

1.0.3 - (2018-03-26)
------------------

* Fix validation states on requirement page
  [dianaboiangiu]

1.0.2 - (2018-03-21)
------------------

* Add user teammates
  [dianaboiangiu]

1.0.1 - (2018-03-16)
-----------------------

* Fix worker timeout
  [dianaboiangiu]

1.0.0 - (2018-03-12)
------------------

* Initial release
  [dianaboiangiu]
