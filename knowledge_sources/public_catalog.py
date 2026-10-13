"""Public security knowledge sources with provenance and licensing review requirements.

Catalog entries are not claims that content was downloaded, reviewed, or learned.
"""
SOURCES = [
    {"id":"cwe","url":"https://cwe.mitre.org/data/downloads.html","domain":"general","format":"taxonomy","status":"cataloged"},
    {"id":"nvd","url":"https://nvd.nist.gov/developers/vulnerabilities","domain":"general","format":"CVE API","status":"cataloged"},
    {"id":"osv","url":"https://osv.dev/docs/","domain":"open-source","format":"OSV API","status":"cataloged"},
    {"id":"owasp-smart-contract","url":"https://scs.owasp.org/","domain":"web3","format":"taxonomy","status":"cataloged"},
    {"id":"smartbugs-curated","url":"https://github.com/smartbugs/smartbugs-curated","domain":"solidity","format":"labeled samples","status":"cataloged"},
    {"id":"solodit","url":"https://solodit.cyfrin.io/","domain":"web3","format":"audit findings","status":"cataloged"},
    {"id":"code4rena","url":"https://code4rena.com/reports","domain":"web3","format":"public audits","status":"cataloged"},
    {"id":"sherlock","url":"https://audits.sherlock.xyz/contests","domain":"web3","format":"public audits","status":"cataloged"},
    {"id":"immunefi","url":"https://immunefi.com/bug-bounty/","domain":"web3","format":"public disclosures where available","status":"cataloged"},
    {"id":"rekt","url":"https://rekt.news/","domain":"web3","format":"incident postmortems","status":"cataloged"},
]
