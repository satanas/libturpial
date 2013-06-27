.. _api:

API
===

.. module:: libturpial

The API_ module contains the modules and classes that will be used for any developer that want
to create an application or script based on libturpial. We can call it the *public interface*.
Here you can find the Core_, all the models_ that represent libturpial entities and the Managers_


Core
----

.. autoclass:: libturpial.api.core.Core
    :members:
    :member-order: bysource


Models
------

Here you can find the representation of the information used by libturpial_ mapped to Python objects.
They handle the methods and properties of each entity and guarantee the data consistency.

Account
+++++++

.. autoclass:: libturpial.api.models.account.Account
    :members:
    :member-order: bysource

Column
++++++

.. autoclass:: libturpial.api.models.column.Column
    :members:
    :member-order: bysource

List
++++

.. autoclass:: libturpial.api.models.list.List
    :members:
    :member-order: bysource

Status
++++++

.. autoclass:: libturpial.api.models.status.Status
    :members:
    :member-order: bysource

Profile
+++++++

.. autoclass:: libturpial.api.models.profile.Profile
    :members:
    :member-order: bysource

Entity
++++++

.. autoclass:: libturpial.api.models.entity.Entity
    :members:
    :member-order: bysource

Client
++++++

.. autoclass:: libturpial.api.models.client.Client
    :members:
    :member-order: bysource

Media
+++++

.. autoclass:: libturpial.api.models.media.Media
    :members:
    :member-order: bysource

Proxy
+++++

.. autoclass:: libturpial.api.models.proxy.Proxy
    :members:
    :member-order: bysource





Managers
--------

Account Manager
+++++++++++++++

.. autoclass:: libturpial.api.managers.accountmanager.AccountManager
	:members:
	:undoc-members:
	:special-members:

Column Manager
++++++++++++++

.. autoclass:: libturpial.api.managers.columnmanager.ColumnManager
	:members:
	:undoc-members:
	:special-members:

