Introduction
============

This User Guide proposes to describe the way the application should be used and all the functionalities that are available
within the application.

.. figure:: screenshots/home.png
    :width: 600px
    :align: center
    :target: _images/home.png

    *Figure 1. Main application page*

The first page, available at https://cis2.eea.europa.eu/, is the HomePage presented in *Figure 1*. The navigation menu is
available on the top of the page and it can be used to navigate to the listing pages of Products, Requirements, Data,
Data Providers, to make changes to the user’s account or to consult an online help page.

Database objects
================
The application holds the following main objects: Products, Requirements, Data, Data Provider. Those objects can have
multiple relations between one another. Besides those objects, there are many picklists tables which hold various values
to be used when defining an object.

----------
 Products
----------

..  figure:: screenshots/products.png
    :width: 600px
    :align: center
    :target: _images/products.png

    *Figure 2. Products listing page*

Listing products
----------------
Products listing page can be accessed from the link in the navigation bar. The listing can be filtered using the dropdown
options or by searching the products by their names. The filtered table can be exported then as a PDF or Excel document.

Creating new products
---------------------
A new product can be created by clicking the button “New product” from the listing page. The form must be completed
respecting the validation constraints.
A product can be added only by an **user with administration rights**.

..  figure:: screenshots/product_details.png
    :width: 600px
    :align: center
    :target: _images/product_details.png

    *Figure 3. A product’s detail page*

Detail page of a product
------------------------
A product’s detail page can be accessed by clicking on the product’s name in the listing table. All information concerning
the product is displayed on this page. The table at the bottom of the page presents the requirements that product has a
relation with. By clicking on the requirement name, the requirement detail page can be seen. This table can be filtered
by searching the requirement’s name. It can also be exported as either PDF or Excel document.


Updating an existing product
----------------------------
A product can be edited by clicking on the “Edit Product” button from a product’s detail page. The form must again respect all validation constraints.
A product can be updated only by an **user with administration rights**.

Deleting a product
------------------
A product can be deleted by clicking on the “Delete Product” button from a product’s detail page. Another button must be clicked then to accept this change.
A product can be deleted only by an user with administration rights.

-----------
Requirement
-----------

..  figure:: screenshots/requirements.png
    :width: 600px
    :align: center
    :target: _images/requirements.png

    *Figure 4. Requirements listing page*

Listing requirements
--------------------
Requirements listing page can be accessed from the link in the navigation bar. The listing can be filtered using the
dropdown options or by searching the requirements by their names. The filtered table can be exported then as a PDF or
Excel document.
For metrics columns a legend explaining the values meaning can be accessed by hovering over the information button.

Creating new requirements
-------------------------
A new requirement can be created by clicking the button “New requirement” from the listing page. The form must be
completed respecting the validation constraints.
For requirement, a special validation is implemented. There must be no duplicated requirement. This means that in order
to create a new requirement, it must have at least one field(except for its name) which is different from another
requirement already in the database.

Cloning a requirement
---------------------
The clone option can be used if a new requirement to be created is very similar to one existing already in the application.
The cloning form can be accessed by going to the detail page of the similar requirement and clicking on the Clone button.
The form will be completed with data from the similar requirement. However, in order to save the new requirement, at
least one field must be changed (except the name field).

Detail page of a requirement
----------------------------
A requirement’ s detail page can be accessed by clicking on the requirement’s name in the listing table.
All information concerning the requirement is displayed on this page. The metrics information is explained when hovering
over the values.
There are two tables at the bottom of the page. Both tables can be filtered by name and then exported as PDF or as Excel.

**The first table concerns the relation with products**. All products with which the requirement has a relation with are
listed in this table.

..  figure:: screenshots/product_requirements.png
    :width: 600px
    :align: center
    :target: _images/product_requirements.png

    *Figure 5. Requirement Products relation table*

Those relations must be unique, so between Product A and Requirement B there can be only a relation. There is an exception
to this rule in case the Relevance parameter is different.
There are two ways to  add a new relation to products.
First method is to click on the  “Add requirement to product” button and then complete a form in which you select the product
you want to use in that relation.
The second method is to click on the “Add requirement to product group” button. In the form a product group can be selected.
After form submission, relations will be created between the requirement and all the products that are in that product group.
A relation will be created only if a relation does not exist between that product and that requirement, following the Relevance
rule presented above.  The relations can also be edited or deleted using the buttons attached to each row in the table.

**The second table concerns the relation with data**. All data with which the requirement has a relation with is listed in
this table.

..  figure:: screenshots/data_requirement.png
    :width: 600px
    :align: center
    :target: _images/data_requirement.png

    *Figure 6. Requirement Data relation table*

Similar to the products, new relations between the requirement and data can be created. There must be a unique relation
between a requirement and a data. The relation can be edited or deleted using the buttons from the table.

Updating an existing requirement
--------------------------------
A requirement can be edited by clicking on the “Edit Requirement” button from a requirement’ s detail page. The form must
again respect all validation constraints, including the uniqueness of the requirements discussed in the Creating new
requirements section.

Deleting a requirement
----------------------
A requirement can be deleted by clicking on the “Delete Requirement” button from a requirement’ s detail page. Another
button must be clicked then to accept this change.


----
Data
----

..  figure:: screenshots/data.png
    :width: 600px
    :align: center
    :target: _images/data.png

    *Figure 7. Data Provider listing page*

Listing data
------------
Data listing page can be accessed from the link in the navigation bar. The listing can be filtered using the dropdown
options or by searching data by its name. The filtered table can be exported then as a PDF or Excel document.

..  figure:: screenshots/add_data.png
    :width: 600px
    :align: center
    :target: _images/add_data.png

    *Figure 8. Datalisting page*

Creating new data
-----------------
A new data can be created by clicking the button “New data” from the listing page.
The form which is initially accessed has no validation. This was decided in order to allow partial data to be created in
the application. However, if the user is sure about the data that he wants to introduce, he should use the form provided
in Figure 7.
There is a special validation rule for this form: at least an inspire theme or an essential variable.

Cloning a data
--------------
The clone option can be used if the new data is very similar to one existing already in the application. The cloning form
can be accessed by going to the detail page of the similar data and clicking on the Clone button. The form will be completed
with data from the similar data.

..  figure:: screenshots/data_details.png
    :width: 600px
    :align: center
    :target: _images/data_details.png

    *Figure 9. Data detail page*

Detail page of data
A data’ s detail page can be accessed by clicking on the data’s name in the listing table.
All information concerning the data is displayed on this page.
If that data is just partially completed, a warning message will be displayed on the top of the page with a link to the
editing page with full validation(Figure 9).

..  figure:: screenshots/data_dataprovider.png
    :width: 600px
    :align: center
    :target: _images/data_dataprovider.png

    *Figure 10. Data detail page relations*

There are two tables at the bottom of the page. Both tables can be filtered by name and then exported as PDF or as Excel.

**The first table concerns the relation with data provider**. All data providers with which the data has a relation with
are listed in this table.
Those relations must be unique, so between Data A and DataProvider B there can be only one relation. By clicking on the
button “Add data to data provider” and completing the form a new relation is added. The relation can be edited or deleted
using the buttons from the table.

**The second table concerns the relation with requirement**. All requirements with which the data has a relation with is
listed in this table. New relations can be created from requirement’ s page.

Updating an existing data
-------------------------
A data can be edited by clicking on the “Edit Data” button from a data’ s detail page. Similar to the creation of new data,
there are two forms: one with validation and one without.

Deleting data
-------------
Data can be deleted by clicking on the “Delete Requirement” button from a requirement’ s detail page. Another button must
be clicked then to accept this change.

-------------
Data provider
-------------

..  figure:: screenshots/data_providers.png
    :width: 600px
    :align: center
    :target: _images/data_providers.png

    *Figure 11. Data provider listing*

**There are two types of data providers: data provider network and data provider. The data provider network can have other**
**data providers or data provider networks as its members. This structure is defined as so to maintain a hierarchy between**
**data providers.**

Listing data provider
---------------------
Data provider listing page can be accessed from the link in the navigation bar. The listing can be filtered using the
dropdown options or by searching data by its name. The filtered table can be exported then as a PDF or Excel document.

Creating a new data provider
----------------------------
A new data provider can be created by clicking the button “New data provider” from the listing page.
A new data provider network can be created by clicking the button “New data provider network” from the listing page.

Detail page of data provider
----------------------------
A data provider’s detail page can be accessed by clicking on the data provider’s name in the listing table.

