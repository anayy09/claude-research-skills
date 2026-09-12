# Code and data availability statements

The statement is a promise a reviewer or reader will act on. It says what
exists, where, under what terms, and what a reader has to do. It does not
say why the authors are confident, and it does not apologise.

## The shape

Code: repository URL, archive DOI (concept), license, and the one line that
says what the code regenerates.

Data: for each dataset, the name, the source, the access route, and the
agreement. Derived files the authors own (cohort ids, features, predictions)
are either in the archive or described by what regenerates them.

## Restricted data

MIMIC-IV, PhysioNet resources, eICU, and any dataset with protected health
information cannot be redistributed. The statement names the resource, its
DOI or version, the credentialing route (the PhysioNet credentialed health
data use agreement and the required training), and says that the archive
contains the code that derives every cohort and feature from the source so
that a credentialed user reproduces the study. It does not contain row-level
data, ids, or anything that identifies a record.

## "Available on reasonable request"

Springer Nature's guidance permits it; its worked examples pair the
restriction with a stated reason, usually sensitivity or a third party's
agreement. A statement that restricts without a reason draws an editorial
query. When there is no sensitivity reason, the honest alternatives are a
results-only release (committed result files, figure and table scripts, the
run log, without the simulator or pipeline) or a full release. If the
authors' reason is that the analysis code is unreleased, say that the
analysis repository is not released and give the results-only archive; do
not invent a sensitivity reason.

## By venue family

**Nature Portfolio and Scientific Reports.** Separate "Data availability"
and "Code availability" statements, mandatory, after the Methods. Code
statement names the repository and the archive DOI. Data statement covers
every dataset, including public benchmarks with their DOI or URL.

**Elsevier.** A "Data availability" statement is selected on the portal from
fixed options and expanded in the manuscript; code is usually described in
the same statement or in a "Code availability" paragraph before the
references. The declaration of competing interests and CRediT roles are
separate sections and come from `AUTHORS.yaml`.

**IEEE.** No mandated section; a footnote or a sentence at the end of the
introduction or in the experimental setup naming the repository and DOI is
the convention. Code Ocean capsules are accepted for some transactions.

**BMC and Springer journals with a Declarations section.** "Availability of
data and materials" under Declarations, with ethics, consent, competing
interests, funding, and author contributions; all from `AUTHORS.yaml`.

**PLOS.** A data availability statement covering all data underlying the
findings, with the repository DOI; "on request" is not accepted without a
named data access committee.

## Wording that holds

> The code that builds every cohort, feature, model, table, and figure in
> this article is available at https://github.com/ORG/REPO and archived at
> https://doi.org/10.5281/zenodo.NNNNNNN under the MIT license. Running
> `python make.py all` regenerates Tables 2 to 5 and Figures 2 to 4 from the
> result files included in the archive.

> MIMIC-IV v3.1 and the MDS-ED benchmark are available from PhysioNet to
> credentialed users under the PhysioNet Credentialed Health Data Use
> Agreement, which does not permit redistribution of row-level data. The
> archive contains the code that derives the study cohort and every feature
> from those sources, so a credentialed user reproduces the study from the
> published files. No individual record, prediction, or stratum assignment is
> released.

Wording that does not hold: "available upon publication" (say where), "will
be made available" (do it), "available from the authors" without a reason,
and any DOI placeholder.
