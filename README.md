\# TAM Frontier-State Governance Harness



A reproducible governance and verification harness for evaluating frontier-state emissions from an autonomous-racing software surface.



This repository packages a technical evidence run over a public TAM-related autonomous-racing software surface and produces sealed, inspectable artifacts for intake, landing, computation, solver output, physics output, QPE evidence, and final run certification.



\## Target Surface



\- Public repository: `TUMFTM/TAM\_\_common`

\- Source: https://github.com/TUMFTM/TAM\_\_common



\## Purpose



The purpose of this repository is to demonstrate that a motorsports software surface can be processed through a governed verification pipeline and converted into structured frontier-state evidence.



The harness is designed to support technical review by exposing:



\- deterministic intake records

\- landed run evidence

\- solver emissions

\- physics emissions

\- QPE tool evidence

\- state, field, energy, torque, and residual measurements

\- predicate closure checks

\- deterministic receipts

\- master seal artifacts

\- emitted output ledgers



This is not a simple file-count or repository-summary report. It is an evidence package showing how an autonomous-racing software surface can be transformed into a sealed, inspectable governance-state run.



\## Repository Scope



The current repository includes:



```text

frontier\_harness.py

run\_intake.py

tam\_common\_manifest.json

tam\_common\_garden\_landed.json

frontier\_emitted\_outputs.json

frontier\_operator\_receipt.json

frontier\_qpe\_receipt.json

frontier\_master\_seal.txt

