Changelog
=========

1.2.5 (2020-03-13)
------------------
* Fix user uniqueness check
  [dianaboiangiu]

1.2.4 (2020-03-09)
------------------
* Add BCC email address to global template context
  [dianaboiangiu]

1.2.3 (2020-02-12)
------------------
* Fix PersonCompany integrity error on save on fetch_ecr
  [dianaboiangiu]

1.2.2 (2020-02-12)
------------------
* Add current user to through model person-company 
  [dianaboiangiu]

1.2.1 (2020-02-12)
------------------
* Fix inactive companies from ODS/FGAS
  [dianaboiangiu]

1.2.0 (2019-08-22)
------------------
* Grab sidemenu from bdr
  [dianaboiangiu]

1.1.32 (2019-07-09)
------------------
* Fix security issues (Django)
  [catalinjitea]

1.1.31 (2019-06-20)
------------------
* Split cars and vans groups
  [catalinjitea]

1.1.30 (2019-05-21)
------------------
* Updated entry for fetch in docker-compose
  [olimpiurob]

1.1.29 (2019-04-15)
------------------
* Allow ECR Revision companies in the application
  [dianaboiangiu]

1.1.28 (2019-04-11)
------------------
* Grab all companies in fetch
  [dianaboiangiu]

1.1.27 (2019-04-11)
------------------
* Fix ecr companies create or update
  [dianaboiangiu]

1.1.26 (2019-04-11)
------------------
* Add command for fetching both BDR and ECR companies
  [dianaboiangiu]

1.1.25 (2019-04-11)
------------------
* Fix entrypoint for fetch service
  [dianaboiangiu]

1.1.24 (2019-04-11)
------------------
* Take old commits
  [dianaboiangiu]

1.1.23 (2019-04-11)
------------------
* Set logger for commands
  [dianaboiangiu]

1.1.22 (2019-04-11)
------------------
* Fix fetch service
  [nico4]

1.1.21 (2019-04-09)
------------------
* Improve fetching
* Check companies fetched from ECR
  [dianaboiangiu]

1.1.20 (2019-04-04)
------------------
* Reuse email template
  [dianaboiangiu]

1.1.19 (2019-04-03)
------------------
* Set OTRS email headers
  [dianaboiangiu]

1.1.18 (2019-04-02)
-------------------
* Remove unique from email
  [dianaboiangiu]

1.1.17 (2019-04-02)
------------------
* Fix create person
  [dianaboiangiu]

1.1.16 (2019-03-28)
------------------
* Allow admin to delete cyclenotifications
  [dianaboiangiu]

1.1.15 (2019-03-28)
------------------
* Fix person fetch email/username
  [dianaboiangiu]

1.1.14 (2019-03-27)
------------------
* Fix fetch ecr persons
  [dianaboiangiu]

1.1.13 (2019-03-27)
------------------
* Add representative details to company
  [dianaboiangiu]

1.1.12 (2019-03-27)
------------------
* Fix details in pages
  [dianaboiangiu]

1.1.11 (2019-03-26)
------------------
* Add DEBUG to context
  [dianaboiangiu]

1.1.10 (2019-03-26)
------------------
* Fix text trigger page
  [dianaboiangiu]

1.1.9 (2019-03-26)
-----------------
* Do not send bcc in test template
  [dianaboiangiu]

1.1.8 (2019-03-26)
-----------------
* Add details on template trigger page
  [dianaboiangiu]

1.1.7 (2019-03-26)
-----------------
* Add BCC to send mail
  [dianaboiangiu]

1.1.6 (2019-03-25)
-----------------
* Remove buttons from ckeditor
  [dianaboiangiu]

1.1.5 (2019-03-25)
-----------------
* Fix companies title
  [dianaboiangiu]

1.1.4 (2019-03-25)
-----------------
* Refactor design
  [dianaboiangiu]

1.1.3 (2019-03-25)
-----------------
* Fix mail filtering for many-to-many relations
* Improve frontend
  [dianaboiangiu]

1.1.2 (2019-03-22)
-----------------
* Add mail filtering
* Fix bugs
  [dianaboiangiu]

1.1.1 (2019-02-26)
-----------------
* Optimize async
  [dianaboiangiu]

1.1.0 (2019-02-26)
------------------
* Switch from gunicorn to uwsgi
  [dianaboiangiu]

1.0.11(2019-02-26)
-----------------
* Add timeout to gunicorn
  [dianaboiangiu]

1.0.10 (2019-02-25)
-----------------
* Add params to subject
  [dianaboiangiu]

1.0.9 (2019-02-25)
-----------------
* Fix email templates editing and creation
  [dianaboiangiu]

1.0.8 (2019-02-22)
-----------------
* Rewrite alpine entrypoint commands
  [dianaboiangiu]

1.0.7 (2019-02-22)
-----------------
* Set entrypoint variables
  [dianaboiangiu]

1.0.6 (2019-02-22)
------------------
* Fix alpine sh
  [dianaboiangiu]

1.0.5 (2019-02-22)
------------------
* Fix fetching errors
* Refactor docker-compose
  [dianaboiangiu]

1.0.2 (2019-01-16)
------------------
* Upgrade gunicorn to 19.5.0
  [dianaboiangiu]

1.0.1 (2019-01-15)
------------------
* Semantic Versioning
* Upgrade Django to 1.11
  [dianaboiangiu]

1.0.dev0 - (unreleased)
-----------------------
* Initial commit
  [chiridra refs #84117]
