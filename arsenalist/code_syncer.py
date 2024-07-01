# TODO(sdhande): Create a code syncer for Arsenalist where it is assumed that there is updated code once he sends job. The master auto picks the code dir from account info
# Maybe after job sender runs, it tars the code dir and keeps it in account data dir
# Master will sync this file then scp it to slave. We can keep another instance of fnotifier in the slave, which will reda if a tar file comes in. If it does,
# the slave can extract it and replace the code base.
# Save code with file name <job_id>.tar.gz
