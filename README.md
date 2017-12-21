# FOIA The Dead

FOIA The Dead is a "morbid transparency project" that creates automated public records requests for the subjects of newly published obituaries. Because the Freedom of Information Act limits access to certain private information about living people, the project occasionally uncovers records that would have previously been withheld.

This repository contains the script that fetches obituaries (currently only from the *New York Times*) and creates a record request based on the information those obituaries contain. The resulting requests were previously sent via email to the FBI, but now are delivered via the [Muckrock](https://www.muckrock.com) API.

This repository also contains the scripts that publish the project's results at [foiathedead.org](https://foiathedead.org). Those HTML pages are generated with Python, based on information stored in a SQLite database that tracks the project's requests through publication.

FOIA The Dead is a Special Project of the [Freedom of the Press Foundation](https://freedom.press), and written and maintained by [Parker Higgins](https://twitter.com/xor).
