# Status Manager

---

## Contributors
* Johannes Schmid
* Girtler Florian

## General Description
The status of an asynchronous order changes in the course of processing it. Possible order states can be the
following:

* RECEIVED: the order has succeeded the validation and was accepted
* QUEUED: the order has been sent to the service queue
* RUNNING: the order started processing
* INVALID: there is no satellite data available for the requested date(s)
* SUCCESS: the order finished successfully
* FAILED: the order failed during processing
* ABORTED: the order was canceled manually by the user


The states are being updated by the API (RECEIVED, QUEUED and ABORTED) and by Airflow (RUNNING,
INVALID, FAILED, SUCCESS). The overall workflow is illustraded in the Figure below.

![alt text](docs/overview_order_status_updating_workflow.png)

Updating a status is done by the API gateway, which offers respective routes for Airflow to access. For
specific status updates such as “SUCCESS”, “INVALID” and “FAILED” an e-mail notification is sent to the user,
if the optional notification parameter in the service ordering payload is set to “true”. By default no email is
sent.
