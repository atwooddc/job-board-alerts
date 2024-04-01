# job-board-alerts

automate your job search with this email alert script that notifies you of postings on otherwise silent job boards

# steps

1. clone repo
2. populate email, password fields and add any desired job boards: for non-workday job boards, the name of the company, the url, and the HTML name and id BeautifulSoup uses to identify postings
3. type `crontab -e` in Terminal to add a cron job
4. type `i` to enter editing mode
5. add a line in the form of `* * * * * python3 full/path/to/job_board_alerts.py`, using a cron expression to specify how often the script runs (see https://crontab.guru/#*_*_*_*_* for more info on cron schedule expressions)
6. hit `esc`, then type `:wq` and hit `enter` to save and exit the crontab editor
