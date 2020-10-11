#!/bin/sh
arvados-cwl-runner --project-uuid=cborg-j7d0g-lcux1tdrdshvul7 --update-workflow=cborg-7fd4e-3ig4fl4bz90uydt metagenome/mrsa-metagenome.cwl
arvados-cwl-runner --project-uuid=cborg-j7d0g-lcux1tdrdshvul7 --update-workflow=cborg-7fd4e-qhxoc5ddgrti3tq pangenome/mrsa-pangenome.cwl
