# Authorization API

---

## General Description
User authentication, authorization and management are based on the OAuth2 framework. It is used to
exchange data between client and server through authorization. The OAuth 2.0 authorization framework
enables a third-party application to obtain limited access to an HTTP service, either on behalf of a resource
owner by orchestrating an approval interaction between the resource owner and the HTTP service, or by
allowing the third-party application to obtain access on its own behalf. The Authorization Server provides
several endpoints for authorization, issuing tokens, refreshing tokens and revoking tokens. When the
resource owner (user)authenticates, this server issues an access token to the client. The resource owner is
the user who is using a service. A resource owner can log in to a website with a username/email and
password, or by other methods. A client is an application making protected resource requests on behalf of
the resource owner and with its authorization. Any application that uses OAuth 2.0 to access CLC backbone
API must have authorization credentials that identify the application to the OAuth 2.0 server. Therefore, the
authorization server comes with a PostgreSQL database for managing users, clients, access permissions and
access tokens. The API of the authorization server provides a set of endpoints which are required to perform
common authorization operations and flows. Scopes define which services a user has access to.

---

## What it offers

* Authorisation and authentication
* Token generation
* Creating OAuth clients
* User login
* Access token generation
* Token validation
* Scopes creation and management
