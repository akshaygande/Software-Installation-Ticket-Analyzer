from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Span
import spacy
 
def add_custom_patterns(nlp):
    matcher = Matcher(nlp.vocab)
    phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    
    install_verbs = ["install", "deploy", "configure", "setup", "initialize", 
                     "upgrade", "download", "reinstall", "uninstall", "manual", "remove"]
    install_nouns = ["installation", "deployment", "setup", "configuration", 
                     "initialization", "upgrade", "uninstallation", "reinstallation", "removal"]
    matcher.add("INSTALL_TASK", [
        [{"LEMMA": {"in": install_verbs}}],
        [{"LOWER": {"in": install_nouns}}],
        [{"TEXT": {"REGEX": r"(?i)^i?n?stal+[a-z]*"}}],
        [{"LOWER": "set"}, {"LOWER": "up"}],
        [{"LOWER": "re"}, {"LOWER": "install"}],
    ])
    matcher.add("TYPE_NOT_ABLE", [
        [{"LOWER": "not"}, {"LOWER": "able"}, {"LOWER": "to"}],
        [{"LOWER": "unable"},{"LOWER": "to"}]
    ])
    matcher.add("TYPE_ENABLE", [
        [{"LOWER": "enable"}]
    ])
    matcher.add("TYPE_HOW_TO", [
        [{"LOWER": "how"}, {"LOWER": "to"}]
    ])
    matcher.add("TYPE_NOT_GETTING_INSTALLED", [
        [{"LOWER": "not"}, {"LOWER": "getting"}, {"LOWER": "installed"}],
    ])
    matcher.add("TYPE_CONNECT", [
        [{"LEMMA": "connect"}],
    ])
    matcher.add("TYPE_ACT", [
        [{"LEMMA": {"in": install_verbs}}],
        [{"LOWER": {"in": install_nouns}}],
        [{"TEXT": {"REGEX": r"(?i)^i?n?stal+[a-z]*"}}],
        [{"LOWER": "set"}, {"LOWER": "up"}],
        [{"LOWER": "re"}, {"LOWER": "install"}],
        [{"LOWER": {"IN": ["required", "require", "requirement"]}}],
    ])
    
    matcher.add("REQUIRE_TASK", [
        [{"LOWER": {"IN": ["required", "require", "requirement"]}}],
        [{"LOWER": "not"}, {"LOWER": "getting"}, {"LOWER": "installed"}],
        [{"LOWER": "not"}, {"LOWER": "able"}, {"LOWER": "to"}, {"LOWER": "use"}],
    ])
    
    matcher.add("REQUEST_TASK", [
        [{"LOWER": "request"}]
    ])
    
    matcher.add("ACCESS_TASK", [
        [{"LOWER": "access"}]
    ])
    
    software_terms = [
        "visudo", "Stat", "SSH", "Editplus", "citrixworkspace", "matrix", "GP", "RDC","node", "google", "postgres", "pgdmin", "UBS My desk", "enterproce arichtecure", "Oracle SQL developer", "postgresql", "VM Ware horizon client", "nodejs", "node.js", "notepad++", "notepad ++", "oracle virtual box", "mvn", "postgres sql",
        "jupyter", "jupyterlab", "visual studio", "microsoft visual studio", "docker", "nginx", "redis", "mvn clean install",
        "mongodb", "apache", "eclipse", "pycharm", "intellij", "webex", "teams", 
        "citrix", "ctirix", "openjdk", "opebjdk", "maven", "tomcat", "apachetomcat", "java", "jdk", "java jdk" ,"netbeans", "git", "one drive",
        "putty", "power bi", "ssms", "sql server express", "azure", "aws", "awscliv2",
        "vscode", "vs code", "angular", "excel", "word", "outlook", "dbeaver", "pgadmin", "pyhton interpreter",
        "soapui", "postman", "Cisco Jabber", "avaya workspace", "FortiClientMiniSetup-Windows", "chrome",
        "oracle", "visio", "appium", "appium gui server", "appium inspector", "python", "prohance", "anaconda", "android studio", 
        "jabber", "adobe acrobat","MS team", "ms teams", "ms visio", "streamlit", "tableau", "win otp  authenticator",
        "checkpoint vpn", "vnc viewer", "7-zip", "snowflake", ".netcore", ".net", ".net framework", ".netframework" ,
        "msdn", "sap gui", "zscaler", "remote desktop", "amazon workspace", "dbforge", "tableau public", "sts", 
        "nvm", "node modules", "ide eclipse", "wireshark","tabular editor", "autosas", "ARCON",
        "avaya agent", "citrix workspace", "azure cli", "oracle database", "packet tracer", "winotp", "win otp", "note ++",
        "sap gui logon pad", "amazon ssm", "sf cli", "sql work bench", "Robot Framework", "global protect", "Libreoffice",
        "firefox", "safari", "edge", "sublime", "codeblocks", "winrar", "vlc", "kubernetes", "gitbash", "github","Cisco Packet Tracer",
        "autocad", "altium", "anyconnect", "anydesk", "appgate", "appstream", "arcsight", "aris", "articulate", "dot net core",
        "as400", "autosar", "amplify", "android", "ant", "antlr", "balsamiq", "bash", "bentley", "beyondtrust", "ntrust identity",
        "click", "codility", "composer", "configmgr", "copilot", "crowdstrike", "cucumber", "nvidia cuda", "curl", "cyberark",
        "cypress", "dapr", "databricks", "davinci", "dbt", "defender", "devicetrust", "draw.io", "dynatrace", "editplus",
        "erwin", "esxi","fastboot", "fiddler", "filezilla", "finacle", "flash", "forticlient", "framemaker",
        "gcloud", "genesys", "gitlab", "gns3", "gnupg", "golang", "gradle", "grafana", "grammarly", "groovy", "h2",
        "hashicorp", "hibernate", "iis", "illustrator", "idle", "informatica", "installanywhere", "intune",
        "ireport", "ivanti", "jasper", "jboss", "jenkins", "jetbrains", "jira", "jmeter", "jre", "jupyter notebook",
        "kafka", "katalon", "keepass", "keepassxc", "keycloak", "kubectl", "laravel", "linqpad", "linux", "logmein",
        "lotus notes", "mingw", "minikube", "minitab", "mremoteng", "mcafee", "meld", "metadefender", "microstation",
        "microstrategy", "milestone", "mobaxterm", "obs", "okta", "ollama", "onenote", "onvue", "openai", "openssh",
        "openssl", "opentext", "paint", "paloalto", "panda", "parsec", "pcoip", "pgagent", "php", "phpstorm", "pingid",
        "pip", "playwright", "podman", "noxplayer", "npm", "nprinting", "ns3", "numpy", "nvda", "qlikview", "qualyscloud",
        "qualyscloudagent", "questionmark", "R", "rabbitmq", "rdp", "react", "remotedesktop", "rstudio", "rhel",
        "sailpoint", "salesforce", "scala", "sccm", "selenium", "sentinelone", "servicenow", "sharepoint", "slack",
        "snagit", "softphone", "solarwinds", "spark", "spfx", "springboot", "spyder", "sqlexpress", "sqlite",
        "stackbuilder", "storyline", "superputty", "swagger", "synapse", "talend", "terraform", "testng", "tortoisegit",
        "tortoisesvn", "tosca", "treesize", "tricentis", "typescript", "unix", "vault", "vdi", "virtualbox", "vmware",
        "xampp", "xdr", "xrmtoolbox", "zulu", "chromedriver", "ciscoanyconnect", "citrixworkspaceapp", "entrust software identityguard soft token", "soap ui", "MS -Teams",
        "microsoft project professional", "winscap", "azure storage explorer", "matrix Workspace", "winscp", "sap Logon", "Mysql", "Chrome extension", "cisco-secure-client", "tableu"
    ]
    matcher.add("SOFTWARE_COMPOUND", [
        [{"LOWER": "power"}, {"LOWER": "bi"}],
        [{"LOWER": "microsoft"}, {"LOWER": "store"}],
        [{"LOWER": "visual"}, {"LOWER": "studio"}],
        [{"LOWER": "sql"}, {"LOWER": {"REGEX": "server|developer"}}],
        [{"LOWER": "sql"}, {"LOWER": "server"}, {"LOWER": "management"}, {"LOWER": "studio"}],
        [{"LOWER": "oracle"}, {"LOWER": {"REGEX": "openjdk|sql"}}],
        [{"LOWER": "oracle"}, {"LOWER": "developer"}, {"LOWER": "suite"}],
        [{"LOWER": "open"}, {"LOWER": "jdk"}],
        [{"LOWER": "node"}, {"LOWER": "js"}],
        [{"LOWER": "mongo"}, {"LOWER": "db"}],
        [{"LOWER": "microsoft"}, {"LOWER": {"REGEX": "teams|word|excel|outlook|visio"}}],
        [{"LOWER": "mysql"}, {"LOWER": {"REGEX": "workbench"}}],
        [{"LOWER": "remote"}, {"LOWER": "desktop"}],
        [{"LOWER": "checkpoint"}, {"LOWER": "endpoint"}],
        [{"LOWER": "pydev"}, {"LOWER": "for"}, {"LOWER": "eclipse"}],
        [{"LOWER": "citrix"}, {"LOWER": "work"}, {"LOWER": "space"}],
        [{"LOWER": "cisco"}, {"LOWER": "packet"}, {"LOWER": "tracker"}],
        [{"LOWER": "cisco"}, {"LOWER": "secure"}, {"LOWER": "client"}],
        [{"LOWER": "cisco"}, {"LOWER": "anyconnect"}, {"LOWER": "secure"}, {"LOWER": "mobility"}],
        [{"LOWER": "sap"}, {"LOWER": "hana"}, {"LOWER": "studio"}],
        [{"LOWER": "amazon"}, {"LOWER": "workspaces"}],
        [{"LOWER": {"REGEX": r"^(?:vdi|cvw|alt|pam|aws|azure)$"}}]
    ])
    software_patterns = [nlp.make_doc(term) for term in software_terms]
    phrase_matcher.add("SOFTWARE_NAMES", software_patterns)
    
    
    matcher.add("SOFTWARE_WITH_VERSION", [
        [{"TEXT": {"REGEX": r"^(?P<sw>[A-Za-z\.]+)(?P<ver>\d+(?:\.\d+)*)$"}}]
    ])
    
    matcher.add("VERSION_NUMBERS", [
        [{"LOWER": "latest"}],
        [{"TEXT": {"REGEX": r"^(?:v?\.?)?\d+(?:\.\d+)*[a-z]?(?:_x000d)?$"}}],
        [{"TEXT": {"REGEX": r"\b(?:19|20)\d{2}\b"}}],
        [{"TEXT": {"REGEX": r"\b\d+\.\d+(?:\.\d+)?(?:-[\w\d]+)?\b"}}],
        [{"TEXT": {"REGEX": r"(?<=\D)(\d+\.\d+\.\d+|\d+\.\d+)(?=\b)"}}]
    ])
    
    file_extensions = r"exe|msi|dmg|pkg|zip|tar|gz|bz2|rar|7z|deb|rpm|jar|war|apk|sh|bat|ps1|cmd"
    matcher.add("PACKAGE_NAMES", [
        [{"TEXT": {"REGEX": fr"^(?:[A-Za-z0-9][\w-]*?[-_]?(?:setup|install|client|server|win|x64|x86|v?\d+[\w.-]*?)\.(?:{file_extensions}))(?:_x000d)?$"}}],
        [{"TEXT": {"REGEX": r"^[A-Za-z0-9][\w-]*?\.tar\.(?:gz|bz2)(?:_x000d)?$"}}],
        [{"TEXT": {"REGEX": r"(?i)^.*(?:setup|installer|client|agent).*\.(?:exe|msi)$"}}],
        [{"TEXT": {"REGEX": r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+-\d+\.\d+"}}],
        [{"TEXT": {"REGEX": r"^(?:SessionManagerPlugin|AmazonSSMAgent|AWSCLIV2)"}}]
    ])
    
    matcher.add("PACKAGE_WITH_VERSION", [
        [{"TEXT": {"REGEX": r"^(?P<pkg>[A-Za-z0-9]+Setup)-(?:[A-Za-z0-9\-]+-)?(?P<ver>[A-Za-z0-9\-\.]+)$"}}]
    ])
    
    target_terms = [
        "machine", "laptop", "desktop", "server", "cloud", "container", "asset",
        "vm", "host", "vdi", "system", "workspace", "environment", "device", 
        "platform", "terminal", "instance", "local system", "virtual machine",
        "virtual box", "windows server", "ubuntu vm", "network", "infrastructure",
        "client machine", "my system", "my laptop", "local machine", "virtual environment",
        "cloud instance", "development environment", "production server", "windows book"
    ]
    matcher.add("TARGETS", [
        [{"LOWER": {"in": target_terms}}],
        [{"TEXT": {"REGEX": r"(?i)\b(?:vm|vdi|alt|pam)\b"}}],
        [{"LOWER": {"REGEX": r"^(?:virtual|cloud|local)"}}],
        [{"LOWER": "host"}, {"LOWER": "name"}],
        [{"LOWER": "windows"}, {"LOWER": "book"}],
        [{"LOWER": "virtual"}, {"LOWER": "workspace"}]
    ])
    
    matcher.add("JUSTIFICATIONS", [
        [{"LOWER": "to"}, {"LOWER": "work"}, {"LOWER": "on"}, {"LOWER": "spring"}, {"LOWER": "tool"}, {"LOWER": "suite"}],
        [{"LOWER": "for"}, {"LOWER": {"REGEX": "business|work|project|development|learning|learn|testing|production|oca"}}, {"LOWER": {"REGEX": "purposes|needs|requirements|learning|work|devops|project|olympus"}}, {"IS_PUNCT": True, "OP": "?"}],
        [{"LOWER": "to"}, {"LOWER": {"REGEX": "learn|complete|practice|develop|use|work"}}, {"LOWER": "on", "OP": "?"}],
        [{"LOWER": "for"}, {"LOWER": {"REGEX": "project|learning|development|work|testing|production"}}],
        [{"LOWER": "to"}, {"LOWER": "learn"}, {"LOWER": "and"}, {"LOWER": "practice"}],
        [{"LOWER": "complete"}, {"LOWER": "assignments"}],
        [{"LOWER": "admin"}, {"LOWER": "creds"}],
        [{"LOWER": "business"}, {"LOWER": "purposes"}],
        [{"LOWER": "client"}, {"LOWER": {"REGEX": r"request(ed)?"}}],
        [{"LOWER": "to"}, {"LOWER": "complete"}, {"LOWER": "mandatory"}, {"LOWER": "training"}],
        [{"LOWER": "for"}, {"LOWER": "python"}, {"LOWER": "training"}],
        [{"LOWER": "for"}, {"LOWER": "my"}, {"LOWER": "hands"}, {"LOWER": "on"}],
        [{"LOWER": "for"}, {"LOWER": "bau"}, {"LOWER": "activity"}],
        [{"LOWER": "for"}, {"LOWER": "project"}, {"LOWER": "to"}, {"LOWER": "analyse"}, {"LOWER": "complex"}, {"LOWER": "data"}],
    ])
    
    # LICENSES Patterns
    license_types = ["enterprise", "standard", "evaluation", "open source", "professional", "community", "commercial", "free"]
    matcher.add("LICENSES", [
        [{"LOWER": {"in": license_types}}]
    ])
    
    return matcher, phrase_matcher
