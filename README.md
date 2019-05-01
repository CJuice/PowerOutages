# MD Power Outages
This is a procedural script coordinating multiple imported classes to process power providers outage data for MEMA use.

The main() function contains all of the functionality. Imports include multiple custom modules that begin with
'doit_' to identify them as custom and not widely available python libraries. Main is generally organized into the
following order of sections: imports, variable definition/creation, web requests for various provider related data,
processing of response data, output of feed status to json file, and database transactions for 'realtime' and 'archive'
and customer data.
Main relies on the following imported modules containing classes: ArchiveClasses, CustomerClass,
CTKClasses, DatabaseFunctionality, DELClasses, EUCClasses, FESClasses, PEPClasses, SMEClasses,
and UtilityClass. It also relies on a CentralizedVariables python file, and access through a parser
to a Credentials config file and a ProvidersURI config file.
The process is designed with an object-oriented focus. For power providers, there is a top level parent class called
Provider. All providers are then subclassed from this parent to create child classes. The child classes contain
unique behavior specific to a provider. Functionality/behavior common to all providers has been placed into the parent
class and inherited downward into the children. For PEP and DEL, Provider is inherited by the PEPDEL_ParentClass. This
class organizes behavior common to both PEP and DEL providers. Both PEP and DEL children inherit from
PEPDEL_ParentClass, which inherits from Provider. Where necessary, some methods in parent classes have been overridden
by methods in child classes.
A Utility class is used by all modules and serves as a static resource for common/shared helper functions and a few
simple variables. The Centralized Variables module contains variables, no classes or functions, and environment related
variables and sql statements. It is not intended to be used by Utility class.
A Web Related Functionality class exists for web related functionality and is accessed by the Provider exclusively.
The output json file named PowerOutageFeeds_StatusJSON.json is stored in a folder named JSON_Outputs.