All information concerning the data provider is displayed on this page.
There is a tables at the bottom of the page.It can be filtered by name and then exported as PDF or as Excel.
**The table concerns the relation with data**. All data with which the data provider has a relation with is listed in
this table.

Updating an existing data provider
----------------------------------
A data provider can be edited by clicking on the “Edit Data Provider” button from a data provider’ s detail page.
Different forms are used for data provider/data provider network.

Edit network members
--------------------
A data provider network can have members. Its members can be edited by clicking on the “Edit network members”. A network
can’t be its own member.

Deleting data provider
----------------------
A data provider can be deleted by clicking on the “Delete Data provider” button from a data provider’ s detail page.
Another button must be clicked then to accept this change.


Users
=====
There are two types of users in the application: the administrator and the usual user.
The usual user is restricted from accessing the administration section, the management section and create, update or delete
any products.
The users have permission to edit or delete an object if they are the owner of it. Being the owner of an object means that
the object was created by that specific user.

..  figure:: screenshots/teammates.png
    :width: 600px
    :align: center
    :target: _images/teammates.png

    *Figure 12. Teammates editing form*

----------
User Teams
----------

A user can add other users to its team. Adding a user to one’s team gives that user permission to edit or delete all
objects created by that user. Once a user A adds another user B to his team, the user B will also have user A in their team.
A user can edit their teammates by accessing the edit teammates form from the navigation menu. (*Figure 12*)


Validation workflow
===================

Requirement, Data and Data Provider are all passing through a validation workflow.

..  figure:: screenshots/workflow.png
    :width: 600px
    :align: center
    :target: _images/workflow.png

    *Figure 13. Workflow for Requirement, Data, Data Provider*

------
States
------
**Draft**

This is the state that the object has on its creation. In this state the object and its relations are editable. The owner
or one of their teammates can mark as ready the object.

**Ready for validation**

In this state the object and its relations cannot be edited. A user different from the owner or their teammates can either
mark as valid the object and end the workflow or request changes if that user considers that there is missing information.

**Changes requested**

In this state the object and its relations cannot be edited. The owner or one of their teammates can get the object back
to the draft state.

**Valid**

In this state the object and its relations cannot be edited. The workflow has ended and the object cannot be modified anymore.

----------------------
Requirement validation
----------------------
A requirement will go through the workflow together with its relations. Its relations the links to products and the links
to data. The relations will always be in the same state as the requirement.

---------------
Data validation
---------------
Data will go through the workflow together with its relations. Its relations the links to data providers. The relations
will always be in the same state as the data.

------------------------
Data provider validation
------------------------
A requirement will go through the workflow together with its relations. Its relations the links to products and the links
to data. The relations will always be in the same state as the requirement.


Administration
==============

Requirement, Data and Data Provider are all passing through a validation workflow.

..  figure:: screenshots/admin.png
    :width: 600px
    :align: center
    :target: _images/admin.png

    *Figure 14. Teammates editing form*

The administration panel can be accessed only by a user who has administration rights. Here, all objects, relations and
picklists values can be modified without countraints.


Help page
=========

The help page describes each value in the dropdowns used to fill the objects.
The help page can be accessed from the navigation menu by clicking “Help”. In the forms, the dropdown fields have
attached a question mark. By clicking on that question mark you will access the help page.

..  figure:: screenshots/barrier.png
    :width: 600px
    :align: center
    :target: _images/barrier.png

    *Figure 15. An example table from help page*

For Example, in *Figure 15* is one of the tables available on the Help page. Under the table title there is a small
description of that field’ s purpose. In the table there is the name of each value and the description of what that value
represents.


Management
==========

..  figure:: screenshots/manage.png
    :width: 600px
    :align: center
    :target: _images/manage.png

    *Figure 16.  Management section*

The management section is accessible only to an user with administration rights. This section can be used to export all
picklists or all products as an excel document. In order to import picklists or products, the user must first export
them, edit the exported spreadsheet and then import it.


Logging actions
===============

All actions done by users are logged in a log file. Viewing, editing, adding or deleting any object from the application
will be stored. The log gives informations about the user, the action the user made and the object that was accessed.


Soft deletion
=============

The objects and relations are never deleted. They are instead marked as “deleted”. The objects can be permanently deleted
only by accessing the database directly.












