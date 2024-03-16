# job-board-alerts
automate your job search with this email alert script that notifies you of postings on otherwise silent job boards

# steps
1. clone repo
2. populate email, password, fpath,...,subject fields and save
3. type `crontab -e` in Terminal to add a cron job
4. type `i` to enter editing mode
5. add a line in the form of `* * * * * python3 full/path/to/job-board-alert.py`, replacing * with numbers to specify how often the script runs (see https://crontab.guru/#*_*_*_*_* for more info on cron schedule expressions)
6. hit `esc`, then type `:wq` and hit `enter` to save and exit the crontab editor
